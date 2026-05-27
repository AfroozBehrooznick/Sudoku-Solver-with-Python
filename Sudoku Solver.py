# Sudoku Solver (CSP + AC3, Backtracking + MRV , Local Search)
# Created By Afrooz Behrooznick

import sys
import time
import random
import copy
import os
import tracemalloc

DIGITS = '123456789'
ROWS = 'ABCDEFGHI'
COLS = DIGITS

def cross(A, B):
    return [a+b for a in A for b in B]

# All 81 squares
SQUARES = cross(ROWS, COLS)

# All units - rows, columns, and 3x3 square
UNITLIST = ([cross(ROWS, c) for c in COLS] +
            [cross(r, COLS) for r in ROWS] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])

# Map each square to its units
UNITS = dict((s, [u for u in UNITLIST if s in u]) for s in SQUARES)

# Check each square to its neighbour - in same row, column, or box
PEERS = dict((s, set(sum(UNITS[s],[])) - set([s])) for s in SQUARES)

def gridValues(grid):
    #Convert grid string into dictionary
    chars = [c for c in grid if c in DIGITS or c in '0.']
    if len(chars) != 81:
        return None
    return dict(zip(SQUARES, chars))

def display(values):
    #For print
    if not values:
        print("Empty Grid")
        return
    
    if isinstance(values, list):
        if isinstance(values[0], list):
            flat = [str(val) if val != 0 else '.' for row in values for val in row]
            values = dict(zip(SQUARES, flat))
        else:
            values = dict(zip(SQUARES, values))
    
    width = 1 + max(len(values[s]) for s in SQUARES)
    line = '+'.join(['-'*(width*3)]*3)
    for r in ROWS:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in COLS))
        if r in 'CF': 
            print(line)
    print()


def visualizeStep(values, algo_name, step_num=None):
    #For visualization
    if step_num is not None:
        print(f"--- Solving with {algo_name} (Step {step_num}) ---")
    else:
        print(f"--- Solving with {algo_name} ---")
    display(values)
    time.sleep(0.05)



# 1.CSP WITH ARC CONSISTENCY (AC-3)
def solveCspAC3(gridStr, visualize=False):
    #Solve Sudoku using AC-3
    
    values = dict((s, DIGITS) for s in SQUARES)
    gridDict = gridValues(gridStr)
    if not gridDict:
        return False
    
    for s, d in gridDict.items():
        if d in DIGITS:
            if not assign(values, s, d, visualize):
                return False
    
    # Start search
    return searchCsp(values, visualize, 0)

def assign(values, s, d, visualize=False):
    #Assign value d to square s and remove it from peers
    otherValues = values[s].replace(d, '')
    if all(remoove(values, s, d2, visualize) for d2 in otherValues):
        return values
    else:
        return False


