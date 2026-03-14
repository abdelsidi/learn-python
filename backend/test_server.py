"""
Standalone test server using SQLite — no PostgreSQL required.
Run: python test_server.py
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from datetime import datetime
import bcrypt
import subprocess
import sys
import tempfile
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "test-jwt-secret"
app.config["SECRET_KEY"] = "test-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, origins=["http://localhost:3000"])


# ── Models ──────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    progress = db.relationship("Progress", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "completed_exercises": [p.exercise_id for p in self.progress if p.completed],
        }


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    exercises = db.relationship("Exercise", backref="lesson", lazy=True, order_by="Exercise.order")

    def to_dict(self, include_exercises=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "order": self.order,
            "exercise_count": len(self.exercises),
        }
        if include_exercises:
            data["exercises"] = [e.to_dict() for e in self.exercises]
        return data


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starter_code = db.Column(db.Text, default="")
    expected_output = db.Column(db.Text)
    hint = db.Column(db.Text)
    video_url = db.Column(db.String(500))  # Micro-video for this exercise
    order = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "title": self.title,
            "description": self.description,
            "starter_code": self.starter_code,
            "hint": self.hint,
            "order": self.order,
        }


class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    last_code = db.Column(db.Text)
    completed_at = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint("user_id", "exercise_id"),)

class Streak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.DateTime)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    badge_id = db.Column(db.String(50), nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    badge_icon = db.Column(db.String(10))
    description = db.Column(db.String(255))
    unlocked_at = db.Column(db.DateTime, default=datetime.now)
    __table_args__ = (db.UniqueConstraint("user_id", "badge_id"),)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default="beginner")  # beginner, intermediate, advanced
    order = db.Column(db.Integer)
    real_world_context = db.Column(db.Text)  # Why this matters in real world
    exercises = db.relationship("ProjectExercise", backref="project", lazy=True)

    def to_dict(self, include_exercises=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "order": self.order,
            "real_world_context": self.real_world_context,
            "exercise_count": len(self.exercises),
        }
        if include_exercises:
            data["exercises"] = [e.to_dict() for e in self.exercises]
        return data

class ProjectExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starter_code = db.Column(db.Text, default="")
    expected_output = db.Column(db.Text)
    hint = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "project_id": self.project_id,
            "title": self.title,
            "description": self.description,
            "starter_code": self.starter_code,
            "hint": self.hint,
            "order": self.order,
        }

class ProjectProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_exercise_id = db.Column(db.Integer, db.ForeignKey("project_exercise.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint("user_id", "project_exercise_id"),)

# ── Achievements Definition ───────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"badge_id": "first_exercise", "name": "First Step", "icon": "🎯", "description": "Complete your first exercise"},
    {"badge_id": "10_exercises", "name": "Getting Started", "icon": "🚀", "description": "Complete 10 exercises"},
    {"badge_id": "50_exercises", "name": "On Fire", "icon": "🔥", "description": "Complete 50 exercises"},
    {"badge_id": "100_exercises", "name": "Century", "icon": "💯", "description": "Complete 100 exercises"},
    {"badge_id": "first_lesson", "name": "Lesson Master", "icon": "📚", "description": "Complete an entire lesson"},
    {"badge_id": "all_lessons", "name": "Python Expert", "icon": "🏆", "description": "Complete all lessons"},
    {"badge_id": "7_day_streak", "name": "Week Warrior", "icon": "⚡", "description": "7-day learning streak"},
    {"badge_id": "30_day_streak", "name": "Consistency King", "icon": "👑", "description": "30-day learning streak"},
    {"badge_id": "first_project", "name": "Project Pioneer", "icon": "🛠️", "description": "Complete your first project"},
]

# ── Real-World Projects ────────────────────────────────────────────────────────
PROJECTS = [
    {
        "title": "Web Scraper: News Headlines",
        "difficulty": "beginner",
        "order": 1,
        "real_world_context": "Learn how to scrape websites and extract data automatically. News aggregators, price monitoring, and research tools use this technique.",
        "description": "Build a tool that scrapes news headlines from a website and displays them.",
        "exercises": [
            {"order": 1, "title": "Fetch Web Page", "description": "Use requests library to fetch HTML from a news website.", "starter_code": "import requests\n# Fetch HTML\n", "expected_output": "200", "hint": "resp = requests.get(url)\nprint(resp.status_code)"},
            {"order": 2, "title": "Parse HTML", "description": "Use BeautifulSoup to parse the HTML and find article titles.", "starter_code": "from bs4 import BeautifulSoup\n# Parse and find titles\n", "expected_output": "Found 5 articles", "hint": "Find all article elements"},
            {"order": 3, "title": "Extract Data", "description": "Extract titles and links from articles.", "starter_code": "# Extract article data\n", "expected_output": "['Title 1', 'Title 2', ...]", "hint": "Create list of titles"},
            {"order": 4, "title": "Format Output", "description": "Format the data nicely as a table or JSON.", "starter_code": "# Format output\n", "expected_output": "JSON formatted articles", "hint": "Use json module"},
        ],
    },
    {
        "title": "Data Analysis: COVID-19 Stats",
        "difficulty": "beginner",
        "order": 2,
        "real_world_context": "Data scientists analyze health, finance, and social data daily. Learn real data analysis with Pandas and NumPy.",
        "description": "Analyze COVID-19 data: calculate trends, find peaks, and create insights.",
        "exercises": [
            {"order": 1, "title": "Load Data", "description": "Load CSV with Pandas and explore structure.", "starter_code": "import pandas as pd\n# Load and inspect\n", "expected_output": "shape: (100, 5)", "hint": "Use pd.read_csv()"},
            {"order": 2, "title": "Clean Data", "description": "Handle missing values and data types.", "starter_code": "# Clean data\n", "expected_output": "No missing values", "hint": "Check for NaN"},
            {"order": 3, "title": "Calculate Stats", "description": "Find mean, median, peaks for cases/deaths.", "starter_code": "# Statistics\n", "expected_output": "Mean: 150, Max: 500", "hint": "Use .mean(), .max()"},
            {"order": 4, "title": "Create Visualization", "description": "Plot trends over time.", "starter_code": "import matplotlib.pyplot as plt\n# Plot data\n", "expected_output": "Graph saved", "hint": "Use plt.plot()"},
        ],
    },
    {
        "title": "Weather App: API Integration",
        "difficulty": "intermediate",
        "order": 3,
        "real_world_context": "APIs power modern apps. Learn to integrate external services - weather, maps, payment processing, social media.",
        "description": "Build a weather app using free weather API. Display current weather and forecast.",
        "exercises": [
            {"order": 1, "title": "Setup API", "description": "Get API key and make first request.", "starter_code": "import requests\n# Get weather data\n", "expected_output": "200", "hint": "Use OpenWeatherMap free API"},
            {"order": 2, "title": "Parse Response", "description": "Extract temperature, humidity, conditions.", "starter_code": "# Parse JSON\n", "expected_output": "Temp: 25°C", "hint": "response.json()"},
            {"order": 3, "title": "Error Handling", "description": "Handle invalid cities, network errors, API limits.", "starter_code": "try:\n    # Your code\nexcept:\n    pass\n", "expected_output": "City not found", "hint": "Catch exceptions"},
            {"order": 4, "title": "Build UI", "description": "Create simple text-based UI showing forecast.", "starter_code": "# Display weather\n", "expected_output": "Formatted forecast", "hint": "Print nicely"},
        ],
    },
]

# ── Curriculum ───────────────────────────────────────────────────────────────

CURRICULUM = [
    # ── Lesson 1 ──────────────────────────────────────────────────────────────
    {
        "title": "Python Basics",
        "description": "Variables, data types, input/output, and basic operations",
        "order": 1,
        "exercises": [
            {"order": 1, "title": "Hello World", "description": "Print `Hello, World!` to the screen.", "starter_code": "# Write your code here\n", "expected_output": "Hello, World!", "hint": "print('Hello, World!')"},
            {"order": 2, "title": "Variables", "description": "Create a variable `name = 'Python'` and print it.", "starter_code": "# Create a variable and print it\n", "expected_output": "Python", "hint": "name = 'Python'\nprint(name)"},
            {"order": 3, "title": "Multiple Variables", "description": "Create `x = 5`, `y = 3`. Print their sum, difference, and product each on its own line.", "starter_code": "x = 5\ny = 3\n# Print sum, difference, product\n", "expected_output": "8\n2\n15", "hint": "print(x + y)\nprint(x - y)\nprint(x * y)"},
            {"order": 4, "title": "String Concatenation", "description": 'Create `first = \"Hello\"` and `second = \"World\"`, print them joined with a space.', "starter_code": 'first = "Hello"\nsecond = "World"\n# Print joined with a space\n', "expected_output": "Hello World", "hint": 'print(first + " " + second)'},
            {"order": 5, "title": "f-Strings", "description": "Create `name = 'Alice'` and `age = 25`. Print `Alice is 25 years old.` using an f-string.", "starter_code": "name = 'Alice'\nage = 25\n# Use an f-string\n", "expected_output": "Alice is 25 years old.", "hint": "print(f'{name} is {age} years old.')"},
            {"order": 6, "title": "Data Types", "description": "Print the type of `42`, `3.14`, `'hello'`, and `True` each on its own line.", "starter_code": "# Print type of each value\n", "expected_output": "<class 'int'>\n<class 'float'>\n<class 'str'>\n<class 'bool'>", "hint": "print(type(42))\nprint(type(3.14))\nprint(type('hello'))\nprint(type(True))"},
            {"order": 7, "title": "Integer Division & Modulo", "description": "Print the result of `17 // 5` and `17 % 5` each on its own line.", "starter_code": "# Floor division and modulo\n", "expected_output": "3\n2", "hint": "print(17 // 5)\nprint(17 % 5)"},
            {"order": 8, "title": "String Repetition", "description": "Print `ha` repeated 3 times (result: `hahaha`).", "starter_code": "# Repeat 'ha' three times\n", "expected_output": "hahaha", "hint": "print('ha' * 3)"},
        ],
    },
    # ── Lesson 2 ──────────────────────────────────────────────────────────────
    {
        "title": "Strings In Depth",
        "description": "String methods, slicing, and formatting",
        "order": 2,
        "exercises": [
            {"order": 1, "title": "Upper & Lower", "description": "Given `s = 'Hello World'`, print it in uppercase then lowercase.", "starter_code": "s = 'Hello World'\n# Print upper then lower\n", "expected_output": "HELLO WORLD\nhello world", "hint": "print(s.upper())\nprint(s.lower())"},
            {"order": 2, "title": "String Length", "description": "Print the length of `'Python is awesome'`.", "starter_code": "s = 'Python is awesome'\n# Print its length\n", "expected_output": "18", "hint": "print(len(s))"},
            {"order": 3, "title": "Strip Whitespace", "description": "Given `s = '  hello  '`, strip whitespace and print it.", "starter_code": "s = '  hello  '\n# Strip and print\n", "expected_output": "hello", "hint": "print(s.strip())"},
            {"order": 4, "title": "Replace", "description": "Given `s = 'I love Java'`, replace `Java` with `Python` and print.", "starter_code": "s = 'I love Java'\n# Replace Java with Python\n", "expected_output": "I love Python", "hint": "print(s.replace('Java', 'Python'))"},
            {"order": 5, "title": "Split & Join", "description": "Split `'apple,banana,cherry'` by comma and print the list. Then join it with ` | ` and print.", "starter_code": "s = 'apple,banana,cherry'\n# Split then join\n", "expected_output": "['apple', 'banana', 'cherry']\napple | banana | cherry", "hint": "parts = s.split(',')\nprint(parts)\nprint(' | '.join(parts))"},
            {"order": 6, "title": "String Slicing", "description": "Given `s = 'Hello, Python!'`, print the first 5 chars, then chars from index 7 to end.", "starter_code": "s = 'Hello, Python!'\n# Slice the string\n", "expected_output": "Hello\nPython!", "hint": "print(s[:5])\nprint(s[7:])"},
            {"order": 7, "title": "Count & Find", "description": "Given `s = 'banana'`, print how many times `'a'` appears, then the index of the first `'n'`.", "starter_code": "s = 'banana'\n# Count 'a' and find first 'n'\n", "expected_output": "3\n2", "hint": "print(s.count('a'))\nprint(s.find('n'))"},
            {"order": 8, "title": "Palindrome Check", "description": "Check if `'racecar'` is a palindrome. Print `True` or `False`.", "starter_code": "s = 'racecar'\n# Check palindrome\n", "expected_output": "True", "hint": "print(s == s[::-1])"},
        ],
    },
    # ── Lesson 3 ──────────────────────────────────────────────────────────────
    {
        "title": "Control Flow",
        "description": "if/elif/else, for loops, while loops, break, and continue",
        "order": 3,
        "exercises": [
            {"order": 1, "title": "If/Else", "description": "Given `x = 10`, print `positive` if x > 0, else `non-positive`.", "starter_code": "x = 10\n# Check if x is positive\n", "expected_output": "positive", "hint": "if x > 0:\n    print('positive')\nelse:\n    print('non-positive')"},
            {"order": 2, "title": "elif Chain", "description": "Given `score = 75`, print `A` (>=90), `B` (>=80), `C` (>=70), `D` (>=60), or `F`.", "starter_code": "score = 75\n# Grade the score\n", "expected_output": "C", "hint": "if score >= 90: print('A')\nelif score >= 80: print('B')\nelif score >= 70: print('C')\nelif score >= 60: print('D')\nelse: print('F')"},
            {"order": 3, "title": "For Loop", "description": "Print numbers 1 through 5, each on its own line.", "starter_code": "# Use a for loop\n", "expected_output": "1\n2\n3\n4\n5", "hint": "for i in range(1, 6):\n    print(i)"},
            {"order": 4, "title": "For with Step", "description": "Print even numbers from 2 to 10 (inclusive) each on its own line.", "starter_code": "# Print even numbers 2 to 10\n", "expected_output": "2\n4\n6\n8\n10", "hint": "for i in range(2, 11, 2):\n    print(i)"},
            {"order": 5, "title": "While Loop", "description": "Print `count: 0`, `count: 1`, `count: 2` using a while loop.", "starter_code": "count = 0\n# Use a while loop\n", "expected_output": "count: 0\ncount: 1\ncount: 2", "hint": "while count < 3:\n    print('count:', count)\n    count += 1"},
            {"order": 6, "title": "Break", "description": "Loop through 1-10, print each number, but stop (break) when you reach 5.", "starter_code": "# Break at 5\n", "expected_output": "1\n2\n3\n4\n5", "hint": "for i in range(1, 11):\n    print(i)\n    if i == 5:\n        break"},
            {"order": 7, "title": "Continue", "description": "Print numbers 1-10, skipping multiples of 3.", "starter_code": "# Skip multiples of 3\n", "expected_output": "1\n2\n4\n5\n7\n8\n10", "hint": "for i in range(1, 11):\n    if i % 3 == 0:\n        continue\n    print(i)"},
            {"order": 8, "title": "FizzBuzz", "description": "For 1-15: print Fizz (÷3), Buzz (÷5), FizzBuzz (÷both), else the number.", "starter_code": "# FizzBuzz 1 to 15\n", "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz", "hint": "Check % 15 first, then % 3, then % 5."},
            {"order": 9, "title": "Sum of List", "description": "Sum all numbers in `nums = [4, 7, 2, 9, 1]` using a loop and print the result.", "starter_code": "nums = [4, 7, 2, 9, 1]\ntotal = 0\n# Sum with a loop\n", "expected_output": "23", "hint": "for n in nums:\n    total += n\nprint(total)"},
        ],
    },
    # ── Lesson 4 ──────────────────────────────────────────────────────────────
    {
        "title": "Functions",
        "description": "Defining functions, parameters, return values, and scope",
        "order": 4,
        "exercises": [
            {"order": 1, "title": "Define a Function", "description": "Define `greet()` that prints `Hello from a function!`, then call it.", "starter_code": "# Define and call greet()\n", "expected_output": "Hello from a function!", "hint": "def greet():\n    print('Hello from a function!')\ngreet()"},
            {"order": 2, "title": "Return Value", "description": "Define `add(a, b)` that returns a+b. Print `add(3, 4)`.", "starter_code": "# Define add(a, b)\n", "expected_output": "7", "hint": "def add(a, b):\n    return a + b\nprint(add(3, 4))"},
            {"order": 3, "title": "Default Parameters", "description": "Define `power(base, exp=2)`. Print `power(3)` and `power(2, 3)`.", "starter_code": "# Define power() with default exp=2\n", "expected_output": "9\n8", "hint": "def power(base, exp=2):\n    return base**exp\nprint(power(3))\nprint(power(2, 3))"},
            {"order": 4, "title": "Multiple Return Values", "description": "Define `min_max(nums)` that returns the min and max of a list. Print `min_max([3,1,4,1,5,9])`.", "starter_code": "# Return min and max\n", "expected_output": "1 9", "hint": "def min_max(nums):\n    return min(nums), max(nums)\nlo, hi = min_max([3,1,4,1,5,9])\nprint(lo, hi)"},
            {"order": 5, "title": "*args", "description": "Define `total(*nums)` that returns the sum of all arguments. Print `total(1, 2, 3, 4, 5)`.", "starter_code": "# Use *args\n", "expected_output": "15", "hint": "def total(*nums):\n    return sum(nums)\nprint(total(1, 2, 3, 4, 5))"},
            {"order": 6, "title": "Recursion — Fibonacci", "description": "Define `fib(n)` recursively returning the nth Fibonacci number. Print `fib(7)` (answer: 13).", "starter_code": "# fib(0)=0, fib(1)=1, fib(n)=fib(n-1)+fib(n-2)\n", "expected_output": "13", "hint": "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)\nprint(fib(7))"},
            {"order": 7, "title": "Recursive Factorial", "description": "Define `factorial(n)` recursively. Print `factorial(5)`.", "starter_code": "# Recursive factorial\n", "expected_output": "120", "hint": "def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n-1)\nprint(factorial(5))"},
            {"order": 8, "title": "is_even / is_odd", "description": "Define `is_even(n)` returning True/False. Print `is_even(4)` and `is_even(7)`.", "starter_code": "# Define is_even\n", "expected_output": "True\nFalse", "hint": "def is_even(n):\n    return n % 2 == 0\nprint(is_even(4))\nprint(is_even(7))"},
        ],
    },
    # ── Lesson 5 ──────────────────────────────────────────────────────────────
    {
        "title": "Lists & Tuples",
        "description": "Creating, slicing, and manipulating lists and tuples",
        "order": 5,
        "exercises": [
            {"order": 1, "title": "List Basics", "description": "Create `fruits = ['apple','banana','cherry']` and print each item on a new line.", "starter_code": "fruits = ['apple', 'banana', 'cherry']\n# Print each\n", "expected_output": "apple\nbanana\ncherry", "hint": "for fruit in fruits:\n    print(fruit)"},
            {"order": 2, "title": "List Indexing", "description": "Given `nums = [10, 20, 30, 40, 50]`, print the first, last, and middle elements.", "starter_code": "nums = [10, 20, 30, 40, 50]\n# First, last, middle\n", "expected_output": "10\n50\n30", "hint": "print(nums[0])\nprint(nums[-1])\nprint(nums[2])"},
            {"order": 3, "title": "List Slicing", "description": "Given `nums = [0,1,2,3,4,5,6,7,8,9]`, print elements from index 3 to 7 (exclusive).", "starter_code": "nums = list(range(10))\n# Slice index 3 to 7\n", "expected_output": "[3, 4, 5, 6]", "hint": "print(nums[3:7])"},
            {"order": 4, "title": "List Methods", "description": "Start with `nums = [3,1,4,1,5]`. Append 9, remove the first `1`, sort it, print it.", "starter_code": "nums = [3, 1, 4, 1, 5]\n# Append 9, remove first 1, sort, print\n", "expected_output": "[1, 3, 4, 5, 9]", "hint": "nums.append(9)\nnums.remove(1)\nnums.sort()\nprint(nums)"},
            {"order": 5, "title": "Reverse a List", "description": "Reverse `[1, 2, 3, 4, 5]` and print it.", "starter_code": "nums = [1, 2, 3, 4, 5]\n# Reverse and print\n", "expected_output": "[5, 4, 3, 2, 1]", "hint": "nums.reverse()\nprint(nums)  # or print(nums[::-1])"},
            {"order": 6, "title": "List Comprehension", "description": "Use a list comprehension to create squares of 1-5. Print the list.", "starter_code": "# Create [1, 4, 9, 16, 25] with a comprehension\n", "expected_output": "[1, 4, 9, 16, 25]", "hint": "print([x**2 for x in range(1, 6)])"},
            {"order": 7, "title": "Filter with Comprehension", "description": "From `nums = [1..10]`, create a list of only even numbers using a comprehension. Print it.", "starter_code": "nums = list(range(1, 11))\n# Filter evens\n", "expected_output": "[2, 4, 6, 8, 10]", "hint": "print([x for x in nums if x % 2 == 0])"},
            {"order": 8, "title": "Tuples", "description": "Create a tuple `point = (3, 7)`. Print each value and the length of the tuple.", "starter_code": "point = (3, 7)\n# Print values and length\n", "expected_output": "3\n7\n2", "hint": "print(point[0])\nprint(point[1])\nprint(len(point))"},
            {"order": 9, "title": "Enumerate", "description": "Print the index and value for each item in `['a', 'b', 'c']` as `0: a`, `1: b`, `2: c`.", "starter_code": "items = ['a', 'b', 'c']\n# Use enumerate\n", "expected_output": "0: a\n1: b\n2: c", "hint": "for i, v in enumerate(items):\n    print(f'{i}: {v}')"},
        ],
    },
    # ── Lesson 6 ──────────────────────────────────────────────────────────────
    {
        "title": "Dictionaries & Sets",
        "description": "Key-value pairs, set operations, and nested data",
        "order": 6,
        "exercises": [
            {"order": 1, "title": "Dictionary Basics", "description": 'Create `person = {\"name\":\"Alice\",\"age\":25}` and print each key-value as `name: Alice` etc.', "starter_code": 'person = {"name": "Alice", "age": 25}\n# Print each key-value\n', "expected_output": "name: Alice\nage: 25", "hint": "for k, v in person.items():\n    print(f'{k}: {v}')"},
            {"order": 2, "title": "Dict get()", "description": "Given `d = {'a': 1, 'b': 2}`, print `d.get('a')` and `d.get('z', 0)`.", "starter_code": "d = {'a': 1, 'b': 2}\n# Use get() with default\n", "expected_output": "1\n0", "hint": "print(d.get('a'))\nprint(d.get('z', 0))"},
            {"order": 3, "title": "Dict Keys & Values", "description": "Print the sorted keys and sorted values of `{'banana':3,'apple':5,'cherry':1}`.", "starter_code": "d = {'banana': 3, 'apple': 5, 'cherry': 1}\n# Print sorted keys, then sorted values\n", "expected_output": "['apple', 'banana', 'cherry']\n[1, 3, 5]", "hint": "print(sorted(d.keys()))\nprint(sorted(d.values()))"},
            {"order": 4, "title": "Word Count", "description": "Count how many times each word appears in `'the cat sat on the mat the cat'`. Print sorted by key.", "starter_code": "text = 'the cat sat on the mat the cat'\n# Count each word\n", "expected_output": "cat: 2\nmat: 1\non: 1\nsat: 1\nthe: 3", "hint": "counts = {}\nfor w in text.split():\n    counts[w] = counts.get(w, 0) + 1\nfor k in sorted(counts):\n    print(f'{k}: {counts[k]}')"},
            {"order": 5, "title": "Nested Dict", "description": "Create `students = {'Alice': {'grade': 'A'}, 'Bob': {'grade': 'B'}}`. Print Alice's grade.", "starter_code": "students = {'Alice': {'grade': 'A'}, 'Bob': {'grade': 'B'}}\n# Print Alice's grade\n", "expected_output": "A", "hint": "print(students['Alice']['grade'])"},
            {"order": 6, "title": "Set Basics", "description": "Create `a={1,2,3,4}` and `b={3,4,5,6}`. Print union, intersection, and difference (a-b).", "starter_code": "a = {1, 2, 3, 4}\nb = {3, 4, 5, 6}\n# Union, intersection, difference\n", "expected_output": "{1, 2, 3, 4, 5, 6}\n{3, 4}\n{1, 2}", "hint": "print(a | b)\nprint(a & b)\nprint(a - b)"},
            {"order": 7, "title": "Remove Duplicates", "description": "Given `nums = [1,2,2,3,3,3,4]`, use a set to remove duplicates then print sorted.", "starter_code": "nums = [1, 2, 2, 3, 3, 3, 4]\n# Remove duplicates\n", "expected_output": "[1, 2, 3, 4]", "hint": "print(sorted(set(nums)))"},
        ],
    },
    # ── Lesson 7 ──────────────────────────────────────────────────────────────
    {
        "title": "List Comprehensions & Lambdas",
        "description": "Compact expressions, map, filter, and sorted with key",
        "order": 7,
        "exercises": [
            {"order": 1, "title": "Basic Comprehension", "description": "Create a list of cubes of 1-6 using a comprehension. Print it.", "starter_code": "# List of cubes 1-6\n", "expected_output": "[1, 8, 27, 64, 125, 216]", "hint": "print([x**3 for x in range(1, 7)])"},
            {"order": 2, "title": "Conditional Comprehension", "description": "From `range(1, 21)`, create a list of numbers divisible by 3 or 5. Print it.", "starter_code": "# Divisible by 3 or 5, 1-20\n", "expected_output": "[3, 5, 6, 9, 10, 12, 15, 18, 20]", "hint": "print([x for x in range(1, 21) if x % 3 == 0 or x % 5 == 0])"},
            {"order": 3, "title": "Dict Comprehension", "description": "Create a dict mapping numbers 1-5 to their squares. Print it.", "starter_code": "# Dict comprehension\n", "expected_output": "{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}", "hint": "print({x: x**2 for x in range(1, 6)})"},
            {"order": 4, "title": "Lambda Basics", "description": "Create a lambda that doubles a number. Print `double(7)`.", "starter_code": "# Lambda to double a number\n", "expected_output": "14", "hint": "double = lambda x: x * 2\nprint(double(7))"},
            {"order": 5, "title": "map()", "description": "Use `map()` with a lambda to square each number in `[1,2,3,4,5]`. Print the result as a list.", "starter_code": "nums = [1, 2, 3, 4, 5]\n# map with lambda\n", "expected_output": "[1, 4, 9, 16, 25]", "hint": "print(list(map(lambda x: x**2, nums)))"},
            {"order": 6, "title": "filter()", "description": "Use `filter()` to keep only odd numbers from `[1..10]`. Print as a list.", "starter_code": "nums = list(range(1, 11))\n# filter odd numbers\n", "expected_output": "[1, 3, 5, 7, 9]", "hint": "print(list(filter(lambda x: x % 2 != 0, nums)))"},
            {"order": 7, "title": "sorted() with key", "description": "Sort `['banana','apple','kiwi','cherry']` by string length and print.", "starter_code": "words = ['banana', 'apple', 'kiwi', 'cherry']\n# Sort by length\n", "expected_output": "['kiwi', 'apple', 'banana', 'cherry']", "hint": "print(sorted(words, key=len))"},
        ],
    },
    # ── Lesson 8 ──────────────────────────────────────────────────────────────
    {
        "title": "Object-Oriented Programming",
        "description": "Classes, constructors, methods, inheritance, and special methods",
        "order": 8,
        "exercises": [
            {"order": 1, "title": "Create a Class", "description": "Create class `Dog` with `bark()` printing `Woof!`. Create an instance and call it.", "starter_code": "# Define Dog class\n", "expected_output": "Woof!", "hint": "class Dog:\n    def bark(self):\n        print('Woof!')\nDog().bark()"},
            {"order": 2, "title": "Constructor", "description": "Create `Person` with `__init__(name, age)`. Print `Alice is 30 years old.`", "starter_code": "# Define Person\n", "expected_output": "Alice is 30 years old.", "hint": "class Person:\n    def __init__(self, name, age):\n        self.name = name; self.age = age\np = Person('Alice', 30)\nprint(f'{p.name} is {p.age} years old.')"},
            {"order": 3, "title": "Instance Method", "description": "Add `greet()` to `Person` that prints `Hi, I'm Alice!`. Create `Person('Alice', 30)` and call `greet()`.", "starter_code": "class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    # Add greet() method\n", "expected_output": "Hi, I'm Alice!", "hint": "def greet(self):\n    print(f\"Hi, I'm {self.name}!\")"},
            {"order": 4, "title": "__str__", "description": "Add `__str__` to `Person` returning `Person(Alice, 30)`. Print a `Person('Alice', 30)` instance.", "starter_code": "class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    # Add __str__\n", "expected_output": "Person(Alice, 30)", "hint": "def __str__(self):\n    return f'Person({self.name}, {self.age})'"},
            {"order": 5, "title": "Class Variable", "description": "Add a class variable `species = 'Canis lupus'` to `Dog`. Print `Dog.species`.", "starter_code": "class Dog:\n    # Add class variable species\n    pass\n", "expected_output": "Canis lupus", "hint": "class Dog:\n    species = 'Canis lupus'\nprint(Dog.species)"},
            {"order": 6, "title": "Inheritance", "description": "Create `Animal` with `speak()` printing `...`, and `Cat(Animal)` overriding it to print `Meow!`.", "starter_code": "# Define Animal and Cat\n", "expected_output": "Meow!", "hint": "class Cat(Animal):\n    def speak(self):\n        print('Meow!')\nCat().speak()"},
            {"order": 7, "title": "super()", "description": "Create `Vehicle(brand)` and `Car(Vehicle, model)`. Car's `__init__` uses `super()`. Print `Toyota Corolla`.", "starter_code": "class Vehicle:\n    def __init__(self, brand):\n        self.brand = brand\n\nclass Car(Vehicle):\n    def __init__(self, brand, model):\n        # Use super()\n        pass\n", "expected_output": "Toyota Corolla", "hint": "super().__init__(brand)\nself.model = model\nc = Car('Toyota','Corolla')\nprint(c.brand, c.model)"},
            {"order": 8, "title": "Property", "description": "Create `Circle(radius)` with a `@property` `area` returning π*r². Print area of circle with r=5 (round to 2 decimals).", "starter_code": "import math\nclass Circle:\n    def __init__(self, radius):\n        self.radius = radius\n    # Add area property\n", "expected_output": "78.54", "hint": "@property\ndef area(self):\n    return round(math.pi * self.radius**2, 2)\nprint(Circle(5).area)"},
        ],
    },
    # ── Lesson 9 ──────────────────────────────────────────────────────────────
    {
        "title": "Error Handling",
        "description": "try/except, multiple exceptions, finally, and custom exceptions",
        "order": 9,
        "exercises": [
            {"order": 1, "title": "Try/Except", "description": "Try to convert `'abc'` to int. Catch ValueError and print `Invalid number`.", "starter_code": "# Handle ValueError\n", "expected_output": "Invalid number", "hint": "try:\n    int('abc')\nexcept ValueError:\n    print('Invalid number')"},
            {"order": 2, "title": "ZeroDivisionError", "description": "Try `10 / 0`. Catch ZeroDivisionError and print `Cannot divide by zero`.", "starter_code": "# Catch ZeroDivisionError\n", "expected_output": "Cannot divide by zero", "hint": "try:\n    10 / 0\nexcept ZeroDivisionError:\n    print('Cannot divide by zero')"},
            {"order": 3, "title": "Multiple Except", "description": "Try `int('x') + 1/0`. Catch ValueError printing `bad value`, ZeroDivisionError printing `div zero`.", "starter_code": "# Multiple except blocks\n", "expected_output": "bad value", "hint": "try:\n    int('x') + 1/0\nexcept ValueError:\n    print('bad value')\nexcept ZeroDivisionError:\n    print('div zero')"},
            {"order": 4, "title": "Finally", "description": "Try `10/0`, print `Error` in except, print `Done` in finally.", "starter_code": "# try/except/finally\n", "expected_output": "Error\nDone", "hint": "try:\n    10/0\nexcept:\n    print('Error')\nfinally:\n    print('Done')"},
            {"order": 5, "title": "else Clause", "description": "Try converting `'42'` to int. If successful (else), print `Success: 42`. If error, print `Failed`.", "starter_code": "# try/except/else\n", "expected_output": "Success: 42", "hint": "try:\n    n = int('42')\nexcept:\n    print('Failed')\nelse:\n    print(f'Success: {n}')"},
            {"order": 6, "title": "Raise Exception", "description": "Define `check_age(age)` raising `ValueError('Too young')` if age < 18. Catch and print it.", "starter_code": "# Define check_age\n", "expected_output": "Too young", "hint": "def check_age(age):\n    if age < 18: raise ValueError('Too young')\ntry:\n    check_age(15)\nexcept ValueError as e:\n    print(e)"},
            {"order": 7, "title": "Custom Exception", "description": "Create `NegativeError(Exception)`. Raise it if `n = -5` is negative. Catch and print `Negative number: -5`.", "starter_code": "# Custom exception\n", "expected_output": "Negative number: -5", "hint": "class NegativeError(Exception): pass\nn = -5\ntry:\n    if n < 0: raise NegativeError(f'Negative number: {n}')\nexcept NegativeError as e:\n    print(e)"},
        ],
    },
    # ── Lesson 10 ──────────────────────────────────────────────────────────────
    {
        "title": "Modules & the Standard Library",
        "description": "math, random, datetime, os.path, and collections",
        "order": 10,
        "exercises": [
            {"order": 1, "title": "math module", "description": "Import math. Print `math.sqrt(144)` and `math.pi` rounded to 4 decimals.", "starter_code": "import math\n# Print sqrt(144) and pi to 4 decimals\n", "expected_output": "12.0\n3.1416", "hint": "print(math.sqrt(144))\nprint(round(math.pi, 4))"},
            {"order": 2, "title": "math.ceil / floor", "description": "Print `math.ceil(4.3)` and `math.floor(4.9)`.", "starter_code": "import math\n# ceil and floor\n", "expected_output": "5\n4", "hint": "print(math.ceil(4.3))\nprint(math.floor(4.9))"},
            {"order": 3, "title": "random module", "description": "Set `random.seed(42)`. Print `random.randint(1, 10)` (should be 2).", "starter_code": "import random\n# Seed 42, print a random int 1-10\n", "expected_output": "2", "hint": "random.seed(42)\nprint(random.randint(1, 10))"},
            {"order": 4, "title": "random.choice", "description": "Set `random.seed(1)`. Use `random.choice(['rock','paper','scissors'])`. Print the result.", "starter_code": "import random\nrandom.seed(1)\nchoices = ['rock', 'paper', 'scissors']\n# Pick one randomly\n", "expected_output": "rock", "hint": "print(random.choice(choices))"},
            {"order": 5, "title": "datetime", "description": "Create `datetime.date(2024, 1, 15)`. Print it and its `.year`.", "starter_code": "import datetime\n# Create date and print it + year\n", "expected_output": "2024-01-15\n2024", "hint": "d = datetime.date(2024, 1, 15)\nprint(d)\nprint(d.year)"},
            {"order": 6, "title": "collections.Counter", "description": "Use Counter on `'mississippi'`. Print the 3 most common letters as a sorted list of tuples.", "starter_code": "from collections import Counter\ns = 'mississippi'\n# Count and show top 3\n", "expected_output": "[('s', 4), ('i', 4), ('p', 2)]", "hint": "c = Counter(s)\nprint(c.most_common(3))"},
            {"order": 7, "title": "collections.defaultdict", "description": "Use defaultdict(list) to group `[('a',1),('b',2),('a',3)]` by key. Print the dict.", "starter_code": "from collections import defaultdict\npairs = [('a', 1), ('b', 2), ('a', 3)]\n# Group by key\n", "expected_output": "{'a': [1, 3], 'b': [2]}", "hint": "d = defaultdict(list)\nfor k, v in pairs:\n    d[k].append(v)\nprint(dict(d))"},
        ],
    },
    # ── Lesson 11 ──────────────────────────────────────────────────────────────
    {
        "title": "File I/O",
        "description": "Reading and writing files, working with text data",
        "order": 11,
        "exercises": [
            {"order": 1, "title": "Write a File", "description": "Write `Hello, File!` to a file called `test.txt`, then read and print it.", "starter_code": "# Write then read test.txt\n", "expected_output": "Hello, File!", "hint": "with open('test.txt', 'w') as f:\n    f.write('Hello, File!')\nwith open('test.txt') as f:\n    print(f.read())"},
            {"order": 2, "title": "Write Multiple Lines", "description": "Write `line1`, `line2`, `line3` to `lines.txt` (one per line), then read and print the file.", "starter_code": "# Write 3 lines, then read\n", "expected_output": "line1\nline2\nline3", "hint": "with open('lines.txt','w') as f:\n    f.write('line1\\nline2\\nline3')\nwith open('lines.txt') as f:\n    print(f.read().strip())"},
            {"order": 3, "title": "Read Lines", "description": "Write `a\\nb\\nc` to `abc.txt`, read line by line and print each stripped line.", "starter_code": "# Write then read line by line\n", "expected_output": "a\nb\nc", "hint": "with open('abc.txt','w') as f:\n    f.write('a\\nb\\nc')\nwith open('abc.txt') as f:\n    for line in f:\n        print(line.strip())"},
            {"order": 4, "title": "Append to File", "description": "Write `first` to `app.txt`, then append `second`. Read and print.", "starter_code": "# Write, append, read\n", "expected_output": "firstsecond", "hint": "with open('app.txt','w') as f: f.write('first')\nwith open('app.txt','a') as f: f.write('second')\nwith open('app.txt') as f: print(f.read())"},
            {"order": 5, "title": "Count Words in File", "description": "Write `the quick brown fox jumps` to `words.txt`. Count and print the number of words.", "starter_code": "# Write sentence, count words\n", "expected_output": "5", "hint": "with open('words.txt','w') as f:\n    f.write('the quick brown fox jumps')\nwith open('words.txt') as f:\n    print(len(f.read().split()))"},
        ],
    },
    # ── Lesson 12 ──────────────────────────────────────────────────────────────
    {
        "title": "Iterators & Generators",
        "description": "zip, enumerate, itertools, yield, and generator expressions",
        "order": 12,
        "exercises": [
            {"order": 1, "title": "zip()", "description": "Zip `names=['Alice','Bob','Charlie']` and `scores=[95,87,92]`. Print each as `Alice: 95` etc.", "starter_code": "names = ['Alice', 'Bob', 'Charlie']\nscores = [95, 87, 92]\n# zip and print\n", "expected_output": "Alice: 95\nBob: 87\nCharlie: 92", "hint": "for name, score in zip(names, scores):\n    print(f'{name}: {score}')"},
            {"order": 2, "title": "enumerate()", "description": "Print `1. apple`, `2. banana`, `3. cherry` from the list using enumerate (starting at 1).", "starter_code": "fruits = ['apple', 'banana', 'cherry']\n# enumerate starting at 1\n", "expected_output": "1. apple\n2. banana\n3. cherry", "hint": "for i, f in enumerate(fruits, 1):\n    print(f'{i}. {f}')"},
            {"order": 3, "title": "Generator Function", "description": "Define `count_up(n)` that yields 1 through n. Print each value from `count_up(4)`.", "starter_code": "# Generator using yield\n", "expected_output": "1\n2\n3\n4", "hint": "def count_up(n):\n    for i in range(1, n+1):\n        yield i\nfor v in count_up(4):\n    print(v)"},
            {"order": 4, "title": "Generator Expression", "description": "Use a generator expression to sum squares of 1-100. Print the result.", "starter_code": "# Sum of squares 1-100 via generator\n", "expected_output": "338350", "hint": "print(sum(x**2 for x in range(1, 101)))"},
            {"order": 5, "title": "itertools.chain", "description": "Use `itertools.chain` to iterate `[1,2,3]` and `[4,5,6]` together. Print each value.", "starter_code": "import itertools\na = [1, 2, 3]\nb = [4, 5, 6]\n# chain and print\n", "expected_output": "1\n2\n3\n4\n5\n6", "hint": "for v in itertools.chain(a, b):\n    print(v)"},
            {"order": 6, "title": "itertools.combinations", "description": "Print all 2-element combinations of `['A','B','C']`.", "starter_code": "import itertools\nitems = ['A', 'B', 'C']\n# 2-element combinations\n", "expected_output": "('A', 'B')\n('A', 'C')\n('B', 'C')", "hint": "for c in itertools.combinations(items, 2):\n    print(c)"},
        ],
    },
    # ── Lesson 13 ──────────────────────────────────────────────────────────────
    {
        "title": "Decorators & Context Managers",
        "description": "Higher-order functions, functools, and the with statement",
        "order": 13,
        "exercises": [
            {"order": 1, "title": "Simple Decorator", "description": "Write a `shout` decorator that uppercases the return value of a function. Decorate `greet()` returning `'hello'`. Print the result.", "starter_code": "# Write shout decorator\ndef shout(func):\n    pass\n\n@shout\ndef greet():\n    return 'hello'\n\nprint(greet())\n", "expected_output": "HELLO", "hint": "def shout(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs).upper()\n    return wrapper"},
            {"order": 2, "title": "Decorator with Arguments", "description": "Write a `repeat(n)` decorator that calls the function n times. Apply `@repeat(3)` to `say()` printing `hi`.", "starter_code": "def repeat(n):\n    # return a decorator\n    pass\n\n@repeat(3)\ndef say():\n    print('hi')\n\nsay()\n", "expected_output": "hi\nhi\nhi", "hint": "def repeat(n):\n    def decorator(func):\n        def wrapper(*a, **k):\n            for _ in range(n): func(*a, **k)\n        return wrapper\n    return decorator"},
            {"order": 3, "title": "functools.wraps", "description": "Rewrite the `shout` decorator using `@functools.wraps`. Check that `greet.__name__` is still `greet`.", "starter_code": "import functools\n\ndef shout(func):\n    # Use @functools.wraps\n    pass\n\n@shout\ndef greet():\n    return 'hello'\n\nprint(greet())\nprint(greet.__name__)\n", "expected_output": "HELLO\ngreet", "hint": "@functools.wraps(func)\ndef wrapper(*a, **k):\n    return func(*a, **k).upper()"},
            {"order": 4, "title": "Context Manager (with)", "description": "Use `open()` as a context manager to write `hello` to `cm.txt` and read it back.", "starter_code": "# Write with context manager, then read\n", "expected_output": "hello", "hint": "with open('cm.txt','w') as f:\n    f.write('hello')\nwith open('cm.txt') as f:\n    print(f.read())"},
            {"order": 5, "title": "Custom Context Manager", "description": "Use `contextlib.contextmanager` to create a `managed()` context that prints `enter` then `exit`. Use it with `with managed(): print('inside')`.", "starter_code": "from contextlib import contextmanager\n\n@contextmanager\ndef managed():\n    # yield between enter and exit\n    pass\n\nwith managed():\n    print('inside')\n", "expected_output": "enter\ninside\nexit", "hint": "print('enter')\nyield\nprint('exit')"},
        ],
    },
    # ── Lesson 14 ──────────────────────────────────────────────────────────────
    {
        "title": "NumPy Basics",
        "description": "NumPy (Numerical Python) is a powerful library for numerical computing. It provides:\n• **Fast arrays**: NumPy arrays are much faster than Python lists for numerical operations\n• **Mathematical functions**: Built-in functions for linear algebra, statistics, and more\n• **Multi-dimensional data**: Handle matrices and higher-dimensional arrays easily\n\nWhy NumPy? Python lists are slow for math. NumPy arrays are 50-100x faster! Used in data science, machine learning, scientific computing, and finance.",
        "order": 14,
        "exercises": [
            {"order": 1, "title": "Create Array", "description": "**What it does**: Creates a NumPy array (a fast numerical array).\n**Why?** NumPy arrays are the foundation of numerical computing in Python. Unlike Python lists, they're optimized for math.\n**Difference**: Regular list `[1,2,3]` vs NumPy array `np.array([1,2,3])` - the array is 10x faster!\n**Real-world use**: Store sensor data, pixel values in images, stock prices, temperature readings, etc.\n\nCreate an array and print it.", "starter_code": "import numpy as np\n# Create array from a list\n", "expected_output": "[1 2 3 4 5]", "hint": "arr = np.array([1, 2, 3, 4, 5])\nprint(arr)"},
            {"order": 2, "title": "Array Shape", "description": "**What it does**: Gets the dimensions (shape) of a NumPy array.\n**Why?** Arrays can be 1D (line), 2D (table), 3D (cube), etc. You need to know the shape for operations.\n**Shape format**: `(rows, columns)` for 2D arrays.\n**Example**: Shape `(2, 3)` means 2 rows and 3 columns = a 2×3 table\n**Real-world use**: Images have shape (height, width, colors). Understanding shape is crucial in deep learning!\n\nCreate a 2D array and print its shape.", "starter_code": "import numpy as np\n# Create 2D array and print shape\narr = np.array([[1, 2, 3], [4, 5, 6]])\n", "expected_output": "(2, 3)", "hint": "print(arr.shape)"},
            {"order": 3, "title": "Array Indexing", "description": "**What it does**: Access individual elements in an array using index positions.\n**Why?** To get specific values from your data.\n**Indexing rules**: Starts at 0! Index 0 = first element, index 2 = third element.\n**Visual**: Array `[10, 20, 30, 40, 50]` → Index 2 = `30`\n**Real-world use**: Get a pixel value from an image, get a specific sensor reading, access database records.\n\nAccess the element at index 2 and print it.", "starter_code": "import numpy as np\narr = np.array([10, 20, 30, 40, 50])\n# Get element at index 2\n", "expected_output": "30", "hint": "print(arr[2])"},
            {"order": 4, "title": "Array Slicing", "description": "**What it does**: Extract a portion (slice) of an array.\n**Why?** Often you need only part of your data (e.g., first 10 rows of a dataset).\n**Syntax**: `arr[start:end]` extracts from index `start` to `end-1`\n**Visual**: Slice `arr[1:3]` gets indices 1 and 2 (NOT 3!)\n**Real-world use**: Get specific rows from a dataset, extract a portion of an audio file, crop an image.\n\nSlice the array from index 1 to 3 (exclusive) and print it.", "starter_code": "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\n# Slice from index 1 to 3\n", "expected_output": "[2 3]", "hint": "print(arr[1:3])"},
            {"order": 5, "title": "Array Operations", "description": "**What it does**: Performs math on entire arrays at once (element-wise operations).\n**Why?** NumPy's superpower! Add 1 million numbers instantly.\n**How it works**: Each element in array A is added to the corresponding element in array B.\n**Visual**: `[1,2,3] + [4,5,6] = [5,7,9]` (element by element)\n**Real-world use**: Image processing (add brightness), sensor fusion (combine readings), financial calculations.\n\nAdd two arrays element-wise and print the result.", "starter_code": "import numpy as np\na = np.array([1, 2, 3])\nb = np.array([4, 5, 6])\n# Add element by element\n", "expected_output": "[5 7 9]", "hint": "print(a + b)"},
            {"order": 6, "title": "Array Methods", "description": "**What it does**: Computes statistics on your data (mean, max, min, sum, std, etc.).\n**Why?** Essential for data analysis - find trends, outliers, averages.\n**Methods**: `.mean()` = average, `.max()` = largest, `.min()` = smallest, `.sum()` = total\n**Example**: Array `[3,1,4,1,5]` → mean=2.8, max=5, min=1\n**Real-world use**: Find average temperature, detect anomalies, summarize sensor data, calculate statistics.\n\nCompute mean, max, and min of an array.", "starter_code": "import numpy as np\narr = np.array([3, 1, 4, 1, 5])\n# Calculate statistics\n", "expected_output": "2.8\n5\n1", "hint": "print(arr.mean())\nprint(arr.max())\nprint(arr.min())"},
        ],
    },
    # ── Lesson 15 ──────────────────────────────────────────────────────────────
    {
        "title": "Pandas Basics",
        "description": "Pandas (Python Data Analysis Library) is the go-to tool for working with tabular data. It provides:\n• **Series**: 1D labeled data (like a column in Excel)\n• **DataFrames**: 2D tables with rows and columns (like Excel spreadsheets!)\n• **Data manipulation**: Filter, sort, group, aggregate data easily\n• **File I/O**: Read/write CSV, Excel, SQL databases\n\nWhy Pandas? 95% of data scientists use it. It makes data analysis 10x faster than raw Python. If you're doing data work, Pandas is essential!",
        "order": 15,
        "exercises": [
            {"order": 1, "title": "Create Series", "description": "**What it does**: Creates a Pandas Series (1D labeled array, like a column in Excel).\n**Why?** Series is the basic building block for working with tabular data.\n**Structure**: Series has index (0, 1, 2...) on left and values on right\n**Difference**: NumPy array vs Pandas Series - Series has labels (indices) and metadata\n**Real-world use**: Store a single column of data (e.g., temperature readings, sales figures, customer ages).\n\nCreate a Series and print it.", "starter_code": "import pandas as pd\n# Create series from a list\n", "expected_output": "0    a\n1    b\n2    c\ndtype: object", "hint": "s = pd.Series(['a','b','c'])\nprint(s)"},
            {"order": 2, "title": "Create DataFrame", "description": "**What it does**: Creates a Pandas DataFrame (2D table, like an Excel spreadsheet).\n**Why?** DataFrames are how you work with real-world data - they have rows AND columns.\n**Structure**: Columns are labeled (name, age, city), rows are indexed (0, 1, 2...)\n**Visual**: Like an Excel sheet with headers\n```\n   name  age\n0  Alice   25\n1    Bob   30\n```\n**Real-world use**: Customer database, sales records, survey responses, any tabular data.\n\nCreate a DataFrame and print it.", "starter_code": "import pandas as pd\n# Create DataFrame from dictionary\ndata = {'name': ['Alice', 'Bob'], 'age': [25, 30]}\n", "expected_output": "    name  age\n0  Alice   25\n1    Bob   30", "hint": "df = pd.DataFrame(data)\nprint(df)"},
            {"order": 3, "title": "DataFrame Shape", "description": "**What it does**: Gets the dimensions (rows, columns) of your DataFrame.\n**Why?** You need to know your data size - how many records? How many fields?\n**Format**: `(rows, columns)` - tells you data size at a glance\n**Example**: Shape `(1000, 5)` = 1000 customer records with 5 fields each\n**Real-world use**: Data validation (\"We expected 1000 records but got only 999!\"), memory planning.\n\nPrint the shape of a DataFrame.", "starter_code": "import pandas as pd\ndf = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})\n# Get shape\n", "expected_output": "(3, 2)", "hint": "print(df.shape)"},
            {"order": 4, "title": "Column Access", "description": "**What it does**: Extract a single column from a DataFrame.\n**Why?** Work with specific data - analyze just the 'age' column, just the 'salary' column, etc.\n**Syntax**: `df['column_name']` returns a Series\n**Visual**: Extract the 'age' column from a table\n**Real-world use**: Calculate statistics on one field (average age, total sales), plot a column, filter based on column values.\n\nAccess and print a specific column.", "starter_code": "import pandas as pd\ndf = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})\n# Access column 'x'\n", "expected_output": "0    1\n1    2\n2    3\nName: x, dtype: int64", "hint": "print(df['x'])"},
            {"order": 5, "title": "DataFrame Filter", "description": "**What it does**: Select rows that match a condition (filtering/querying).\n**Why?** Extract relevant data - find all customers over 25, all sales above $100, all defective products.\n**Syntax**: `df[df['column'] > value]` returns only matching rows\n**Visual**: Filter a customer table to show only those aged > 25\n**Real-world use**: Find high-value customers, detect anomalies, segment data, answer business questions.\n\nFilter rows based on a condition.", "starter_code": "import pandas as pd\ndf = pd.DataFrame({'age': [20, 25, 30]})\n# Filter for age > 22\n", "expected_output": "   age\n1   25\n2   30", "hint": "print(df[df['age'] > 22])"},
            {"order": 6, "title": "DataFrame Methods", "description": "**What it does**: Computes statistics on DataFrame columns (mean, sum, count, std, median, etc.).\n**Why?** Summarize data instantly - answer questions like \"What's the average age?\" \"How many records?\"\n**Methods**: `.mean()` = average, `.sum()` = total, `.count()` = number of non-null values, `.min()`, `.max()`\n**Speed**: Computing stats on 1 million rows is instant with Pandas!\n**Real-world use**: Generate reports, find outliers, validate data quality, exploratory data analysis.\n\nCompute statistics on a DataFrame column.", "starter_code": "import pandas as pd\ndf = pd.DataFrame({'nums': [1, 2, 3, 4, 5]})\n# Calculate statistics\n", "expected_output": "3.0\n15\n5", "hint": "print(df['nums'].mean())\nprint(df['nums'].sum())\nprint(df['nums'].count())"},
        ],
    },
    # ── Lesson 16 ──────────────────────────────────────────────────────────────
    {
        "title": "Requests Library",
        "description": "The Requests library makes HTTP requests easy - no more complicated urllib code! It provides:\n• **GET requests**: Fetch data from APIs and websites\n• **POST requests**: Send data to servers\n• **Headers & params**: Customize requests (User-Agent, authentication, filters)\n• **JSON handling**: Automatic parsing of API responses\n• **Status codes**: Check if request succeeded (200 = OK, 404 = not found, etc.)\n\nWhy Requests? It's the de facto standard for API calls in Python. Learn it for web scraping, automation, and data collection!",
        "order": 16,
        "exercises": [
            {"order": 1, "title": "Basic GET Request", "description": "**What it does**: Makes an HTTP GET request to a server and gets the response.\n**Why?** To fetch data from APIs, websites, web services. The foundation of all API work!\n**Status codes**: 200 = success, 404 = not found, 500 = server error\n**How it works**: Your code → server → server sends back data\n**Real-world use**: Fetch weather data, stock prices, user information from APIs, download web pages.\n\nMake a GET request and check the status code.", "starter_code": "import requests\n# Make GET request to a test API\nurl = 'https://jsonplaceholder.typicode.com/posts/1'\n", "expected_output": "200", "hint": "resp = requests.get(url)\nprint(resp.status_code)"},
            {"order": 2, "title": "JSON Response", "description": "**What it does**: Parses JSON response (converts JSON text to Python dictionary).\n**Why?** Most APIs return JSON. You need to convert it to Python data to use it.\n**JSON format**: Text representation of data: `{\"name\":\"Alice\", \"age\":25}`\n**Parsing**: `.json()` method automatically converts JSON → Python dictionary\n**Real-world use**: Parse API responses (Twitter API, Weather API, GitHub API), work with nested data.\n\nParse JSON response and extract a field.", "starter_code": "import requests\nurl = 'https://jsonplaceholder.typicode.com/posts/1'\n", "expected_output": "sunt aut facere repellat provident", "hint": "resp = requests.get(url)\ndata = resp.json()\nprint(data['title'])"},
            {"order": 3, "title": "Check Response", "description": "**What it does**: Creates a function that validates whether a URL is accessible.\n**Why?** Error handling! Not all URLs work - server might be down, page deleted, no permission.\n**Pattern**: Check status code → if 200, success; else, failure\n**Status codes**: 200 = OK, 404 = not found, 403 = forbidden, 500 = server error\n**Real-world use**: Monitor website uptime, validate API endpoints, health checks, data validation.\n\nWrite a function to check if a URL responds with status 200.", "starter_code": "import requests\n\ndef check_url(url):\n    # Make request and check status\n    pass\n\nprint(check_url('https://jsonplaceholder.typicode.com/posts/1'))\n", "expected_output": "OK", "hint": "resp = requests.get(url)\nreturn 'OK' if resp.status_code == 200 else 'FAIL'"},
            {"order": 4, "title": "Headers", "description": "**What it does**: Adds custom headers to your request (like User-Agent, authentication, content-type).\n**Why?** Servers sometimes block requests without proper headers. User-Agent identifies your application.\n**Headers are metadata**: Tell the server what you are, what you want, how to respond\n**Real-world use**: Bypass simple bot detection, API authentication (Bearer tokens), specify language preferences.\n\nMake a request with custom headers.", "starter_code": "import requests\nheaders = {'User-Agent': 'MyBot/1.0'}\nurl = 'https://jsonplaceholder.typicode.com/posts/1'\n", "expected_output": "200", "hint": "resp = requests.get(url, headers=headers)\nprint(resp.status_code)"},
            {"order": 5, "title": "Query Parameters", "description": "**What it does**: Adds parameters to URL (filtering, pagination, sorting).\n**Why?** APIs often support filters. Instead of fetching 1000 records, get only what you need.\n**Syntax**: `params={'_limit': 2}` → URL becomes `.../posts?_limit=2`\n**Benefits**: Faster (less data), cleaner code, follows API patterns\n**Real-world use**: Pagination (get page 1, 2, 3...), filtering (show only active users), sorting (newest first).\n\nMake a request with query parameters to limit results.", "starter_code": "import requests\nparams = {'_limit': 2}\nurl = 'https://jsonplaceholder.typicode.com/posts'\n", "expected_output": "2", "hint": "resp = requests.get(url, params=params)\nprint(len(resp.json()))"},
            {"order": 6, "title": "POST Request", "description": "**What it does**: Sends data TO a server (create, update, submit data).\n**Why?** GET fetches data. POST sends data. Used for form submissions, API creation, data uploads.\n**JSON body**: Data sent as JSON: `{\"title\":\"New Post\", \"body\":\"Content\"}`\n**Response**: Server typically returns created object with ID\n**Real-world use**: Create user accounts, submit forms, post tweets, add database records, trigger actions on servers.\n\nMake a POST request to create a new resource.", "starter_code": "import requests\ndata = {'title': 'Test', 'body': 'Hello'}\nurl = 'https://jsonplaceholder.typicode.com/posts'\n", "expected_output": "101", "hint": "resp = requests.post(url, json=data)\nprint(resp.json()['id'])"},
        ],
    },
    # ── Lesson 17 ──────────────────────────────────────────────────────────────
    {
        "title": "BeautifulSoup Web Scraping",
        "description": "BeautifulSoup parses HTML and extracts data from web pages. It provides:\n• **HTML parsing**: Convert messy HTML into a searchable structure\n• **Finding elements**: Search by tag, class, id, CSS selectors\n• **Text extraction**: Get text, attributes, links from HTML\n• **Traversal**: Navigate parent/child elements\n\nWhy BeautifulSoup? Extract data from websites (news articles, product prices, quotes, etc.). Combined with Requests, you can automate data collection!",
        "order": 17,
        "exercises": [
            {"order": 1, "title": "Parse HTML", "description": "**What it does**: Converts HTML text into a parsed object you can search and navigate.\n**Why?** Websites are HTML. To extract data, you need to parse and search the structure.\n**How it works**: Raw HTML string → BeautifulSoup parses it → access elements\n**HTML reminder**: `<p>Hello</p>` is a paragraph tag with text \"Hello\"\n**Real-world use**: Parse web pages, scrape news articles, extract product info, analyze website structure.\n\nParse HTML and extract text from a paragraph.", "starter_code": "from bs4 import BeautifulSoup\nhtml = '<p>Hello</p>'\n# Parse HTML\nsoup = BeautifulSoup(html, 'html.parser')\n", "expected_output": "Hello", "hint": "print(soup.p.string)"},
            {"order": 2, "title": "Find Tag", "description": "**What it does**: Finds the first occurrence of a specific HTML tag.\n**Why?** Navigate HTML structure - find all titles, all links, all images, etc.\n**Method**: `.find('tag_name')` returns the first matching tag\n**Visual**: HTML has many tags: `<h1>`, `<p>`, `<a>`, `<img>`, etc. Find what you need!\n**Real-world use**: Extract headline from news site, get product title, find error messages.\n\nFind an h1 tag and extract its text.", "starter_code": "from bs4 import BeautifulSoup\nhtml = '<div><h1>Title</h1></div>'\n# Find h1 tag\nsoup = BeautifulSoup(html, 'html.parser')\n", "expected_output": "Title", "hint": "print(soup.find('h1').string)"},
            {"order": 3, "title": "Find All Tags", "description": "**What it does**: Finds ALL occurrences of a tag (returns a list).\n**Why?** Extract multiple elements - all list items, all product prices, all links on page.\n**Method**: `.find_all('tag_name')` returns a list of all matches\n**Loop through**: Use `for` loop to process each element\n**Real-world use**: Scrape all prices from store, extract all links from page, get all product titles.\n\nFind all list items and count them.", "starter_code": "from bs4 import BeautifulSoup\nhtml = '<ul><li>A</li><li>B</li><li>C</li></ul>'\n# Find all li tags\nsoup = BeautifulSoup(html, 'html.parser')\n", "expected_output": "3", "hint": "print(len(soup.find_all('li')))"},
            {"order": 4, "title": "Extract Attributes", "description": "**What it does**: Extracts attributes (href, src, class, id, data-*, etc.) from HTML tags.\n**Why?** Tags have metadata - links have `href`, images have `src`, etc. You need these values!\n**Syntax**: `tag['attribute_name']` or `tag.get('attribute_name')`\n**Visual**: `<a href=\"google.com\">Link</a>` → extract `href` = \"google.com\"\n**Real-world use**: Extract all links from page, get image URLs, find data attributes, scrape form values.\n\nExtract the href attribute from a link.", "starter_code": "from bs4 import BeautifulSoup\nhtml = '<a href=\"test.html\">Link</a>'\n# Extract href attribute\nsoup = BeautifulSoup(html, 'html.parser')\n", "expected_output": "test.html", "hint": "print(soup.a['href'])"},
            {"order": 5, "title": "CSS Selector", "description": "**What it does**: Uses CSS selectors to find elements (more powerful than .find()).\n**Why?** CSS selectors are powerful - find by class, id, hierarchy, attributes, etc.\n**Selectors**: `tag`, `.class`, `#id`, `tag.class`, `parent > child`\n**Visual**: Find `<p>` inside `<div class='container'>` with `.select('div.container p')`\n**Real-world use**: Complex selections, styling-based extraction, find elements by relationship.\n\nUse CSS selector to find an element.", "starter_code": "from bs4 import BeautifulSoup\nhtml = '<div class=\"container\"><p>Text</p></div>'\n# CSS selector\nsoup = BeautifulSoup(html, 'html.parser')\n", "expected_output": "Text", "hint": "print(soup.select('div.container p')[0].string)"},
            {"order": 6, "title": "Extract Multiple Data", "description": "**What it does**: Combines find_all() with loops and list comprehension to extract data at scale.\n**Why?** Real scraping: extract dozens/hundreds of items from a page efficiently.\n**Pattern**: Find all → Loop through → Extract what you need → Store in list\n**Power**: Extract all product prices, all article titles, all contact info automatically!\n**Real-world use**: Scrape prices from 100 products, extract all tweets, get article metadata from news site.\n\nExtract text from multiple table cells into a list.", "starter_code": "from bs4 import BeautifulSoup\nhtml = '<table><tr><td>A</td><td>B</td></tr><tr><td>C</td><td>D</td></tr></table>'\n# Extract all cell texts\nsoup = BeautifulSoup(html, 'html.parser')\n", "expected_output": "['A', 'B', 'C', 'D']", "hint": "print([td.string for td in soup.find_all('td')])"},
        ],
    },
]

# ── Routes: Auth ─────────────────────────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 200


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return jsonify(user.to_dict()), 200

# ── Routes: Lessons ───────────────────────────────────────────────────────────

@app.route("/api/lessons", methods=["GET"])
@jwt_required()
def get_lessons():
    user_id = int(get_jwt_identity())
    lessons = Lesson.query.order_by(Lesson.order).all()
    completed_ids = {p.exercise_id for p in Progress.query.filter_by(user_id=user_id, completed=True)}

    result = []
    for lesson in lessons:
        exercise_ids = [e.id for e in lesson.exercises]
        data = lesson.to_dict()
        data["completed_count"] = sum(1 for eid in exercise_ids if eid in completed_ids)
        result.append(data)
    return jsonify(result), 200


@app.route("/api/lessons/<int:lesson_id>", methods=["GET"])
@jwt_required()
def get_lesson(lesson_id):
    user_id = int(get_jwt_identity())
    lesson = Lesson.query.get_or_404(lesson_id)
    completed_ids = {p.exercise_id for p in Progress.query.filter_by(user_id=user_id, completed=True)}
    saved_code = {p.exercise_id: p.last_code for p in Progress.query.filter_by(user_id=user_id) if p.last_code}

    data = lesson.to_dict(include_exercises=True)
    for ex in data["exercises"]:
        ex["completed"] = ex["id"] in completed_ids
        if ex["id"] in saved_code:
            ex["starter_code"] = saved_code[ex["id"]]
    return jsonify(data), 200


@app.route("/api/progress", methods=["GET"])
@jwt_required()
def get_progress():
    user_id = int(get_jwt_identity())
    return jsonify({
        "total": Exercise.query.count(),
        "completed": Progress.query.filter_by(user_id=user_id, completed=True).count(),
    }), 200

# ── Routes: Streak ────────────────────────────────────────────────────────────

@app.route("/api/streak", methods=["GET"])
@jwt_required()
def get_streak():
    user_id = int(get_jwt_identity())
    streak = Streak.query.filter_by(user_id=user_id).first()
    if not streak:
        streak = Streak(user_id=user_id, current_streak=0, longest_streak=0)
        db.session.add(streak)
        db.session.commit()
    return jsonify({
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "last_activity": streak.last_activity_date.isoformat() if streak.last_activity_date else None,
    }), 200

@app.route("/api/streak/update", methods=["POST"])
@jwt_required()
def update_streak():
    user_id = int(get_jwt_identity())
    streak = Streak.query.filter_by(user_id=user_id).first()
    if not streak:
        streak = Streak(user_id=user_id, current_streak=1, longest_streak=1, last_activity_date=datetime.now())
        db.session.add(streak)
    else:
        last_activity = streak.last_activity_date
        today = datetime.now().date()
        if last_activity:
            last_date = last_activity.date()
            if last_date == today:
                pass  # Already counted today
            elif (today - last_date).days == 1:
                streak.current_streak += 1
                if streak.current_streak > streak.longest_streak:
                    streak.longest_streak = streak.current_streak
            else:
                streak.current_streak = 1  # Reset streak
        else:
            streak.current_streak = 1
        streak.last_activity_date = datetime.now()
    db.session.commit()
    return jsonify({"current_streak": streak.current_streak, "longest_streak": streak.longest_streak}), 200

# ── Routes: Achievements ──────────────────────────────────────────────────────

@app.route("/api/achievements", methods=["GET"])
@jwt_required()
def get_achievements():
    user_id = int(get_jwt_identity())
    achievements = Achievement.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "badge_id": a.badge_id,
        "badge_name": a.badge_name,
        "badge_icon": a.badge_icon,
        "description": a.description,
        "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None,
    } for a in achievements]), 200

def check_and_unlock_achievements(user_id):
    """Check if user earned any new achievements"""
    completed = Progress.query.filter_by(user_id=user_id, completed=True).count()
    total_lessons = Lesson.query.count()
    completed_lessons = 0
    for lesson in Lesson.query.all():
        lesson_exercises = Exercise.query.filter_by(lesson_id=lesson.id).count()
        lesson_completed = Progress.query.filter_by(lesson_id=lesson.id, user_id=user_id, completed=True).count()
        if lesson_completed == lesson_exercises:
            completed_lessons += 1

    unlocked = []

    if completed == 1:
        unlocked.append("first_exercise")
    if completed == 10:
        unlocked.append("10_exercises")
    if completed == 50:
        unlocked.append("50_exercises")
    if completed == 100:
        unlocked.append("100_exercises")
    if completed_lessons == 1:
        unlocked.append("first_lesson")
    if completed_lessons == total_lessons:
        unlocked.append("all_lessons")

    for badge_id in unlocked:
        existing = Achievement.query.filter_by(user_id=user_id, badge_id=badge_id).first()
        if not existing:
            badge = next((b for b in ACHIEVEMENTS if b["badge_id"] == badge_id), None)
            if badge:
                achievement = Achievement(
                    user_id=user_id,
                    badge_id=badge_id,
                    badge_name=badge["name"],
                    badge_icon=badge["icon"],
                    description=badge["description"],
                    unlocked_at=datetime.now()
                )
                db.session.add(achievement)
    db.session.commit()

# ── Routes: Projects ──────────────────────────────────────────────────────────

@app.route("/api/projects", methods=["GET"])
@jwt_required()
def get_projects():
    user_id = int(get_jwt_identity())
    projects = Project.query.all()
    result = []
    for project in projects:
        project_data = project.to_dict()
        project_data["completed_count"] = ProjectProgress.query.join(
            ProjectExercise, ProjectProgress.project_exercise_id == ProjectExercise.id
        ).filter(
            ProjectExercise.project_id == project.id,
            ProjectProgress.user_id == user_id,
            ProjectProgress.completed == True
        ).count()
        result.append(project_data)
    return jsonify(result), 200

@app.route("/api/projects/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    user_id = int(get_jwt_identity())
    project = Project.query.get_or_404(project_id)
    project_data = project.to_dict(include_exercises=True)
    project_data["completed_count"] = ProjectProgress.query.join(
        ProjectExercise
    ).filter(
        ProjectExercise.project_id == project_id,
        ProjectProgress.user_id == user_id,
        ProjectProgress.completed == True
    ).count()
    return jsonify(project_data), 200

@app.route("/api/projects/<int:project_id>/exercises/<int:exercise_id>/submit", methods=["POST"])
@jwt_required()
def submit_project_exercise(project_id, exercise_id):
    user_id = int(get_jwt_identity())
    code = request.json.get("code", "")

    result = run_code(code)

    if result["code"] == 0:
        progress = ProjectProgress.query.filter_by(
            user_id=user_id,
            project_exercise_id=exercise_id
        ).first()
        if not progress:
            progress = ProjectProgress(
                user_id=user_id,
                project_exercise_id=exercise_id,
                completed=True,
                completed_at=datetime.now()
            )
            db.session.add(progress)
        else:
            progress.completed = True
            progress.completed_at = datetime.now()
        db.session.commit()

    return jsonify(result), 200

# ── Routes: Code ──────────────────────────────────────────────────────────────

def run_code(code):
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmp = f.name
        result = subprocess.run(
            [sys.executable, tmp],
            capture_output=True, text=True, timeout=10
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Execution timed out (10s limit).", "code": 1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "code": 1}
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass


@app.route("/api/run", methods=["POST"])
@jwt_required()
def run():
    code = request.get_json().get("code", "")
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400
    return jsonify(run_code(code)), 200


@app.route("/api/submit/<int:exercise_id>", methods=["POST"])
@jwt_required()
def submit(exercise_id):
    user_id = int(get_jwt_identity())
    code = request.get_json().get("code", "")
    exercise = Exercise.query.get_or_404(exercise_id)
    result = run_code(code)

    passed = False
    feedback = ""

    if result["code"] != 0:
        feedback = result["stderr"] or "Runtime error"
    elif exercise.expected_output:
        actual = result["stdout"].strip()
        expected = exercise.expected_output.strip()
        passed = actual == expected
        feedback = "Correct! Well done." if passed else f"Output didn't match.\nExpected:\n{expected}\n\nGot:\n{actual}"
    else:
        passed = True
        feedback = "Looks good! No errors."

    progress = Progress.query.filter_by(user_id=user_id, exercise_id=exercise_id).first()
    if not progress:
        progress = Progress(user_id=user_id, exercise_id=exercise_id)
        db.session.add(progress)

    progress.last_code = code
    if passed and not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"passed": passed, "feedback": feedback, "stdout": result["stdout"], "stderr": result["stderr"]}), 200

# ── Init ──────────────────────────────────────────────────────────────────────

def seed_db():
    # Seed lessons
    if Lesson.query.count() != len(CURRICULUM):
        Exercise.query.delete()
        Lesson.query.delete()
        db.session.commit()
        for lesson_data in CURRICULUM:
            exercises = lesson_data.pop("exercises")
            lesson = Lesson(**lesson_data)
            db.session.add(lesson)
            db.session.flush()
            for ex_data in exercises:
                db.session.add(Exercise(lesson_id=lesson.id, **ex_data))
            lesson_data["exercises"] = exercises  # restore
        db.session.commit()
        print("[OK] Database seeded with lessons.")

    # Seed projects
    if Project.query.count() != len(PROJECTS):
        ProjectExercise.query.delete()
        Project.query.delete()
        db.session.commit()
        for proj_data in PROJECTS:
            exercises = proj_data.pop("exercises")
            project = Project(**proj_data)
            db.session.add(project)
            db.session.flush()
            for ex_data in exercises:
                db.session.add(ProjectExercise(project_id=project.id, **ex_data))
            proj_data["exercises"] = exercises  # restore
        db.session.commit()
        print("[OK] Database seeded with projects.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_db()
    print("\n Server running at http://localhost:5000")
    print(" Frontend should run at http://localhost:3000\n")
    app.run(debug=True, port=5000)
