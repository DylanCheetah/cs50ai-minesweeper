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
        # If the mine count is equal to the number of cells in the set, then all cells in the set are
        # mines
        if len(self.cells) == self.count:
            return self.cells
        
        # We don't know which cells are mines
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the mine count is 0, then all cells in the set are safe
        if not self.count:
            return self.cells

        # We don't know which cells are safe
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # if the cell is in the set, remove the cell which is a mine and decrease the mine count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If the cell is in the set, remove the cell which is safe
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
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Add the cell to the list of moves made and mark it as safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Calculate adjacent cells
        cells = []

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if ((i != cell[0] or j != cell[1]) and 
                    0 <= i < self.height and 0 <= j < self.width):
                    cells.append((i, j))

        if cell in [(0, 0), (7, 0), (7, 7), (0, 7)]:
            print(f"Neighbors: {cells}")

        # Add sentence regarding knowledge gained
        new_sentence = Sentence(cells, count)
        self.knowledge.append(new_sentence)

        # Remove known safe cells from the sentence
        for cell in self.safes:
            new_sentence.mark_safe(cell)

        # Remove known mines from the sentence
        for cell in self.mines:
            new_sentence.mark_mine(cell)

        # Mark additional cells as safe or mines based on inference until no more
        # inferences are possible
        done = False

        while not done:
            # Set done flag
            done = True

            # Check for resolved sentences
            resolved_sentences = []

            for sentence in self.knowledge:
                # Get known safe cells and mines
                safes = tuple(sentence.known_safes())
                mines = tuple(sentence.known_mines())

                # Mark known safe cells and mines
                for cell in safes:
                    self.mark_safe(cell)

                for cell in mines:
                    self.mark_mine(cell)

                # If the sentence has been resolved, queue it for removal and
                # clear done flag
                if len(safes) or len(mines) or not len(sentence.cells):
                    resolved_sentences.append(sentence)
                    done = False

            # Remove resolved sentences from knowledge base
            for sentence in resolved_sentences:
                self.knowledge.remove(sentence)

            # Check for sentences that are subsets of other sentences
            new_sentences = []
            resolved_sentences = []

            for sentence in self.knowledge:
                for sentence2 in self.knowledge:
                    # Ignore sentences that have the same cell sets
                    if sentence.cells == sentence2.cells:
                        continue

                    # Is the sentence a subset of the other sentence?
                    if sentence.cells.issubset(sentence2.cells):
                        # Add new sentence
                        new_sentence = Sentence(
                            sentence2.cells.difference(sentence.cells),
                            sentence2.count - sentence.count
                        )
                        new_sentences.append(new_sentence)

                        # Queue sentence2 for removal
                        resolved_sentences.append(sentence2)
                        done = False

            self.knowledge.extend(new_sentences)

            # Remove resolved sentences from knowledge base
            for sentence in resolved_sentences:
                try:
                    self.knowledge.remove(sentence)

                except ValueError:
                    pass # ignore this

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Find a safe move that hasn't been made yet
        moves = list(self.safes.difference(self.moves_made))

        if not len(moves):
            return None
        
        else:
            return moves[0]

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Generate set of all cells on the board
        moves = set()

        for i in range(self.width):
            for j in range(self.height):
                moves.add((i, j))

        # Remove cells that have been chosen previously or that are known mines
        moves.difference_update(self.moves_made, self.mines)

        # Return random cell from possible moves
        if len(moves):
            return random.choice(list(moves))
        
        else:
            return None
