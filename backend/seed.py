from app import create_app, db
from models import Lesson, Exercise

CURRICULUM = [
    {
        "title": "Python Basics",
        "description": "Variables, data types, and basic operations",
        "order": 1,
        "exercises": [
            {
                "title": "Hello World",
                "description": "Print `Hello, World!` to the screen.",
                "starter_code": "# Write your code here\n",
                "expected_output": "Hello, World!",
                "hint": "Use the print() function with the exact text inside quotes.",
                "order": 1,
            },
            {
                "title": "Variables",
                "description": "Create a variable called `name` with the value `Python`, then print it.",
                "starter_code": "# Create a variable and print it\n",
                "expected_output": "Python",
                "hint": "name = 'Python' then print(name)",
                "order": 2,
            },
            {
                "title": "Basic Math",
                "description": "Calculate and print the result of `15 + 27`.",
                "starter_code": "# Print the sum of 15 and 27\n",
                "expected_output": "42",
                "hint": "print(15 + 27)",
                "order": 3,
            },
            {
                "title": "String Concatenation",
                "description": 'Create two variables: `first = "Hello"` and `second = "World"`, then print them joined with a space.',
                "starter_code": 'first = "Hello"\nsecond = "World"\n# Print them joined with a space\n',
                "expected_output": "Hello World",
                "hint": 'print(first + " " + second)',
                "order": 4,
            },
        ],
    },
    {
        "title": "Control Flow",
        "description": "if/else statements and loops",
        "order": 2,
        "exercises": [
            {
                "title": "If/Else",
                "description": "Given `x = 10`, print `positive` if x > 0, otherwise print `non-positive`.",
                "starter_code": "x = 10\n# Check if x is positive\n",
                "expected_output": "positive",
                "hint": "Use if x > 0: print('positive') else: print('non-positive')",
                "order": 1,
            },
            {
                "title": "For Loop",
                "description": "Print numbers 1 through 5, each on its own line.",
                "starter_code": "# Use a for loop\n",
                "expected_output": "1\n2\n3\n4\n5",
                "hint": "for i in range(1, 6): print(i)",
                "order": 2,
            },
            {
                "title": "While Loop",
                "description": "Use a while loop to print `count: 0`, `count: 1`, `count: 2`.",
                "starter_code": "count = 0\n# Use a while loop\n",
                "expected_output": "count: 0\ncount: 1\ncount: 2",
                "hint": "while count < 3: print('count:', count); count += 1",
                "order": 3,
            },
            {
                "title": "FizzBuzz",
                "description": "For numbers 1 to 15, print `Fizz` if divisible by 3, `Buzz` if by 5, `FizzBuzz` if both, else the number.",
                "starter_code": "# FizzBuzz from 1 to 15\n",
                "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz",
                "hint": "Check divisibility by 15 first, then 3, then 5.",
                "order": 4,
            },
        ],
    },
    {
        "title": "Functions",
        "description": "Defining and calling functions",
        "order": 3,
        "exercises": [
            {
                "title": "Define a Function",
                "description": "Define a function `greet()` that prints `Hello from a function!`, then call it.",
                "starter_code": "# Define and call greet()\n",
                "expected_output": "Hello from a function!",
                "hint": "def greet(): print('Hello from a function!')\ngreet()",
                "order": 1,
            },
            {
                "title": "Function with Parameters",
                "description": "Define `add(a, b)` that returns a + b. Print `add(3, 4)`.",
                "starter_code": "# Define add(a, b) and print the result\n",
                "expected_output": "7",
                "hint": "def add(a, b): return a + b\nprint(add(3, 4))",
                "order": 2,
            },
            {
                "title": "Default Parameters",
                "description": "Define `power(base, exp=2)` that returns base**exp. Print `power(3)` and `power(2, 3)`.",
                "starter_code": "# Define power() with a default exponent\n",
                "expected_output": "9\n8",
                "hint": "def power(base, exp=2): return base**exp",
                "order": 3,
            },
            {
                "title": "Recursive Function",
                "description": "Define `factorial(n)` recursively. Print `factorial(5)`.",
                "starter_code": "# Define factorial(n) recursively\n",
                "expected_output": "120",
                "hint": "Base case: if n <= 1 return 1. Else return n * factorial(n-1).",
                "order": 4,
            },
        ],
    },
    {
        "title": "Data Structures",
        "description": "Lists, dictionaries, tuples, and sets",
        "order": 4,
        "exercises": [
            {
                "title": "Lists",
                "description": "Create a list `fruits = ['apple', 'banana', 'cherry']` and print each item on a new line.",
                "starter_code": "fruits = ['apple', 'banana', 'cherry']\n# Print each fruit\n",
                "expected_output": "apple\nbanana\ncherry",
                "hint": "Use a for loop: for fruit in fruits: print(fruit)",
                "order": 1,
            },
            {
                "title": "List Methods",
                "description": "Start with `nums = [3, 1, 4, 1, 5]`. Append 9, sort it, then print it.",
                "starter_code": "nums = [3, 1, 4, 1, 5]\n# Append 9, sort, print\n",
                "expected_output": "[1, 1, 3, 4, 5, 9]",
                "hint": "nums.append(9); nums.sort(); print(nums)",
                "order": 2,
            },
            {
                "title": "Dictionaries",
                "description": 'Create `person = {"name": "Alice", "age": 25}` and print `name: Alice` and `age: 25`.',
                "starter_code": 'person = {"name": "Alice", "age": 25}\n# Print each key-value pair\n',
                "expected_output": "name: Alice\nage: 25",
                "hint": "for key, val in person.items(): print(f'{key}: {val}')",
                "order": 3,
            },
            {
                "title": "Sets",
                "description": "Create `a = {1,2,3,4}` and `b = {3,4,5,6}`. Print their intersection.",
                "starter_code": "a = {1, 2, 3, 4}\nb = {3, 4, 5, 6}\n# Print the intersection\n",
                "expected_output": "{3, 4}",
                "hint": "print(a & b) or print(a.intersection(b))",
                "order": 4,
            },
        ],
    },
    {
        "title": "Object-Oriented Programming",
        "description": "Classes, objects, and inheritance",
        "order": 5,
        "exercises": [
            {
                "title": "Create a Class",
                "description": "Create a class `Dog` with a method `bark()` that prints `Woof!`. Create a `Dog` instance and call `bark()`.",
                "starter_code": "# Define the Dog class\n",
                "expected_output": "Woof!",
                "hint": "class Dog:\n    def bark(self): print('Woof!')\ndog = Dog()\ndog.bark()",
                "order": 1,
            },
            {
                "title": "Constructor",
                "description": "Create class `Person` with `__init__(self, name, age)`. Print `Alice is 30 years old.`",
                "starter_code": "# Define Person with __init__\n",
                "expected_output": "Alice is 30 years old.",
                "hint": "class Person:\n    def __init__(self, name, age): self.name=name; self.age=age",
                "order": 2,
            },
            {
                "title": "Inheritance",
                "description": "Create `Animal` with `speak()` printing `...`, and `Cat` extending `Animal` overriding `speak()` to print `Meow!`. Call `Cat().speak()`.",
                "starter_code": "# Define Animal and Cat\n",
                "expected_output": "Meow!",
                "hint": "class Cat(Animal):\n    def speak(self): print('Meow!')",
                "order": 3,
            },
        ],
    },
    {
        "title": "Error Handling",
        "description": "try/except and raising exceptions",
        "order": 6,
        "exercises": [
            {
                "title": "Try/Except",
                "description": "Try to convert `'abc'` to int. Catch the ValueError and print `Invalid number`.",
                "starter_code": "# Try to convert 'abc' to int\n",
                "expected_output": "Invalid number",
                "hint": "try:\n    int('abc')\nexcept ValueError:\n    print('Invalid number')",
                "order": 1,
            },
            {
                "title": "Finally",
                "description": "Use try/except/finally. Try `10 / 0`, print `Error` in except, print `Done` in finally.",
                "starter_code": "# Use try/except/finally\n",
                "expected_output": "Error\nDone",
                "hint": "try:\n    10/0\nexcept:\n    print('Error')\nfinally:\n    print('Done')",
                "order": 2,
            },
            {
                "title": "Raise Exception",
                "description": "Define `check_age(age)` that raises `ValueError('Too young')` if age < 18. Catch it and print the message.",
                "starter_code": "# Define check_age and test it\n",
                "expected_output": "Too young",
                "hint": "def check_age(age):\n    if age < 18: raise ValueError('Too young')\ntry:\n    check_age(15)\nexcept ValueError as e:\n    print(e)",
                "order": 3,
            },
        ],
    },
]


def seed():
    app = create_app()
    with app.app_context():
        # Clear existing data
        Exercise.query.delete()
        Lesson.query.delete()
        db.session.commit()

        for lesson_data in CURRICULUM:
            exercises = lesson_data.pop("exercises")
            lesson = Lesson(**lesson_data)
            db.session.add(lesson)
            db.session.flush()

            for ex_data in exercises:
                ex = Exercise(lesson_id=lesson.id, **ex_data)
                db.session.add(ex)

        db.session.commit()
        print(f"Seeded {len(CURRICULUM)} lessons successfully.")


if __name__ == "__main__":
    seed()
