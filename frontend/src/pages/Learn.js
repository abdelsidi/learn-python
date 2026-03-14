import React, { useState } from "react";
import axios from "axios";
import { useLanguage } from "../context/LanguageContext";
import { translations } from "../translations";
import API_URL from "../config";

const s = {
  page: { display: "grid", gridTemplateColumns: "280px 1fr", gap: "2rem", maxWidth: "1400px", margin: "0 auto", padding: "2rem", minHeight: "calc(100vh - 60px)" },

  // Sidebar
  sidebar: { background: "#1e293b", borderRadius: "12px", padding: "1.5rem", border: "1px solid #334155", height: "fit-content", position: "sticky", top: "80px" },
  sidebarTitle: { fontSize: "0.9rem", fontWeight: "700", color: "#94a3b8", textTransform: "uppercase", marginBottom: "1rem" },
  chapterList: { display: "flex", flexDirection: "column", gap: "0.5rem" },
  chapterItem: { padding: "0.75rem", borderRadius: "6px", cursor: "pointer", fontSize: "0.9rem", transition: "all 0.2s", border: "1px solid transparent" },
  chapterActive: { background: "#3b82f6", color: "#fff", borderColor: "#3b82f6" },
  chapterInactive: { color: "#cbd5e1", hover: { background: "#334155" } },

  // Main Content
  content: { background: "#0f172a", borderRadius: "12px", padding: "2.5rem", border: "1px solid #334155" },
  header: { marginBottom: "2rem", paddingBottom: "2rem", borderBottom: "1px solid #334155" },
  chapterNum: { fontSize: "0.85rem", color: "#3b82f6", fontWeight: "700", textTransform: "uppercase", marginBottom: "0.5rem" },
  title: { fontSize: "2rem", fontWeight: "700", marginBottom: "0.5rem" },
  subtitle: { color: "#94a3b8", fontSize: "1rem" },

  // Content Sections
  section: { marginBottom: "2.5rem" },
  sectionTitle: { fontSize: "1.3rem", fontWeight: "700", marginBottom: "1rem", color: "#e2e8f0" },
  paragraph: { color: "#cbd5e1", fontSize: "0.95rem", lineHeight: "1.8", marginBottom: "1rem" },

  // Code Examples
  codeBlock: { background: "#1e293b", borderRadius: "8px", border: "1px solid #334155", padding: "1.25rem", marginBottom: "1.5rem", overflow: "auto" },
  codeLabel: { fontSize: "0.8rem", color: "#94a3b8", fontWeight: "700", marginBottom: "0.75rem", textTransform: "uppercase" },
  code: { fontFamily: "monospace", fontSize: "0.9rem", color: "#e2e8f0", whiteSpace: "pre-wrap", wordBreak: "break-word" },

  // Output Box
  outputBox: { background: "#0f172a", borderRadius: "8px", border: "1px solid #22c55e", padding: "1rem", marginTop: "0.5rem", marginBottom: "1.5rem" },
  outputLabel: { fontSize: "0.8rem", color: "#4ade80", fontWeight: "700", marginBottom: "0.5rem" },
  output: { fontFamily: "monospace", fontSize: "0.9rem", color: "#4ade80" },

  // Concept Box
  conceptBox: { background: "#1e3a5f", borderLeft: "4px solid #3b82f6", padding: "1rem", borderRadius: "6px", marginBottom: "1.5rem" },
  conceptTitle: { color: "#60a5fa", fontWeight: "700", marginBottom: "0.5rem" },
  conceptText: { color: "#cbd5e1", fontSize: "0.9rem", lineHeight: "1.6" },

  // Tips
  tipBox: { background: "#4d2e3b", borderLeft: "4px solid #f472b6", padding: "1rem", borderRadius: "6px", marginBottom: "1.5rem" },
  tipTitle: { color: "#f472b6", fontWeight: "700", marginBottom: "0.5rem" },
  tipText: { color: "#cbd5e1", fontSize: "0.9rem", lineHeight: "1.6" },

  // Try It Button
  runBtn: { background: "#22c55e", color: "#fff", border: "none", padding: "0.6rem 1.25rem", borderRadius: "6px", fontWeight: "600", cursor: "pointer", fontSize: "0.9rem", marginTop: "0.5rem" },
};