def remoove(values, s, d, visualize=False):
    #Remove digit d from values[s] and apply Arc Consistency
    if d not in values[s]:
        return values
    
    values[s] = values[s].replace(d, '')
    
    # If square has no values left then fail
    if len(values[s]) == 0:
        return False
    # If square reduced to one value, remove that value from peers
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(remoove(values, s2, d2, visualize) for s2 in PEERS[s]):
            return False
            
    # Check if a unit has only one place for value d
    for u in UNITS[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False  # No place for d in this unit
        elif len(dplaces) == 1: # Only one place for d
            if not assign(values, dplaces[0], d, visualize):
                return False
    
    return values


def searchCsp(values, visualize, stepCount):
    #Choose the square with the fewest remaining values
    #Recursive search with backtracking for CSP and uses MRV
    if values is False:
        return False
    
    # Check if solved - all squares have exactly one value
    if all(len(values[s]) == 1 for s in SQUARES):
        return values
    
    # MRV heuristic that choose square with fewest remaining values
    unassigned = [(len(values[s]), s) for s in SQUARES if len(values[s]) > 1]
    if not unassigned:
        return False
    
    n, s = min(unassigned)
    
    # Try each possible value for the chosen square
    for d in values[s]:
        if visualize and stepCount % 50 == 0:
            visualizeStep(values, "CSP (Arc Consistency)", stepCount)
        
        result = searchCsp(assign(values.copy(), s, d, visualize), visualize, stepCount + 1)
        if result:
            return result
    
    return False


def solveBacktrackingFC(gridStr, visualize=False):
    # Solve using Backtracking with Forward Checking and MRV heuristic 
    gridDict = gridValues(gridStr)
    if not gridDict:
        return False
    
    # Initialize domains - filled cells have single value, empty cells have all 1-9
    domains = {}
    for s in SQUARES:
        if gridDict[s] in DIGITS:
            domains[s] = [int(gridDict[s])]
        else:
            domains[s] = list(range(1, 10))
    
    # Initial forward checking for fixed values
    for s in SQUARES:
        if len(domains[s]) == 1:
            val = domains[s][0]
            if not forwardCheck(domains, s, val):
                return False  # Invalid initial board
    
    return backtrackFC(domains, visualize, 0)

def forwardCheck(domains, square, value):
    # Remove value from domains of all peers
    for peer in PEERS[square]:
        if value in domains[peer]:
            domains[peer].remove(value)
            if len(domains[peer]) == 0:
                return False  
                
    return True


def backtrackFC(domains, visualize, stepCount):
    #Recursive backtracking with forward checking that uses MRV to select next variable to assign
    if all(len(domains[s]) == 1 for s in SQUARES): # Check if solved
        return {s: str(v[0]) for s, v in domains.items()}  # Convert to display format
    
    # MRV = choose variable with fewest remaining values
    unassigned = [s for s in SQUARES if len(domains[s]) > 1]
    if not unassigned:
        return False
    
    s = min(unassigned, key=lambda x: len(domains[x]))
    
    # Try each value in domain
    for val in list(domains[s]):  
        # Use list copy to avoid modification during iteration
        new_domains = copy.deepcopy(domains)
        new_domains[s] = [val]
        
        # Visualization
        if visualize and stepCount % 20 == 0:
            current_view = {k: (str(v[0]) if len(v) == 1 else '.') for k, v in new_domains.items()}
            visualizeStep(current_view, "Backtracking (FC + MRV)", stepCount)
        
        # Forward check
        if forwardCheck(new_domains, s, val):
            result = backtrackFC(new_domains, visualize, stepCount + 1)
            if result:
                return result
    
    return False


def solve_min_conflicts(gridStr, visualize=False, max_steps=100000):
    # Solve using Min-Conflicts local search algorithm - Initialize with valid rows, then swap to minimize conflicts.
    grid = []
    vals = [c for c in gridStr if c in DIGITS or c in '0.']
    if len(vals) != 81:
        return None
    
    fixed = []  # Store positions that cannot be changed
    for r in range(9):
        row_data = []
        for c in range(9):
            val = vals[r*9 + c]
            if val in '0.':
                row_data.append(0)
            else:
                row_data.append(int(val))
                fixed.append((r, c))
        grid.append(row_data)
    
    # Fill each row with missing numbers
    for r in range(9):
        current_row = grid[r]
        present = {x for x in current_row if x != 0}
        missing = list(set(range(1, 10)) - present)
        random.shuffle(missing)
        m_idx = 0
        for c in range(9):
            if grid[r][c] == 0:
                grid[r][c] = missing[m_idx]
                m_idx += 1
    
    current_conflicts = count_total_conflicts(grid)
    
    # Minimize conflicts
    for step in range(max_steps):
        if current_conflicts == 0:
            return grid  # Solved
        
        if visualize and step % 200 == 0: # Visualization
            visualizeStep(grid, f"Min-Conflicts", step)
        
        r = random.randint(0, 8) # Pick random row
        
        candidates = [c for c in range(9) if (r, c) not in fixed] # Pick two non fixed columns in this row
        if len(candidates) < 2:
            continue
        
        c1, c2 = random.sample(candidates, 2)
        
        prev_score = score_cell(grid, r, c1) + score_cell(grid, r, c2) # Calculate conflict change if we swap
        
        grid[r][c1], grid[r][c2] = grid[r][c2], grid[r][c1] # Try swap
        
        new_score = score_cell(grid, r, c1) + score_cell(grid, r, c2)
        
        # Min-conflicts: keep swap if it reduces conflicts -  Use random walk to escape local optima
        if new_score < prev_score:
            current_conflicts += (new_score - prev_score)
        else:
            if random.random() < 0.05:  # random walk probability
                current_conflicts += (new_score - prev_score)
            else:
                grid[r][c1], grid[r][c2] = grid[r][c2], grid[r][c1]  # Revert
    
    return None  # Failed to solve within max_steps

def count_total_conflicts(grid):
    #Count total conflicts in columns and 3x3 boxes
    conflicts = 0
    for c in range(9):
        col = [grid[r][c] for r in range(9)]
        conflicts += 9 - len(set(col))
    # Box conflicts
    for r in range(0, 9, 3):
        for c in range(0, 9, 3):
            block = [grid[i][j] for i in range(r, r+3) for j in range(c, c+3)]
            conflicts += 9 - len(set(block))
    return conflicts


def score_cell(grid, r, c):
    #Count conflicts for a specific cell "column , box , row" 
    val = grid[r][c]
    conflicts = 0
    for i in range(9): # Column check
        if i != r and grid[i][c] == val:
            conflicts += 1
    br, bc = (r // 3) * 3, (c // 3) * 3 # Box check
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if (i, j) != (r, c) and grid[i][j] == val:
                conflicts += 1
    return conflicts

PREDEFINED_PUZZLES = {
    '1': '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..',  # Easy
    '2': '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......',  # Hard
    '3': '8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..'   # Evil
}

def validate_input(choice, valid_options, exit_option='0'):
    # Validate user input and check for exit command 
    
    choice = choice.strip().upper()
    if choice == exit_option or choice == 'EXIT' or choice == 'Q':
        return False, True
    return choice in valid_options, False

def get_input_puzzle():
    # Get Sudoku puzzle from user   
    while True:
        print("\n-- INPUT METHOD SELECTION --")
        print("1. Select a Pre-defined Grid")
        print("2. Enter manually ~ String")
        print("3. Read from file")
        print("0. Exit")
        
        choice = input("Enter choice (0-3): ").strip()
        is_valid, should_exit = validate_input(choice, ['1', '2', '3'], '0')
        
        if should_exit:
            return None
        
        if not is_valid:
            print("Invalid choice. Please enter 0, 1, 2, or 3.")
            continue
        
        if choice == '1':
            while True:
                print("\nAvailable Puzzles:")
                print("1. Easy")
                print("2. Hard")
                print("3. Evil")
                print("0. Back to main menu")
                
                p = input("Select puzzle (0-3): ").strip()
                is_valid, should_exit = validate_input(p, ['1', '2', '3'], '0')
                
                if should_exit:
                    break
                
                if is_valid:
                    return PREDEFINED_PUZZLES[p]
                
                print("Invalid selection. Please enter 0, 1, 2, or 3.")
        
        elif choice == '2':
            while True:
                print("\nEnter 81 characters (digits 1-9 for filled cells, 0 or . for empty cells)")
                print("Example: 003020600900305001001806400008102900700000008006708200002609500800203009005010300")
                print("Type 'back' to return to menu or 'exit' to quit")
                
                data = input("Enter grid string: ").strip()
                
                if data.upper() in ['BACK', 'EXIT', 'Q', '0']:
                    if data.upper() == 'EXIT' or data.upper() == 'Q':
                        return None
                    break
                
                
                if len(data) < 81:
                    print(f"Error: Input too short. Expected 81 characters, got {len(data)}.")
                    continue
                
                if len(data) > 81:
                    print(f"Warning: Input longer than 81 characters. Using first 81 characters.")
                    data = data[:81]
                
                valid_chars = set(DIGITS + '0.') # Check for invalid characters
                invalid_chars = set(data) - valid_chars
                if invalid_chars:
                    print(f"Error: Invalid characters found: {', '.join(sorted(invalid_chars))}")
                    print("Only digits 1-9, 0, and . are allowed.")
                    continue
                
                parsed = gridValues(data)
                if parsed:
                    return data
                else:
                    print("Error: Failed to parse grid. Please check your input.")
        
        elif choice == '3':
            while True:
                print("\nEnter the filename in current directory")
                print("Type 'back' to return to menu or 'exit' to quit")
                
                fname = input("Enter filename(like test.txt): ").strip()
                
                if fname.upper() in ['BACK', 'EXIT', 'Q', '0']:
                    if fname.upper() == 'EXIT' or fname.upper() == 'Q':
                        return None
                    break
                
                if '..' in fname or '/' in fname or '\\' in fname:
                    print("Error: Invalid filename. Please use a filename in the current directory.")
                    continue
                
                if not os.path.exists(fname):
                    print(f"Error: File '{fname}' not found.")
                    continue
                
                try:
                    with open(fname, 'r', encoding='utf-8') as f:
                        content = f.read().replace('\n', '').replace(' ', '').replace('\t', '')
                        
                        valid_content = ''.join([c for c in content if c in DIGITS + '0.'])   # Extract only valid characters
                        
                        if len(valid_content) < 81:
                            print(f"Error: File content too short. Found {len(valid_content)} valid characters, need 81.")
                            continue
                        
                        if len(valid_content) > 81:
                            print(f"Warning: File has more than 81 valid characters. Using first 81.")
                            valid_content = valid_content[:81]
                        
                        parsed = gridValues(valid_content)
                        if parsed:
                            return valid_content
                        else:
                            print("Error: Failed to parse grid from file.")
                except PermissionError:
                    print("Error: Permission denied. Cannot read file.")
                except Exception as e:
                    print(f"Error reading file: {e}")

def get_algorithm_choice():
    # Get algorithm 
    while True:
        print("\n-- SELECT ALGORITHM --")
        print("1. CSP with Arc Consistency (AC-3)")
        print("2. Backtracking with Forward Checking + MRV")
        print("3. Local Search: Min-Conflicts")
        print("0. Exit")
        
        algo = input("Choose algorithm (0-3): ").strip()
        is_valid, should_exit = validate_input(algo, ['1', '2', '3'], '0')
        
        if should_exit:
            return None
        
        if is_valid:
            return algo
        
        print("Invalid choice. Please enter 0, 1, 2, or 3.")

def format_memory(bytes_value):
    
    if bytes_value < 1024:
        return f"{bytes_value:.2f} B"
    elif bytes_value < 1024 * 1024:
        return f"{bytes_value / 1024:.2f} KB"
    else:
        return f"{bytes_value / (1024 * 1024):.2f} MB"


def main():
    while True:    
        print("=" * 30)
        print("\t SUDOKU SOLVER ")
        print("=" * 30)
        
        
        gridStr = get_input_puzzle()
        if gridStr is None:
            print("\nExiting program. Goodbye!")
            sys.exit(0)
        
        print("\nInitial Grid:") # Display initial grid
        display(gridValues(gridStr))
        
        algo = get_algorithm_choice()
        if algo is None:
            print("\nExiting program. Goodbye!")
            sys.exit(0)
        
        while True:
        # Get visualization preference
            vis_input = input("\nVisualize the solving process? (y/n): ").strip().lower()
            if vis_input in ['y', 'yes']:
                visualize = True
                break
            elif vis_input in ['n', 'no']:
                visualize = False
                break
            elif vis_input in ['exit', 'q', '0']:
                print("\nExiting program. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid input. Please enter 'y' or 'n' (or 'exit' to quit).")
        
        tracemalloc.start() # Start performance tracking
        start_time = time.time()
        
        result = None
        algo_names = {
            '1': 'CSP (Arc Consistency)',
            '2': 'Backtracking (Forward Checking + MRV)',
            '3': 'Local Search (Min-Conflicts)'
        }
        
        print(f"\nSolving with {algo_names[algo]}...")
        print("Please wait...\n")
        
        try:
            if algo == '1':
                result = solveCspAC3(gridStr, visualize)
            elif algo == '2':
                result = solveBacktrackingFC(gridStr, visualize)
            elif algo == '3':
                result = solve_min_conflicts(gridStr, visualize)
        except KeyboardInterrupt:
            print("\n\nSolving interrupted by user.")
            tracemalloc.stop()
            sys.exit(0)
        except Exception as e:
            print(f"\n\nError during solving: {e}")
            tracemalloc.stop()
            continue
        
        end_time = time.time() # Stop performance tracking
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
    
        print("=" * 30)
        print("\t FINAL RESULT")
        print("=" * 30)
        
        if result:
            display(result)
            print(f"Status:        SOLVED")
        else:
            print("Status:        FAILED / NO SOLUTION FOUND")
            print("\nThe puzzle may be unsolvable or the algorithm")
            print("needs more time. Try a different algorithm.")
        
        elapsed_time = end_time - start_time
        print(f"\nAlgorithm:     {algo_names[algo]}")
        print(f"Time Taken:    {elapsed_time:.5f} seconds")
        print(f"Peak Memory:   {format_memory(peak_mem)}")
        print("=" * 30)
        
        while True: # Ask if user wants to continue
            continue_choice = input("\nSolve another puzzle? (y/n): ").strip().lower()
            if continue_choice in ['y', 'yes']:
                break
            elif continue_choice in ['n', 'no', 'exit', 'q', '0']:
                print("\nThank you for using Sudoku Solver. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

main()