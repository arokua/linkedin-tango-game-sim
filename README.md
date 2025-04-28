# Simple simulation of Linkedin Tango game
A simple simulation of the linkedin tango game using Python with tkinter
To run with python installed, you just need to install tkinter as extra library if not already have it.
Also install Shiny if you want the web version, then run main.py, the class file should be in the same directory as the main.py
```
    pip install tkinter 
    pip install shiny
```

Data structure used:
2D adjacency matrix to represent the board cells and another 2D matrix to represent the relationships.

The speed to solve and generate is not ideal at O(n squared) worse case.

Using backtracking, the board when generated is checked for the following rules to ensure valid board:

1. For a board of even side length n, there is at max ( n - 1 ) / 2 same symbols next to each other
2. In each row and columns, the total maximum of the two differing filled characters (S and M) must be the same. So 3 S and 3 M for 6x6 board and so on.
3. To help ensure uniqueness, relations are added that does not break the previous 2 rules.
4. If a board when generated is not valid for the given parameter set, it will recursively be regenerated until the board is valid.

Other functionalities to be add:
- Allow for manually setting the known number of cells and relations in each itterations.
- Checking that those value are actually feasible
- Save and load the board to a json file
- Random parameter generation
- Print a text representation of the board out.