const getTranslation = (lang, key) => {
  const keys = key.split(".");
  let value = translations[lang] || translations.en;
  for (let k of keys) {
    value = value[k];
    if (!value) return key;
  }
  return value;
};

const chapters = [
  {
    id: 1,
    num: (lang) => getTranslation(lang, "chapter") + " 1",
    titleKey: "ch1_title",
    subtitleKey: "ch1_subtitle",
    content: `
      Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991, Python emphasizes code readability and allows programmers to express concepts in fewer lines of code.

      ## Why Learn Python?

      • **Easy to Learn**: Simple syntax similar to English
      • **Versatile**: Used in web development, data science, AI, automation, and more
      • **Large Community**: Millions of developers and extensive libraries
      • **Industry Demand**: Top companies use Python (Google, Facebook, Netflix, etc.)
      • **Career Growth**: One of the most in-demand programming skills

      ## Common Use Cases

      • Data Analysis and Visualization
      • Machine Learning and AI
      • Web Development (Django, Flask)
      • Automation and Scripting
      • Scientific Computing
      • Game Development
    `,
  },
  {
    id: 2,
    num: "Chapter 2",
    title: "Variables and Data Types",
    subtitle: "Storing and working with data",
    content: `
      A variable is a container for storing data. Think of it as a labeled box where you put information.

      ## Creating Variables

      Variables are created by assigning a value to a name. Python automatically detects the data type.
    `,
    example1: `name = "Alice"
age = 25
height = 5.6
is_student = True

print(name)
print(age)
print(height)
print(is_student)`,
    example1Output: `Alice
25
5.6
True`,

    concept1Title: "Data Types",
    concept1: `Python has several built-in data types:
• str: Text ("Hello World")
• int: Whole numbers (42)
• float: Decimal numbers (3.14)
• bool: True or False`,

    example2: `# Check the data type with type()
x = 10
y = 3.14
z = "Python"

print(type(x))
print(type(y))
print(type(z))`,
    example2Output: `<class 'int'>
<class 'float'>
<class 'str'>`,

    tip: `Variable names should be descriptive. Use snake_case (my_variable) instead of camelCase. Avoid using Python keywords like 'if', 'for', 'while' as variable names.`,
  },
  {
    id: 3,
    num: "Chapter 3",
    title: "Basic Operations",
    subtitle: "Math, strings, and logical operations",
    content: `
      Operations allow you to manipulate data. Python supports arithmetic, string, and logical operations.

      ## Arithmetic Operations
    `,
    example1: `# Basic math
x = 10
y = 3

print(x + y)      # Addition: 13
print(x - y)      # Subtraction: 7
print(x * y)      # Multiplication: 30
print(x / y)      # Division: 3.333...
print(x // y)     # Floor Division: 3
print(x % y)      # Modulo (remainder): 1
print(x ** y)     # Exponent: 1000`,
    example1Output: `13
7
30
3.3333333333333335
3
1
1000`,

    concept1Title: "String Operations",
    concept1: `You can concatenate (join) strings and repeat them:
• "Hello" + " " + "World" = "Hello World"
• "Ha" * 3 = "HaHaHa"
• len("Python") = 6`,

    example2: `# String operations
greeting = "Hello"
name = "World"

print(greeting + " " + name)
print("!" * 5)
print(len("Python"))`,
    example2Output: `Hello World
!!!!!
6`,
  },
  {
    id: 4,
    num: "Chapter 4",
    title: "Input and Output",
    subtitle: "Getting user input and displaying output",
    content: `
      Output shows information to the user. Input gets information from the user.

      ## The print() Function

      print() displays text or values to the console.
    `,
    example1: `# Different ways to print
print("Hello, World!")
print(42)
print(3.14)
print("Name:", "Alice", "Age:", 25)`,
    example1Output: `Hello, World!
42
3.14
Name: Alice Age: 25`,

    concept1Title: "Getting User Input",
    concept1: `input() function pauses the program and waits for the user to type something. Always returns a string, so convert if needed:
• name = input("What is your name? ")
• age = int(input("What is your age? "))`,

    example2: `# Getting user input
name = input("What is your name? ")
age = input("What is your age? ")
print(f"Hello {name}, you are {age} years old!")`,
    example2Output: `What is your name? Alice
What is your age? 25
Hello Alice, you are 25 years old!`,

    tip: `Use f-strings (formatted string literals) for clean output: f"Hello {name}" instead of "Hello " + name. f-strings are more readable and efficient.`,
  },
  {
    id: 5,
    num: "Chapter 5",
    title: "Conditional Statements",
    subtitle: "Making decisions in your code",
    content: `
      Conditional statements allow your code to make decisions. They execute different code based on conditions.

      ## if, elif, else
    `,
    example1: `# Simple if statement
age = 18

if age >= 18:
    print("You are an adult")
else:
    print("You are a minor")`,
    example1Output: `You are an adult`,

    concept1Title: "Comparison Operators",
    concept1: `Used in conditions:
• == : Equal to
• != : Not equal to
• > : Greater than
• < : Less than
• >= : Greater than or equal
• <= : Less than or equal`,

    example2: `# Multiple conditions with elif
score = 85

if score >= 90:
    print("Grade: A")
elif score >= 80:
    print("Grade: B")
elif score >= 70:
    print("Grade: C")
else:
    print("Grade: F")`,
    example2Output: `Grade: B`,

    example3: `# Logical operators (and, or, not)
age = 25
is_citizen = True

if age >= 18 and is_citizen:
    print("You can vote!")
else:
    print("You cannot vote")`,
    example3Output: `You can vote!`,
  },
  {
    id: 6,
    num: "Chapter 6",
    title: "Loops",
    subtitle: "Repeating code multiple times",
    content: `
      Loops allow you to repeat code without writing it multiple times.

      ## for Loop
    `,
    example1: `# Loop through a range
for i in range(5):
    print(i)`,
    example1Output: `0
1
2
3
4`,

    concept1Title: "while Loop",
    concept1: `Repeats while a condition is true:
while condition:
    # code here
    # update condition`,

    example2: `# while loop
count = 0
while count < 3:
    print(f"Count: {count}")
    count = count + 1`,
    example2Output: `Count: 0
Count: 1
Count: 2`,

    example3: `# Loop through a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)`,
    example3Output: `apple
banana
cherry`,

    tip: `Use break to exit a loop early, and continue to skip to the next iteration. Learn when to use for vs while: use for for known iterations, while for unknown durations.`,
  },
];

