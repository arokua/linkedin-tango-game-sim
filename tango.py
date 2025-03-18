import math
import random
import tkinter as tk
from tkinter import messagebox, Button, Frame

def has_positive_integer_sqrt_binary_search(num):
    """
    Checks if an integer has a positive integer square root using binary search.
    """
    if num < 0:
        return False
    if num == 0:
        return True
    low = 1
    high = num
    while low <= high:
        mid = (low + high) // 2
        square = mid * mid
        if square == num:
            return True
        elif square < num:
            low = mid + 1
        else:
            high = mid - 1
    return False

class TangoBoard:
    def __init__(self, n=6, known_cells=21, relations=8):
        if not has_positive_integer_sqrt_binary_search(n * n):
            raise ValueError("Board size must be a perfect square.")
        if n % 2 != 0:
            raise ValueError("Board side length must be even")
        self.n = n
        self.size = n * n
        self.board = [[-1 for _ in range(n)] for _ in range(n)]
        self.relations = {}  # ((r1, c1), (r2, c2)): '=' or '×'
        self.row_counts = [[0, 0] for _ in range(n)]  # [M, S]
        self.col_counts = [[0, 0] for _ in range(n)]
        self.known_cells = []
        self.length = n
        self.known_cells_count = known_cells
        self.relations_count = relations
        self.generate_full_board()
        self.initialize_puzzle(known_cells, relations)

    def generate_full_board(self):
        def backtrack(pos):
            if pos == self.size:
                return all(self.row_counts[r][0] == 3 and self.row_counts[r][1] == 3 for r in range(self.n)) and \
                       all(self.col_counts[c][0] == 3 and self.col_counts[c][1] == 3 for c in range(self.n))
            row, col = divmod(pos, self.n)
            for value in [0, 1]:  # 0 = "M", 1 = "S"
                if self.row_counts[row][value] < 3 and self.col_counts[col][value] < 3:
                    if self.is_valid_position(row, col, value):
                        self.board[row][col] = value
                        self.row_counts[row][value] += 1
                        self.col_counts[col][value] += 1
                        if backtrack(pos + 1):
                            return True
                        self.board[row][col] = -1
                        self.row_counts[row][value] -= 1
                        self.col_counts[col][value] -= 1
            return False

        backtrack(0)

    def is_valid_position(self, row, col, value):
        # Check no more than 2 adjacent identical symbols
        # Horizontal checks
        if col >= 2 and self.board[row][col-1] == value and self.board[row][col-2] == value:
            return False
        if col <= self.n-3 and self.board[row][col+1] == value and self.board[row][col+2] == value:
            return False
        if col >= 1 and col <= self.n-2 and self.board[row][col-1] == value and self.board[row][col+1] == value:
            return False
        # Vertical checks
        if row >= 2 and self.board[row-1][col] == value and self.board[row-2][col] == value:
            return False
        if row <= self.n-3 and self.board[row+1][col] == value and self.board[row+2][col] == value:
            return False
        if row >= 1 and row <= self.n-2 and self.board[row-1][col] == value and self.board[row+1][col] == value:
            return False
        return True

    def initialize_puzzle(self, known_cells, relations):
        # Reset counts
        self.row_counts = [[0, 0] for _ in range(self.n)]
        self.col_counts = [[0, 0] for _ in range(self.n)]

        # Select known cells
        all_positions = [(r, c) for r in range(self.n) for c in range(self.n)]
        selected_positions = []
        attempts = 0
        while len(selected_positions) < known_cells and attempts < 1000:
            pos = random.choice(all_positions)
            r, c = pos
            value = self.board[r][c]
            temp_row_counts = [row[:] for row in self.row_counts]
            temp_col_counts = [col[:] for col in self.col_counts]
            temp_row_counts[r][value] += 1
            temp_col_counts[c][value] += 1
            if temp_row_counts[r][value] <= 3 and temp_col_counts[c][value] <= 3:
                selected_positions.append(pos)
                self.row_counts[r][value] += 1
                self.col_counts[c][value] += 1
                all_positions.remove(pos)
            attempts += 1

        self.known_cells = [(r, c, self.board[r][c]) for r, c in selected_positions]

        # Add relations
        possible_relations = []
        for r in range(self.n):
            for c in range(self.n):
                if c < self.n - 1:
                    possible_relations.append(((r, c), (r, c+1)))
                if r < self.n - 1:
                    possible_relations.append(((r, c), (r+1, c)))
        selected = random.sample(possible_relations, relations)
        relation_counts_row = [0] * self.n  # Count of '=' per row
        relation_counts_col = [0] * self.n  # Count of '=' per column
        for (r1, c1), (r2, c2) in selected:
            if self.board[r1][c1] == self.board[r2][c2]:
                rel = '='
                if r1 == r2:
                    if relation_counts_row[r1] >= 2:  # Max 2 '=' per row
                        continue
                    relation_counts_row[r1] += 1
                else:
                    if relation_counts_col[c1] >= 2:  # Max 2 '=' per column
                        continue
                    relation_counts_col[c1] += 1
            else:
                rel = '×'
            self.relations[((r1, c1), (r2, c2))] = rel

        # Set board to known cells only
        self.board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        for r, c, val in self.known_cells:
            self.board[r][c] = val

    def solve(self):
        def backtrack(pos):
            if pos == self.size:
                return all(self.row_counts[r][0] == 3 and self.row_counts[r][1] == 3 for r in range(self.n)) and \
                       all(self.col_counts[c][0] == 3 and self.col_counts[c][1] == 3 for c in range(self.n))
            row, col = divmod(pos, self.n)
            if self.board[row][col] != -1:
                return backtrack(pos + 1)
            for value in [0, 1]:
                if self.row_counts[row][value] < 3 and self.col_counts[col][value] < 3:
                    if self.is_valid_position(row, col, value):
                        self.board[row][col] = value
                        self.row_counts[row][value] += 1
                        self.col_counts[col][value] += 1
                        if self.propagate_relations(row, col, value):
                            if backtrack(pos + 1):
                                return True
                        self.board[row][col] = -1
                        self.row_counts[row][value] -= 1
                        self.col_counts[col][value] -= 1
            return False

        return backtrack(0)

    def propagate_relations(self, row, col, value):
        for (r1, c1), (r2, c2) in self.relations:
            if (r1, c1) == (row, col):
                other_r, other_c = r2, c2
            elif (r2, c2) == (row, col):
                other_r, other_c = r1, c1
            else:
                continue
            rel = self.relations[((r1, c1), (r2, c2))]
            if self.board[other_r][other_c] == -1:
                new_value = value if rel == '=' else 1 - value
                if self.row_counts[other_r][new_value] < 3 and self.col_counts[other_c][new_value] < 3:
                    if self.is_valid_position(other_r, other_c, new_value):
                        self.board[other_r][other_c] = new_value
                        self.row_counts[other_r][new_value] += 1
                        self.col_counts[other_c][new_value] += 1
                    else:
                        return False
                else:
                    return False
            else:
                if rel == '=' and self.board[other_r][other_c] != value:
                    return False
                if rel == '×' and self.board[other_r][other_c] == value:
                    return False
        return True

    def toggle_cell(self, row, col):
        """
        Toggles the value of a cell between empty (-1), M (0), and S (1), updating counts.
        Only allows toggling for non-known cells.
        """
        # Check if the cell is a known cell
        if (row, col, 0) in self.known_cells or (row, col, 1) in self.known_cells:
            return  # Don't toggle known cells

        current = self.board[row][col]
        if current != -1:
            self.row_counts[row][current] -= 1
            self.col_counts[col][current] -= 1

        if current == -1:
            new_value = 0  # Set to M
        elif current == 0:
            new_value = 1  # Set to S
        else:
            new_value = -1  # Set to empty

        self.board[row][col] = new_value
        if new_value != -1:
            self.row_counts[row][new_value] += 1
            self.col_counts[col][new_value] += 1

    def is_valid_board(self):
        """
        Checks if the current board state satisfies all constraints.
        """
        # Check balance
        for i in range(self.n):
            if self.row_counts[i][0] > 3 or self.row_counts[i][1] > 3:
                return False
            if self.col_counts[i][0] > 3 or self.col_counts[i][1] > 3:
                return False
        # Fully filled board must have exactly 3 M's and 3 S's
        filled = sum(1 for row in self.board for cell in row if cell != -1)
        if filled == self.size:
            if not all(self.row_counts[r][0] == 3 and self.row_counts[r][1] == 3 for r in range(self.n)):
                return False
            if not all(self.col_counts[c][0] == 3 and self.col_counts[c][1] == 3 for c in range(self.n)):
                return False

        # Check adjacency
        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] != -1:
                    value = self.board[r][c]
                    # Horizontal
                    if c >= 2 and self.board[r][c-1] == value and self.board[r][c-2] == value:
                        return False
                    if c <= self.n-3 and self.board[r][c+1] == value and self.board[r][c+2] == value:
                        return False
                    if c >= 1 and c <= self.n-2 and self.board[r][c-1] == value and self.board[r][c+1] == value:
                        return False
                    # Vertical
                    if r >= 2 and self.board[r-1][c] == value and self.board[r-2][c] == value:
                        return False
                    if r <= self.n-3 and self.board[r+1][c] == value and self.board[r+2][c] == value:
                        return False
                    if r >= 1 and r <= self.n-2 and self.board[r-1][c] == value and self.board[r+1][c] == value:
                        return False

        # Check relations
        for (r1, c1), (r2, c2) in self.relations:
            if self.board[r1][c1] != -1 and self.board[r2][c2] != -1:
                rel = self.relations[((r1, c1), (r2, c2))]
                if rel == '=' and self.board[r1][c1] != self.board[r2][c2]:
                    return False
                if rel == '×' and self.board[r1][c1] == self.board[r2][c2]:
                    return False

        return True

    def print_board(self):
        for r in range(self.n):
            row = []
            for c in range(self.n):
                if self.board[r][c] == 0:
                    row.append("M")
                elif self.board[r][c] == 1:
                    row.append("S")
                else:
                    row.append(".")
            print(" ".join(row))
        print("\nRelations:")
        for (r1, c1), (r2, c2) in self.relations:
            print(f"({r1},{c1})-({r2},{c2}): {self.relations[((r1, c1), (r2, c2))]}")

