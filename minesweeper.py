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
        
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
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
        
        self.moves_made.add(cell)

        self.mark_safe(cell)

        # Find all neighbors
        neighbors = []
        for i_offset in [-1, 0, 1]:
            for j_offset in [-1, 0, 1]:
                if i_offset == 0 and j_offset == 0:
                    continue
                neighbor_i = cell[0] + i_offset
                neighbor_j = cell[1] + j_offset
                if (0 <= neighbor_i < self.height and 
                    0 <= neighbor_j < self.width):
                    neighbors.append((neighbor_i, neighbor_j))

        # Filter neighbors and count known mines
        unknown_neighbors = []
        known_mines_count = 0
        for neighbor in neighbors:
            if neighbor in self.moves_made or neighbor in self.safes:
                continue
            elif neighbor in self.mines:
                known_mines_count += 1
            else:
                unknown_neighbors.append(neighbor)

        # Create new sentence
        if unknown_neighbors:
            new_sentence = Sentence(unknown_neighbors, count - known_mines_count)
            self.knowledge.append(new_sentence)

        changed = True
        while changed:
            changed = False
            for sentence in self.knowledge:
                # Check for known mines
                mines = sentence.known_mines()
                if mines:
                    changed = True
                    for mine in list(mines):
                        self.mark_mine(mine)
                
                # Check for known safes
                safes = sentence.known_safes()
                if safes:
                    changed = True
                    for safe in list(safes):
                        self.mark_safe(safe)

            new_sentences = []
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if (sentence1.cells.issubset(sentence2.cells) and 
                        sentence1 != sentence2 and 
                        len(sentence1.cells) > 0 and 
                        len(sentence2.cells) > 0):
                        
                        new_cells = sentence2.cells - sentence1.cells
                        new_count = sentence2.count - sentence1.count
                        
                        if new_cells:
                            new_sentence = Sentence(new_cells, new_count)
                            if new_sentence not in self.knowledge:
                                new_sentences.append(new_sentence)

            # Add all new sentences to knowledge
            if new_sentences:
                changed = True
                for sentence in new_sentences:
                    self.knowledge.append(sentence)

    def make_safe_move(self):

        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):

        valid_moves = []
        
        # Loop through all cells on the board
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    valid_moves.append(cell)

        if valid_moves:
            return random.choice(valid_moves)
        else:
            return None
