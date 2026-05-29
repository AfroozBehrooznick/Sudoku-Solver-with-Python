# Sudoku Solver 🧩

A Python-based Sudoku Solver that combines Constraint Satisfaction Problems (CSP) techniques with classic AI search algorithms to solve Sudoku puzzles efficiently.

This project supports multiple solving strategies, visualization of the solving process, performance tracking, and flexible puzzle input methods — making it useful both for learning AI concepts and experimenting with search algorithms.

A web based version of this project is also available here:
[https://github.com/AfroozBehrooznick/Sudoku-Solver-Web-Edition]

---

## ✨ Features

✅ Multiple AI solving algorithms

✅ CSP with Arc Consistency (AC-3)

✅ Backtracking + Forward Checking + MRV heuristic

✅ Local Search using Min-Conflicts

✅ Step-by-step visualization mode

✅ Performance measurement

Execution time

Peak memory usage


✅ Multiple input methods

Predefined puzzles

Manual input

Read from file


✅ Clean console-based UI

✅ Handles invalid input safely



---

## 🧠 Algorithms Implemented

1. CSP + Arc Consistency (AC-3)

Uses constraint propagation to reduce domains before and during search.

Techniques used:

Arc Consistency (AC-3)

Recursive Backtracking

MRV (Minimum Remaining Values)


Best for:

Fast and reliable solving

Difficult puzzles



---

2. Backtracking + Forward Checking + MRV

Classic CSP-based solver using:

Recursive backtracking

Forward checking

MRV heuristic


Best for:

Understanding traditional CSP solving

Educational purposes



---

3. Min-Conflicts Local Search

A local search approach that:

Randomly initializes the board

Minimizes conflicts through swaps

Uses random walk to escape local minima


Best for:

Demonstrating heuristic local search

AI experimentation



---

## 📂 Project Structure

Sudoku Solver.py

Everything is implemented in a single Python file for simplicity and portability.


---

## ▶️ How to Run

Make sure Python 3 is installed.

Run the program:

python "Sudoku Solver.py"


---

## 📥 Puzzle Input Methods

Predefined Puzzles

Choose from:

Easy

Hard

Evil



---

Manual Input

Enter an 81-character Sudoku string.

Example:

003020600900305001001806400008102900700000008006708200002609500800203009005010300

Use:

0 or . for empty cells.



---

Read From File

Create a .txt file containing the puzzle string.

Example:

530070000600195000098000060800060003400803001700020006060000280000419005000080079

Then load it directly from the program.


---

##👀 Visualization Mode

Enable visualization to watch the solving process step-by-step.

Example:

Visualize the solving process? (y/n):

Useful for:

Learning search algorithms

Understanding CSP propagation

Demonstrations



---

## 📊 Performance Tracking

The solver automatically measures:

⏱ Execution Time

## 💾 Peak Memory Usage


Example output:

Algorithm:     CSP (Arc Consistency)
Time Taken:    0.00321 seconds
Peak Memory:   128.54 KB


---

## 🛠 Technologies Used

Python 3

CSP Techniques

AC-3 Constraint Propagation

MRV Heuristic

Forward Checking

Local Search

tracemalloc for memory tracking

---
### 👨‍💻 Author

Created by Afrooz Behrooznick