class TangoBoardGUI:
    def __init__(self, master, board_size=6):
        """
        Initializes the GUI for the Tango board.
        """
        self.master = master
        self.master.title("LinkedIn Tango Board")
        known_cells=random.randint(3,board_size*2)
        relations=int(known_cells*random.random()*10)
        self.board = TangoBoard(n=board_size, known_cells=known_cells, relations=relations)
        self.cell_size = 50
        self.padding = 8
        canvas_width = self.board.length * self.cell_size + self.padding * 2
        canvas_height = self.board.length * self.cell_size + self.padding * 2
        self.frame = Frame(master)
        self.frame.pack(padx=10, pady=10)
        self.canvas = tk.Canvas(self.frame, width=canvas_width, height=canvas_height,
                                bg='white', borderwidth=0, highlightthickness=0)
        self.canvas.pack()
        self.buttons_frame = Frame(master)
        self.buttons_frame.pack(pady=5)
        self.new_game_button = Button(self.buttons_frame, text="New Game", command=self.new_game)
        self.new_game_button.grid(row=0, column=0, padx=5)
        self.solve_button = Button(self.buttons_frame, text="Solve", command=self.solve_board)
        self.solve_button.grid(row=0, column=1, padx=5)
        self.check_button = Button(self.buttons_frame, text="Check Validity", command=self.check_validity)
        self.check_button.grid(row=0, column=2, padx=5)
        self.draw_board()

    def draw_board(self):
        """
        Draws the board and relationships on the canvas.
        """
        self.canvas.delete("all")
        for row in range(self.board.length):
            for col in range(self.board.length):
                x1 = col * self.cell_size + self.padding
                y1 = row * self.cell_size + self.padding
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                # Highlight known cells with a light gray background
                fill_color = 'lightgray' if (row, col, 0) in self.board.known_cells or (row, col, 1) in self.board.known_cells else 'white'
                self.canvas.create_rectangle(x1, y1, x2, y2, outline='black', fill=fill_color)
                cell_value = self.board.board[row][col]
                if cell_value == 0:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2,
                                            text="M", font=('Arial', 20, 'bold'))
                elif cell_value == 1:
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2,
                                            text="S", font=('Arial', 20, 'bold'))

        for (r1, c1), (r2, c2) in self.board.relations:
            relation_type = self.board.relations[((r1, c1), (r2, c2))]
            if r1 == r2:  # Horizontal relation
                x1 = (c1 + 1) * self.cell_size + self.padding
                y1 = r1 * self.cell_size + self.cell_size/2 + self.padding
                x2 = c2 * self.cell_size + self.padding
                y2 = y1
            else:  # Vertical relation
                x1 = c1 * self.cell_size + self.cell_size/2 + self.padding
                y1 = (r1 + 1) * self.cell_size + self.padding
                x2 = x1
                y2 = r2 * self.cell_size + self.padding

            if relation_type == '=':
                if r1 == r2:
                    self.canvas.create_line(x1-5, y1-3, x2+5, y2-3, width=2)
                    self.canvas.create_line(x1-5, y1+3, x2+5, y2+3, width=2)
                else:
                    self.canvas.create_line(x1-3, y1-5, x2-3, y2+5, width=2)
                    self.canvas.create_line(x1+3, y1-5, x2+3, y2+5, width=2)
            elif relation_type == '×':
                if r1 == r2:
                    self.canvas.create_line(x1-5, y1-5, x2+5, y2+5, width=2)
                    self.canvas.create_line(x1-5, y1+5, x2+5, y2-5, width=2)
                else:
                    self.canvas.create_line(x1-5, y1-5, x2+5, y2+5, width=2)
                    self.canvas.create_line(x1+5, y1-5, x2-5, y2+5, width=2)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_click(self, event):
        """
        Toggles cell values on click.
        """
        col = (event.x - self.padding) // self.cell_size
        row = (event.y - self.padding) // self.cell_size
        if 0 <= row < self.board.length and 0 <= col < self.board.length:
            self.board.toggle_cell(row, col)
            self.draw_board()

    def new_game(self):
        """
        Starts a new game with a fresh board.
        """
        self.board = TangoBoard(n=self.board.n, known_cells=self.board.known_cells_count,
                               relations=self.board.relations_count)
        self.draw_board()

    def solve_board(self):
        """
        Attempts to solve the current board.
        """
        # Save the current state
        board_copy = [row[:] for row in self.board.board]
        row_counts_copy = [counts[:] for counts in self.board.row_counts]
        col_counts_copy = [counts[:] for counts in self.board.col_counts]
        relations_copy = self.board.relations.copy()

        if self.board.solve():
            messagebox.showinfo("Success", "Board solved successfully!")
            self.draw_board()
        else:
            messagebox.showinfo("Failed", "No solution exists for this board configuration.")
            # Restore the original state
            self.board.board = board_copy
            self.board.row_counts = row_counts_copy
            self.board.col_counts = col_counts_copy
            self.board.relations = relations_copy
            self.draw_board()

    def check_validity(self):
        """
        Checks if the current board is valid.
        """
        if self.board.is_valid_board():
            messagebox.showinfo("Valid", "The current board state is valid.")
        else:
            messagebox.showwarning("Invalid", "The current board state is invalid.")

def run_tango_board():
    """
    Runs the Tango Board application.
    """
    root = tk.Tk()
    app = TangoBoardGUI(root, board_size=6)
    root.mainloop()

if __name__ == "__main__":
    run_tango_board()