export default function Learn() {
  const [activeChapter, setActiveChapter] = useState(1);
  const [results, setResults] = useState({});
  const { language } = useLanguage();

  const chapter = chapters.find(c => c.id === activeChapter);

  const t = (key) => getTranslation(language, key);

  const runCode = async (code, exampleId) => {
    try {
      const response = await axios.post(`${API_URL}/api/run`, { code });
      setResults(prev => ({
        ...prev,
        [exampleId]: response.data.stdout
      }));
    } catch (error) {
      setResults(prev => ({
        ...prev,
        [exampleId]: "Error: " + error.message
      }));
    }
  };

  return (
    <div style={s.page}>
      {/* Sidebar */}
      <div style={{ ...s.sidebar, direction: language === "ar" ? "rtl" : "ltr" }}>
        <div style={s.sidebarTitle}>📚 {t("chapters")}</div>
        <div style={s.chapterList}>
          {chapters.map(ch => (
            <div
              key={ch.id}
              style={{
                ...s.chapterItem,
                ...(activeChapter === ch.id ? s.chapterActive : {}),
              }}
              onClick={() => setActiveChapter(ch.id)}
              onMouseOver={e => !activeChapter === ch.id && (e.target.style.background = "#334155")}
              onMouseOut={e => !activeChapter === ch.id && (e.target.style.background = "transparent")}
            >
              {t("chapter")} {ch.id}
            </div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ ...s.content, direction: language === "ar" ? "rtl" : "ltr" }}>
        <div style={s.header}>
          <div style={s.chapterNum}>{t("chapter")} {chapter.id}</div>
          <h1 style={s.title}>{chapter.title}</h1>
          <p style={s.subtitle}>{chapter.subtitle}</p>
        </div>

        {/* Chapter Content */}
        {chapter.content.split('\n').map((line, idx) => {
          if (line.startsWith('## ')) {
            return <h2 key={idx} style={s.sectionTitle}>{line.replace('## ', '')}</h2>;
          } else if (line.startsWith('• ')) {
            return <p key={idx} style={{ ...s.paragraph, marginLeft: '1.5rem' }}>• {line.replace('• ', '')}</p>;
          } else if (line.trim()) {
            return <p key={idx} style={s.paragraph}>{line}</p>;
          }
          return null;
        })}

        {/* Example 1 */}
        {chapter.example1 && (
          <div style={s.section}>
            <div style={s.codeBlock}>
              <div style={s.codeLabel}>{t("example")}</div>
              <pre style={s.code}>{chapter.example1}</pre>
            </div>
            <button style={s.runBtn} onClick={() => runCode(chapter.example1, 'ex1')}>
              ▶ {t("runCode")}
            </button>
            {results.ex1 && (
              <div style={s.outputBox}>
                <div style={s.outputLabel}>{t("output")}</div>
                <pre style={s.output}>{results.ex1}</pre>
              </div>
            )}
          </div>
        )}

        {/* Concept 1 */}
        {chapter.concept1 && (
          <div style={s.conceptBox}>
            <div style={s.conceptTitle}>💡 {chapter.concept1Title}</div>
            {chapter.concept1.split('\n').map((line, idx) => (
              <div key={idx} style={s.conceptText}>
                {line}
              </div>
            ))}
          </div>
        )}

        {/* Example 2 */}
        {chapter.example2 && (
          <div style={s.section}>
            <div style={s.codeBlock}>
              <div style={s.codeLabel}>Example</div>
              <pre style={s.code}>{chapter.example2}</pre>
            </div>
            <button style={s.runBtn} onClick={() => runCode(chapter.example2, 'ex2')}>
              ▶ Run Code
            </button>
            {results.ex2 && (
              <div style={s.outputBox}>
                <div style={s.outputLabel}>Output:</div>
                <pre style={s.output}>{results.ex2}</pre>
              </div>
            )}
          </div>
        )}

        {/* Example 3 */}
        {chapter.example3 && (
          <div style={s.section}>
            <div style={s.codeBlock}>
              <div style={s.codeLabel}>Example</div>
              <pre style={s.code}>{chapter.example3}</pre>
            </div>
            <button style={s.runBtn} onClick={() => runCode(chapter.example3, 'ex3')}>
              ▶ Run Code
            </button>
            {results.ex3 && (
              <div style={s.outputBox}>
                <div style={s.outputLabel}>Output:</div>
                <pre style={s.output}>{results.ex3}</pre>
              </div>
            )}
          </div>
        )}

        {/* Tip */}
        {chapter.tip && (
          <div style={s.tipBox}>
            <div style={s.tipTitle}>💬 Pro Tip</div>
            <div style={s.tipText}>{chapter.tip}</div>
          </div>
        )}
      </div>
    </div>
  );
}
