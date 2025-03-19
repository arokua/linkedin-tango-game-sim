import math
import random
import tkinter as tk
from tkinter import messagebox, Button, Frame, Toplevel, Label, Entry, Checkbutton, Radiobutton, IntVar, StringVar, filedialog
import json
import os

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
    def __init__(self, n=6, known_cells=21, relations=8, adjacency_limit=2):
        if not has_positive_integer_sqrt_binary_search(n * n):
            raise ValueError("Board size must be a perfect square.")
        if n % 2 != 0:
            raise ValueError("Board side length must be even")
        self.n = n
        self.size = n * n
        self.valid_num = adjacency_limit  # Configurable adjacency limit
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
                return all(self.row_counts[r][0] == self.n//2 and self.row_counts[r][1] == self.n//2 for r in range(self.n)) and \
                       all(self.col_counts[c][0] == self.n//2 and self.col_counts[c][1] == self.n//2 for c in range(self.n))
            row, col = divmod(pos, self.n)
            for value in [0, 1]:
                if self.row_counts[row][value] < self.n//2 and self.col_counts[col][value] < self.n//2:
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
        # General adjacency check for valid_num
        count = 1
        for c in range(col-1, -1, -1):
            if self.board[row][c] == value:
                count += 1
            else:
                break
            if count > self.valid_num:
                return False
        count = 1
        for c in range(col+1, self.n):
            if self.board[row][c] == value:
                count += 1
            else:
                break
            if count > self.valid_num:
                return False
        count = 1
        for r in range(row-1, -1, -1):
            if self.board[r][col] == value:
                count += 1
            else:
                break
            if count > self.valid_num:
                return False
        count = 1
        for r in range(row+1, self.n):
            if self.board[r][col] == value:
                count += 1
            else:
                break
            if count > self.valid_num:
                return False
        return True

    def initialize_puzzle(self, known_cells, relations):
        self.row_counts = [[0, 0] for _ in range(self.n)]
        self.col_counts = [[0, 0] for _ in range(self.n)]

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
            if temp_row_counts[r][value] <= self.n//2 and temp_col_counts[c][value] <= self.n//2:
                selected_positions.append(pos)
                self.row_counts[r][value] += 1
                self.col_counts[c][value] += 1
                all_positions.remove(pos)
            attempts += 1

        self.known_cells = [(r, c, self.board[r][c]) for r, c in selected_positions]

        possible_relations = []
        for r in range(self.n):
            for c in range(self.n):
                if c < self.n - 1:
                    possible_relations.append(((r, c), (r, c+1)))
                if r < self.n - 1:
                    possible_relations.append(((r, c), (r+1, c)))
        selected = random.sample(possible_relations, min(relations, len(possible_relations)))
        relation_counts_row = [0] * self.n
        relation_counts_col = [0] * self.n
        for (r1, c1), (r2, c2) in selected:
            if self.board[r1][c1] == self.board[r2][c2]:
                rel = '='
                if r1 == r2:
                    if relation_counts_row[r1] >= self.n//2 - 1:
                        continue
                    relation_counts_row[r1] += 1
                else:
                    if relation_counts_col[c1] >= self.n//2 - 1:
                        continue
                    relation_counts_col[c1] += 1
            else:
                rel = '×'
            self.relations[((r1, c1), (r2, c2))] = rel

        self.board = [[-1 for _ in range(self.n)] for _ in range(self.n)]
        for r, c, val in self.known_cells:
            self.board[r][c] = val

    def solve(self):
        def backtrack(pos):
            if pos == self.size:
                return all(self.row_counts[r][0] == self.n//2 and self.row_counts[r][1] == self.n//2 for r in range(self.n)) and \
                       all(self.col_counts[c][0] == self.n//2 and self.col_counts[c][1] == self.n//2 for c in range(self.n))
            row, col = divmod(pos, self.n)
            if self.board[row][col] != -1:
                return backtrack(pos + 1)
            for value in [0, 1]:
                if self.row_counts[row][value] < self.n//2 and self.col_counts[col][value] < self.n//2:
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
                if self.row_counts[other_r][new_value] < self.n//2 and self.col_counts[other_c][new_value] < self.n//2:
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
        if (row, col, 0) in self.known_cells or (row, col, 1) in self.known_cells:
            return

        current = self.board[row][col]
        if current != -1:
            self.row_counts[row][current] -= 1
            self.col_counts[col][current] -= 1

        if current == -1:
            new_value = 0
        elif current == 0:
            new_value = 1
        else:
            new_value = -1

        self.board[row][col] = new_value
        if new_value != -1:
            self.row_counts[row][new_value] += 1
            self.col_counts[col][new_value] += 1

    def is_valid_board(self):
        for i in range(self.n):
            if self.row_counts[i][0] > self.n//2 or self.row_counts[i][1] > self.n//2:
                return False
            if self.col_counts[i][0] > self.n//2 or self.col_counts[i][1] > self.n//2:
                return False
        filled = sum(1 for row in self.board for cell in row if cell != -1)
        if filled == self.size:
            if not all(self.row_counts[r][0] == self.n//2 and self.row_counts[r][1] == self.n//2 for r in range(self.n)):
                return False
            if not all(self.col_counts[c][0] == self.n//2 and self.col_counts[c][1] == self.n//2 for c in range(self.n)):
                return False

        for r in range(self.n):
            for c in range(self.n):
                if self.board[r][c] != -1:
                    value = self.board[r][c]
                    count = 1
                    for cc in range(c-1, -1, -1):
                        if self.board[r][cc] == value:
                            count += 1
                        else:
                            break
                        if count > self.valid_num:
                            return False
                    count = 1
                    for cc in range(c+1, self.n):
                        if self.board[r][cc] == value:
                            count += 1
                        else:
                            break
                        if count > self.valid_num:
                            return False
                    count = 1
                    for rr in range(r-1, -1, -1):
                        if self.board[rr][c] == value:
                            count += 1
                        else:
                            break
                        if count > self.valid_num:
                            return False
                    count = 1
                    for rr in range(r+1, self.n):
                        if self.board[rr][c] == value:
                            count += 1
                        else:
                            break
                        if count > self.valid_num:
                            return False

        for (r1, c1), (r2, c2) in self.relations:
            if self.board[r1][c1] != -1 and self.board[r2][c2] != -1:
                rel = self.relations[((r1, c1), (r2, c2))]
                if rel == '=' and self.board[r1][c1] != self.board[r2][c2]:
                    return False
                if rel == '×' and self.board[r1][c1] == self.board[r2][c2]:
                    return False

        return True

    def save_board(self, filename):
        """
        Saves the current board state to a file.
        """
        board_state = {
            'n': self.n,
            'valid_num': self.valid_num,
            'board': self.board,
            'relations': {f"{r1},{c1}->{r2},{c2}": rel for (r1, c1), (r2, c2) in self.relations for rel in [self.relations[((r1, c1), (r2, c2))]]},
            'known_cells': self.known_cells,
            'row_counts': self.row_counts,
            'col_counts': self.col_counts,
            'known_cells_count': self.known_cells_count,
            'relations_count': self.relations_count
        }
        with open(filename, 'w') as f:
            json.dump(board_state, f)

    def load_board(self, filename):
        """
        Loads a board state from a file.
        """
        with open(filename, 'r') as f:
            board_state = json.load(f)
        self.n = board_state['n']
        self.length = self.n
        self.size = self.n * self.n
        self.valid_num = board_state['valid_num']
        self.board = board_state['board']
        self.relations = {}
        for key, rel in board_state['relations'].items():
            coords = key.split('->')
            pos1 = coords[0].split(',')
            pos2 = coords[1].split(',')
            r1, c1 = int(pos1[0]), int(pos1[1])
            r2, c2 = int(pos2[0]), int(pos2[1])
            self.relations[((r1, c1), (r2, c2))] = rel
        self.known_cells = [(r, c, val) for r, c, val in board_state['known_cells']]
        self.row_counts = board_state['row_counts']
        self.col_counts = board_state['col_counts']
        self.known_cells_count = board_state['known_cells_count']
        self.relations_count = board_state['relations_count']
    
    def print_board_to_string(self):
        """
        Returns a string representation of the board and its relations.
        """
        board_str = "Board:\n"
        for r in range(self.n):
            row = []
            for c in range(self.n):
                if self.board[r][c] == 0:
                    row.append("M")
                elif self.board[r][c] == 1:
                    row.append("S")
                else:
                    row.append(".")
            board_str += " ".join(row) + "\n"
        board_str += "\nRelations:\n"
        for (r1, c1), (r2, c2) in self.relations:
            board_str += f"({r1},{c1})-({r2},{c2}): {self.relations[((r1, c1), (r2, c2))]}\n"
        return board_str

class TangoBoardGUI:
    def __init__(self, master, board_size=6):
        """
        Initializes the GUI for the Tango board with random known cells and relations.
        """
        self.master = master
        self.master.title("LinkedIn Tango Board")
        known_cells = random.randint(3, board_size*2)
        relations = int(known_cells * random.random() * 10)
        self.board_size = board_size
        self.known_cells = known_cells
        self.relations = relations
        self.adjacency_mode = 'fixed'  # Default to fixed (2)
        self.adjacency_limit = 2
        self.full_random = False
        self.board = TangoBoard(n=board_size, known_cells=known_cells, relations=relations, adjacency_limit=self.adjacency_limit)
        self.cell_size = 50
        self.padding = 8
        self.update_canvas_size()
        self.frame = Frame(master)
        self.frame.pack(padx=10, pady=10)
        self.canvas = tk.Canvas(self.frame, width=self.canvas_width, height=self.canvas_height,
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
        self.save_button = Button(self.buttons_frame, text="Save Board", command=self.save_board)
        self.save_button.grid(row=0, column=3, padx=5)
        self.load_button = Button(self.buttons_frame, text="Load Board", command=self.load_board)
        self.load_button.grid(row=0, column=4, padx=5)
        self.settings_button = Button(self.buttons_frame, text="⚙️", command=self.open_settings)
        self.settings_button.grid(row=0, column=5, padx=5)
        self.draw_board()

    def update_canvas_size(self):
        """
        Updates the canvas size based on the current board size.
        """
        self.canvas_width = self.board.length * self.cell_size + self.padding * 2
        self.canvas_height = self.board.length * self.cell_size + self.padding * 2

    def open_settings(self):
        """
        Opens a settings window for configuring the game.
        """
        settings_window = Toplevel(self.master)
        settings_window.title("Settings")
        settings_window.geometry("300x400")

        # Full Random Mode
        full_random_var = IntVar(value=1 if self.full_random else 0)
        Checkbutton(settings_window, text="Full Random (Board Size 6-12)", variable=full_random_var,
                    command=lambda: self.toggle_full_random(full_random_var)).pack(pady=5)

        # Adjacency Rule Toggle
        Label(settings_window, text="Adjacency Rule:").pack(pady=5)
        adjacency_var = StringVar(value=self.adjacency_mode)
        Radiobutton(settings_window, text="Fixed (2)", variable=adjacency_var, value='fixed',
                    command=lambda: self.set_adjacency_mode(adjacency_var)).pack()
        Radiobutton(settings_window, text="Scaled (n//2)", variable=adjacency_var, value='scaled',
                    command=lambda: self.set_adjacency_mode(adjacency_var)).pack()

        # Custom Known Cells and Relations
        Label(settings_window, text="Known Cells:").pack(pady=5)
        known_cells_entry = Entry(settings_window)
        known_cells_entry.insert(0, str(self.known_cells))
        known_cells_entry.pack()
        Label(settings_window, text="Relations:").pack(pady=5)
        relations_entry = Entry(settings_window)
        relations_entry.insert(0, str(self.relations))
        relations_entry.pack()
        Button(settings_window, text="Print Board", command=self.print_board_to_string).pack(pady=10)
        # Apply Button
        Button(settings_window, text="Apply", command=lambda: self.apply_settings(
            full_random_var.get(), adjacency_var.get(),
            known_cells_entry.get(), relations_entry.get(), settings_window)).pack(pady=10)

    def toggle_full_random(self, full_random_var):
        self.full_random = bool(full_random_var.get())

    def set_adjacency_mode(self, adjacency_var):
        self.adjacency_mode = adjacency_var.get()
        self.adjacency_limit = 2 if self.adjacency_mode == 'fixed' else (self.board.n - 1) // 2

    def apply_settings(self, full_random, adjacency_mode, known_cells_str, relations_str, settings_window):
        try:
            known_cells = int(known_cells_str)
            relations = int(relations_str)
            if known_cells < 0 or known_cells > self.board.size:
                raise ValueError("Known cells must be between 0 and board size.")
            if relations < 0 or relations > self.board.size * 2:
                raise ValueError("Relations must be between 0 and twice the board size.")
            self.known_cells = known_cells
            self.relations = relations
            self.full_random = bool(full_random)
            self.adjacency_mode = adjacency_mode
            self.adjacency_limit = 2 if self.adjacency_mode == 'fixed' else self.board.n // 2
            self.new_game()  # Regenerate board with new settings
            settings_window.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def draw_board(self):
        self.canvas.delete("all")
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        for row in range(self.board.length):
            for col in range(self.board.length):
                x1 = col * self.cell_size + self.padding
                y1 = row * self.cell_size + self.padding
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
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
            if r1 == r2:
                x1 = (c1 + 1) * self.cell_size + self.padding
                y1 = r1 * self.cell_size + self.cell_size/2 + self.padding
                x2 = c2 * self.cell_size + self.padding
                y2 = y1
            else:
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
        col = (event.x - self.padding) // self.cell_size
        row = (event.y - self.padding) // self.cell_size
        if 0 <= row < self.board.length and 0 <= col < self.board.length:
            self.board.toggle_cell(row, col)
            self.draw_board()

    def new_game(self):
        if self.full_random:
            self.board_size = random.choice([6, 8, 10, 12])
            self.known_cells = random.randint(3, self.board_size * 2)
            self.relations = int(self.known_cells * random.random() * 10)
        self.adjacency_limit = 2 if self.adjacency_mode == 'fixed' else self.board_size // 2
        self.board = TangoBoard(n=self.board_size, known_cells=self.known_cells,
                               relations=self.relations, adjacency_limit=self.adjacency_limit)
        self.update_canvas_size()
        self.draw_board()

    def solve_board(self):
        board_copy = [row[:] for row in self.board.board]
        row_counts_copy = [counts[:] for counts in self.board.row_counts]
        col_counts_copy = [counts[:] for counts in self.board.col_counts]
        relations_copy = self.board.relations.copy()

        if self.board.solve():
            messagebox.showinfo("Success", "Board solved successfully!")
            self.draw_board()
        else:
            messagebox.showinfo("Failed", "No solution exists for this board configuration.")
            self.board.board = board_copy
            self.board.row_counts = row_counts_copy
            self.board.col_counts = col_counts_copy
            self.board.relations = relations_copy
            self.draw_board()

    def check_validity(self):
        if self.board.is_valid_board():
            messagebox.showinfo("Valid", "The current board state is valid.")
        else:
            messagebox.showwarning("Invalid", "The current board state is invalid.")

    def save_board(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            self.board.save_board(filename)
            messagebox.showinfo("Success", "Board saved successfully!")

    def load_board(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            # Save settings to restore after loading
            board_size = self.board_size
            known_cells = self.known_cells
            relations = self.relations
            full_random = self.full_random
            adjacency_mode = self.adjacency_mode
            adjacency_limit = self.adjacency_limit

            self.board.load_board(filename)
            self.board_size = self.board.n
            self.update_canvas_size()
            self.draw_board()

            # Restore settings (but board_size is now dictated by the loaded board)
            self.known_cells = known_cells
            self.relations = relations
            self.full_random = full_random
            self.adjacency_mode = adjacency_mode
            self.adjacency_limit = adjacency_limit
            messagebox.showinfo("Success", "Board loaded successfully!")

    def print_board_to_string(self):
        """
        Displays the board and relations as a string in a new window.
        """
        board_text = self.board.print_board_to_string()
        print_window = Toplevel(self.master)
        print_window.title("Board and Relations")
        print_window.geometry("400x400")
        text_area = tk.Text(print_window, wrap=tk.WORD, height=20, width=50)
        text_area.insert(tk.END, board_text)
        text_area.config(state='disabled')  # Make it read-only
        text_area.pack(padx=10, pady=10)
        Button(print_window, text="Close", command=print_window.destroy).pack(pady=5)

def run_tango_board():
    root = tk.Tk()
    app = TangoBoardGUI(root, board_size=6)
    root.mainloop()

if __name__ == "__main__":
    run_tango_board()