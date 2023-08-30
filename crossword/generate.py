import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for var in self.crossword.variables:
            for word in self.crossword.words:
                # If the length of the word is not equal to the length of the variable
                if len(word) != var.length:
                    # Remove the word from the domain of the variable
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # Initialize a boolean variable to keep track of whether a revision was made
        revised = False

        # If there is an overlap between the variables
        if self.crossword.overlaps[x, y] is not None:
            # Get the overlap
            i, j = self.crossword.overlaps[x, y]

            # Loop over each word in the domain of `x`
            for word_x in self.domains[x].copy():
                # Initialize a boolean variable to keep track of whether there is a possible corresponding value
                # for `y` in `self.domains[y]`
                possible_corresponding_value = False

                # Loop over each word in the domain of `y`
                for word_y in self.domains[y]:
                    # If the two words are not equal and the characters at the overlap are not equal
                    if word_x != word_y and word_x[i] != word_y[j]:
                        # Then there is a possible corresponding value for `y` in `self.domains[y]`
                        possible_corresponding_value = True

                # If there is no possible corresponding value for `y` in `self.domains[y]`
                if not possible_corresponding_value:
                    # Then remove the word from the domain of `x`
                    self.domains[x].remove(word_x)

                    # Mark that a revision was made
                    revised = True

        # Return whether a revision was made to the domain of `x`
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # If arcs is None
        if arcs is None:
            # Then initialize the queue of arcs
            queue = list()

            # Loop over each variable
            for var in self.crossword.variables:
                # Loop over each neighbor of the variable
                for neighbor in self.crossword.neighbors(var):
                    # Add the arc to the queue
                    queue.append((var, neighbor))

        else:
            # Initialize the queue of arcs
            queue = arcs

        while queue:
            # Get the first arc in the queue
            x, y = queue.pop(0)

            # If the arc is revised
            if self.revise(x, y):
                # If the domain of `x` is empty, then return False
                if not self.domains[x]:
                    return False

                # Loop over each neighbor of `x` that is not `y`
                for neighbor in self.crossword.neighbors(x) - {y}:
                    # Add the arc to the queue
                    queue.append((neighbor, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # Loop over each variable in the crossword
        for var in self.crossword.variables:
            # If the variable is not in the assignment, then the assignment is not complete
            if var not in assignment:
                return False

            # If the value of the variable is None, then the assignment is not complete
            if assignment[var] is None:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Loop over each variable in the assignment
        for var in assignment:
            # If the length of the word is not equal to the length of the variable, then the assignment is
            # not consistent
            if len(assignment[var]) != var.length:
                return False

            # Loop over each neighbor of the variable
            for neighbor in self.crossword.neighbors(var):
                # If the neighbor is in the assignment
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]

                    # If the characters at the overlap are not equal, then the assignment is not consistent
                    if assignment[var][i] != assignment[neighbor][j]:
                        return False

                    # If the two words are equal, then the assignment is not consistent
                    if assignment[var] == assignment[neighbor]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Initialize a dictionary to keep track of the number of values ruled out for neighboring variables
        ruled_out = dict()

        # Loop over each value in the domain of `var`
        for value in self.domains[var]:
            # Initialize a counter to keep track of the number of values ruled out for neighboring variables
            ruled_out[value] = 0

            # Loop over each neighbor of `var`
            for neighbor in self.crossword.neighbors(var):
                # If the neighbor is not in the assignment
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]

                    # Loop over each value in the domain of `neighbor`
                    for neighbor_value in self.domains[neighbor]:
                        # If the characters at the overlap are not equal
                        if value[i] != neighbor_value[j]:
                            # Then increment the counter
                            ruled_out[value] += 1

        # Return the values in the domain of `var` in order by the number of values they rule out
        # for neighboring variables
        return sorted(self.domains[var], key=lambda value: ruled_out[value])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Initialize a dictionary to keep track of the number of remaining values in the domain of each variable
        remaining_values = dict()

        # Loop over each variable in the crossword
        for var in self.crossword.variables:
            # If the variable is not in the assignment
            if var not in assignment:
                # Then add the variable to the dictionary
                remaining_values[var] = len(self.domains[var])

        # Get the variable with the minimum number of remaining values in its domain
        min_remaining_values = min(remaining_values.values())

        # Initialize a list to keep track of the variables with the minimum number of remaining values in their domains
        min_remaining_values_vars = list()

        # Loop over each variable in the crossword
        for var in self.crossword.variables:
            # If the variable is not in the assignment
            if var not in assignment:
                # If the variable has the minimum number of remaining values in its domain
                if remaining_values[var] == min_remaining_values:
                    # Append the variable to the list
                    min_remaining_values_vars.append(var)

        # If there is only one variable with the minimum number of remaining values in its domain, then return it
        if len(min_remaining_values_vars) == 1:
            return min_remaining_values_vars[0]

        # Initialize a dictionary to keep track of the degrees of each variable
        degrees = dict()

        # Loop over each variable in the crossword
        for var in self.crossword.variables:
            # If the variable is not in the assignment
            if var not in assignment:
                # Initialize a counter to keep track of the degree of the variable
                degrees[var] = len(self.crossword.neighbors(var))

        # Get the variable with the highest degree
        max_degree = max(degrees.values())

        # Initialize a list to keep track of the variables with the highest degree
        max_degree_vars = list()

        # Loop over each variable in the crossword
        for var in self.crossword.variables:
            # If the variable is not in the assignment
            if var not in assignment:
                # If the variable has the highest degree
                if degrees[var] == max_degree:
                    # Append the variable to the list
                    max_degree_vars.append(var)

        # If there is only one variable with the highest degree, then return it
        if len(max_degree_vars) == 1:
            return max_degree_vars[0]

        # Return any of the tied variables
        return max_degree_vars[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # If the assignment is complete, then return it
        if self.assignment_complete(assignment):
            return assignment

        # Get an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Loop over each value in the domain of the variable
        for value in self.order_domain_values(var, assignment):
            # Add the value to the assignment
            assignment[var] = value

            # If the value is consistent with the assignment
            if self.consistent(assignment):
                # Recursively call backtrack
                result = self.backtrack(assignment)

                # If the result is not None, then return it
                if result is not None:
                    return result

            # Remove the value from the assignment
            del assignment[var]

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
