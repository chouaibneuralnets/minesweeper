import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells)==self.count:
            return self.cells.copy()
        return set()
    
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count==0:
            return self.cells.copy()
        return set()
        
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count-=1
        
    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):

        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
        """
            #1) mark the cell as a move that has been made
        self.moves_made.add(cell)
            #2) mark the cell as safe
        self.mark_safe(cell)
            #3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2): 
            for j in range(cell[1] - 1, cell[1] + 2): 
                if (i, j) != cell and 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.safes and (i, j) not in self.mines:
                        neighbors.add((i, j))
            
            #4) mark any additional cells as safe or as mines
        new_sentence = Sentence(neighbors, count)
        self.knowledge.append(new_sentence)    
            #5) add any new sentences to the AI's knowledge base
        self.apply_inference()      
    def apply_inference(self):
        
        new_knowledge = []

       
        for sentence in self.knowledge:
            mines = sentence.known_mines()
            safes = sentence.known_safes()

            for mine in mines:
                self.mark_mine(mine)
            for safe in safes:
                self.mark_safe(safe)

        
        self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

        
        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 != s2 and s1.cells.issubset(s2.cells):
                    inferred_cells = s2.cells - s1.cells
                    inferred_count = s2.count - s1.count
                    new_sentence = Sentence(inferred_cells, inferred_count)
                    if new_sentence not in self.knowledge:
                        new_knowledge.append(new_sentence)

       
        self.knowledge.extend(new_knowledge)    
       

    def make_safe_move(self):
            for cell in self.safes:
                if cell not in self.moves_made:
                    return cell
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
     """
        available_moves = [
            (i, j) for i in range(self.height) for j in range(self.width)
            
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]
        return random.choice(available_moves) if available_moves else None
        


# tester la class sentence 
s = Sentence({(0, 1), (1, 1), (2, 1)}, 1)
print("   cells:", s.cells)
print("   count:", s.count)
print("   known mines:", s.known_mines()) 
print("   known safes:", s.known_safes())

s.mark_mine((1, 1))
print("   cells:", s.cells)
print("   count:", s.count)
print("   known mines:", s.known_mines()) 
print("   known safes:", s.known_safes()) 

s.mark_safe((0, 0))
print("   cells:", s.cells)
print("   count:", s.count)
print("   known mines:", s.known_mines()) 
print("   known safes:", s.known_safes()) 

sentence2 = Sentence({(3, 1), (4, 1), (5, 1)}, 3) 

print("known mines:", sentence2.known_mines())  

# Tester add_knowledge
ai = MinesweeperAI(height=8, width=8)
ai.add_knowledge((4, 4), 1)
print("Connaissances après ajout de la cellule (4, 4) avec 1 mine voisine:")
for sentence in ai.knowledge:
    print(sentence)
ai.add_knowledge((2, 2), 0)
print("\nConnaissances après ajout de la cellule (2, 2) avec 0 mines voisines:")
for sentence in ai.knowledge:
    print(sentence)
ai.add_knowledge((1, 1), 2)
print("\nConnaissances après ajout de la cellule (1, 1) avec 2 mines voisines:")
for sentence in ai.knowledge:
    print(sentence)


ai = MinesweeperAI(height=8, width=8)
ai.safes = {(2, 2), (3, 3), (4, 4)}
ai.moves_made = {(2, 2)} 

# Tester make_safe_move
safe_move = ai.make_safe_move()
print(f"Prochain coup sûr : {safe_move}")  
ai.mines = {(1, 1), (4, 4)}

# Tester make_random_move
random_move = ai.make_random_move()
print(f"Prochain coup aléatoire : {random_move}")  
