import sys
import random
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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        for key, value in (self.domains).items():
            for x in list(value):
                if len(x) != key.length:
                    self.domains[key].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]  # Generate turple cordinate of intersection
        if overlap != None:
            for xvalue in list(self.domains[x]):
                if any(xvalue[overlap[0]] == yvalue[overlap[1]] for yvalue in self.domains[y]):
                    pass
                else:
                    self.domains[x].remove(xvalue)
                    revised = True
            return revised
        else:
            return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = set()
            for x in self.domains:
                for y in self.domains:
                    # Check for known intersection amongst variables
                    if x != y and self.crossword.overlaps[x, y] != None:
                        queue.add((x, y))  # Queue of all arcs (variables that intersect)
        else:
            queue = set(arcs)  # Queue of arcs given
        '''
        ac-3 algorithm
        '''
        initial_queue = queue.copy()
        while len(queue) > 0:
            for arc in list(queue):
                x, y = arc
                queue.remove(arc)
                if self.revise(x, y):
                    if len(self.domains[x]) == 0:
                        return False
                    for i in initial_queue:
                        if x == i[1]:
                            queue.add(i)
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.domains) == len(assignment) and all(value != None for value in assignment.values()):
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check if distinct
        if len(assignment.values()) != len(set(assignment.values())):
            return False

        # Check for correct length
        for key, value in assignment.items():
            if len(value) != key.length:
                return False

        # No conflict between variables
        No_conflict = True
        for x in assignment:
            for y in assignment:
                if x != y:
                    overlap = self.crossword.overlaps[x, y]
                    if overlap:
                        if assignment[x][overlap[0]] != assignment[y][overlap[1]]:
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Get all domain values for the variable in a list
        unordered_value_list = []
        for value in self.domains[var]:
            unordered_value_list.append(value)

        # Get list of unassigned variables
        domain_var = set()
        for varr in self.domains:
            domain_var.add(varr)

        assignment_var = set()
        for varr in assignment:
            assignment_var.add(varr)

        unassigned_var = domain_var - assignment_var

        # Dict of values and num of constraints
        constraint_num = {}
        for value in unordered_value_list:
            constraint_num[value] = 0

        if len(unassigned_var) != 0:
            for varr in unassigned_var:  # loop throgh variables not in assignment
                if var != varr:
                    overlap = self.crossword.overlaps[var, varr]
                    if overlap:  # Check for overlaps
                        for value1 in unordered_value_list:  # loop through unordered value list of given var
                            # loop through value list of considered var
                            for value2 in self.domains[varr]:
                                if value1[overlap[0]] != value2[overlap[1]]:
                                    constraint_num[value1] += 1

        ordered_LCV = sorted(constraint_num, key=constraint_num.get)
        return ordered_LCV

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.

        """
        # Get list of unassigned variables
        domain_var = set()
        for varr in self.domains:
            domain_var.add(varr)

        assignment_var = set()
        for varr in assignment:
            assignment_var.add(varr)

        unassigned_var = domain_var - assignment_var
        # Maps variables to the length of domain they have
        num_dom = {}
        for var in unassigned_var:
            num_dom[var] = len(self.domains[var])
        min_num = min(num_dom.values())

        # Add variable(s) with the least domain number
        MRV_dom = []
        for var in num_dom:
            if num_dom[var] == min_num:
                MRV_dom.append(var)

        if len(MRV_dom) == 1:
            return MRV_dom[0]

        # Using degree heuristics
        elif len(MRV_dom) > 1:
            degree_num = {value: 0 for value in MRV_dom}
            for var1 in MRV_dom:
                for var2 in unassigned_var:
                    if var1 != var2 and self.crossword.overlaps[var1, var2]:
                        degree_num[var1] += 1
            max_degree_num = max(degree_num.values())

            # Create list with max degree
            max_degree = []
            for key, value in degree_num.items():
                if value == max_degree_num:
                    max_degree.append(key)
            if len(max_degree) == 1:
                return max_degree[0]
            else:
                return max_degree[random.randint(0, len(max_degree)-1)]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            if len(value) == var.length:
                assignment[var] = value
                result = self.backtrack(assignment)
                if self.consistent(result):
                    return result
                assignment.pop(var)
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
