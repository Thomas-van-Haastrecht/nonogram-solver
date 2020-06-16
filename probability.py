__author__ = "Thomas van Haastrecht"
__credits__ = ["Thomas van Haastrecht"]

import numpy as np
from itertools import combinations_with_replacement
from display import display_grid


def solve(rows, columns):
    r = len(rows)
    c = len(columns)
    grid = np.zeros((r, c))
    probability_grid = np.add(np.zeros((r, c)), 0.5)

    # if a row or column has zeroes -> all crosses; only needs to be checked once, not in loop
    for i in range(r):
        if rows[i][0] == 0:
            for j in range(c):
                grid[i][j] = -1
                probability_grid[i][j] = 0

    for i in range(c):
        if columns[i][0] == 0:
            for j in range(r):
                grid[j][i] = -1
                probability_grid[j][i] = 0

    # find different possible solutions for each line (row or column)
    while 0 in grid:
        previous_grid = grid.copy()
        for i in range(r):
            line = grid[i]
            probabilities_for_line = probability_grid[i]
            # only perform calculations for probabilities if row is not complete
            if 0 in line:
                update_probabilities(rows[i], line, probabilities_for_line, True)
            # update grid
            update_grid(line, probabilities_for_line)

        for i in range(c):
            line = grid[:, i]
            probabilities_for_line = probability_grid[:, i]
            # only perform calculations for probabilities if column is not complete
            if 0 in line:
                update_probabilities(columns[i], line, probabilities_for_line, False)
            # update grid
            update_grid(line, probabilities_for_line)

        # if checking all rows and columns individually yielded no extra results, use contradiction method
        if np.array_equal(grid, previous_grid):
            # updates the grid with contradiction search. If a contradiction is found or puzzle is solved, returns
            grid = contradiction_search(grid, probability_grid, rows, columns)

    return grid


def update_grid(grid_line, probability_line):
    for i in range(len(grid_line)):
        if probability_line[i] == 1:
            grid_line[i] = 1
        if probability_line[i] == 0:
            grid_line[i] = -1


# calculate probabilities of grid spaces (one line at a time)
def update_probabilities(sets, line, probabilities, row_pass):
    # calculate shift value
    shift = len(line) - (np.sum(sets) + len(sets) - 1)

    # calculate all possible line possibilities
    possible_lines = distribute_zeros(sets, len(sets) + 1, shift)

    # eliminate all invalid lines, due to existing line info
    # invalid: pos has 1, where line is -1; vice versa
    remove_invalid(possible_lines, line)

    # for each index count number of marks in possible lines and calculate probability
    for i in range(len(probabilities)):
        # only calculate probabilities of undecided spaces
        if probabilities[i] != 0 and probabilities[i] != 1:
            prob_count = 0
            for l in possible_lines:
                if l[i] == 1:
                    prob_count += 1
            # calculate probability and update probability index
            prob_count = prob_count / len(possible_lines)
            if row_pass or prob_count == 0 or prob_count > probabilities[i]:
                probabilities[i] = prob_count


# add all possibilities of "r zeros distributed into n(=r+1) containers" into distributions
def distribute_zeros(sets, n, k):
    # initialize list to return all possible lines
    possible_lines = []

    # initialize all possible combinations to use to make possible lines
    n_list = [i for i in range(n)]
    combinations = list(combinations_with_replacement(n_list, k))
    combinations = [list(i) for i in combinations]

    # create array of marks and crosses, along with indices of where each set starts
    base_line_p = []
    p_index = []
    for l in range(len(sets)):
        if l > 0:
            base_line_p.append(-1)
        for s in range(sets[l]):
            if s == 0:
                p_index.append(len(base_line_p))
            base_line_p.append(1)

    # insert each zero in correct position, using indices and position of zeros
    for c in combinations:
        line_p = base_line_p.copy()
        for i in range(len(c)):
            if c[i] == len(p_index):
                line_p.append(-1)
            else:
                line_p.insert(p_index[c[i]] + i, -1)

        possible_lines.append(line_p)

    return possible_lines


def remove_invalid(possible_lines, line):
    # run through each possible line
    current_line = 0
    while current_line < len(possible_lines):
        # run through each index in each individual line
        line_removed = False
        for i in range(len(possible_lines[current_line])):
            # compare possible line and actual line at each index to see if it is valid
            if abs(possible_lines[current_line][i] - line[i]) > 1:
                line_removed = True
        if line_removed:
            possible_lines.pop(current_line)
            # maintain correct line index if a line is removed
            current_line -= 1
        current_line += 1


def contradiction_search(grid, probability_grid, rows, columns):
    # find highest probability of uncertain position
    max_prob = 0
    attempt_coordinates = []

    for i in range(len(probability_grid)):
        for j in range(len(probability_grid[0])):
            if 1 > probability_grid[i][j] > max_prob:
                max_prob = probability_grid[i][j]
                attempt_coordinates = [i, j]

    current_row = [attempt_coordinates[0]]
    current_column = [attempt_coordinates[1]]

    # create copies of grid. This keeps the original unchanged, in case a contradiction is found
    attempt_grid = grid.copy()
    attempt_probability = probability_grid.copy()
    # mark attempt location
    attempt_grid[attempt_coordinates[0]][attempt_coordinates[1]] = 1
    attempt_probability[attempt_coordinates[0]][attempt_coordinates[1]] = 1

    # check if row and column that have been updated has other solutions

    while len(current_row) > 0:
        r = current_row[0]
        c = current_column[0]

        line = attempt_grid[r]
        probabilities_for_line = attempt_probability[r]
        # attempt solving with guess in place
        try:
            update_probabilities(rows[r], line, probabilities_for_line, True)
            # update grid
            for i in range(len(line)):
                if probabilities_for_line[i] == 1 and line[i] != 1:
                    line[i] = 1
                    current_row.append(r)
                    current_column.append(i)
                if probabilities_for_line[i] == 0 and line[i] != -1:
                    line[i] = -1
                    current_row.append(r)
                    current_column.append(i)
        # if contradiction is found, returns proper value
        except ZeroDivisionError:
            # contradiction
            grid[attempt_coordinates[0]][attempt_coordinates[1]] = -1
            probability_grid[attempt_coordinates[0]][attempt_coordinates[1]] = 0
            return grid

        line = attempt_grid[:, c]
        probabilities_for_line = attempt_probability[:, c]
        # attempt solving with guess in place
        try:
            update_probabilities(columns[c], line, probabilities_for_line, False)
            # update grid and column
            for i in range(len(line)):
                if probabilities_for_line[i] == 1 and line[i] != 1:
                    line[i] = 1
                    current_row.append(i)
                    current_column.append(c)
                if probabilities_for_line[i] == 0 and line[i] != -1:
                    line[i] = -1
                    current_row.append(i)
                    current_column.append(c)
        # if contradiction is found, returns proper value
        except ZeroDivisionError:
            # contradiction
            grid[attempt_coordinates[0]][attempt_coordinates[1]] = -1
            probability_grid[attempt_coordinates[0]][attempt_coordinates[1]] = 0
            return grid

        # remove index of current position for next iteration
        current_row.pop(0)
        current_column.pop(0)

    # check if grid is complete
    if 0 in attempt_grid:
        # if no contradiction is found, and grid is not completed new attempt must be made
        grid = contradiction_search(attempt_grid, attempt_probability, rows, columns)
    else:
        grid = attempt_grid

    return grid


# function that runs the solve function on many different puzzles.
# Running all functions may take some time and will open many images
# Using the exit(1) call will stop the program anywhere if you only want to see some things
# Alternatively, commenting out code will also stop it from running
def test_functions():
    # solving simple 5 x 5 puzzles
    print("Testing 5 x 5 puzzles, Hat and Key...\n")

    hat_r = [[0], [3], [3], [3], [5]]
    hat_c = [[1], [4], [4], [4], [1]]

    key_r = [[3], [1, 1], [3], [1], [2]]
    key_c = [[0], [3], [1, 3], [3, 1], [0]]

    g = solve(hat_r, hat_c)
    print("hat grid:\n", g, "\n")
    display_grid(g, hat_r, hat_c)

    g = solve(key_r, key_c)
    print("key grid:\n", g)
    display_grid(g, key_r, key_c)

    # Initializes grid for contradiction search. Uses the same board state as the example in the paper
    # probability of the position to be tested is artificially raised, so that it is chosen as the attempt
    print("\n\n\nTesting contradiction search...\n")
    con_r = [[1, 2], [1], [1], [3], [2], [2]]
    con_c = [[3], [1], [2], [2], [1, 1], [1, 1]]
    con_grid = np.zeros((6, 6))
    con_grid[0][1] = con_grid[0][3] = con_grid[1][4] = con_grid[1][5] = con_grid[2][2] = -1
    con_grid[0][4] = con_grid[0][5] = 1
    con_prob = np.add(np.zeros((6, 6)), 0.5)
    con_prob[0][1] = con_prob[0][3] = con_prob[1][4] = con_prob[1][5] = con_prob[2][2] = 0
    con_prob[0][4] = con_prob[0][5] = 1
    con_prob[0][2] = 0.75

    contradiction_search(con_grid, con_prob, con_r, con_c)
    print("contradiction grid:\n", con_grid)

    # Eagle picture (25 x 25)
    print("\n\n\nTesting 25 x 25 puzzle, Eagle...\n")

    eagle_r = [[7], [11], [3, 3], [3, 3], [4, 2], [3, 2], [2, 1, 2], [3, 6, 1], [2, 2, 1, 2], [1, 1, 6, 1],
               [2, 2, 1, 2], [3, 2, 2, 2], [3, 2, 4, 1, 1], [2, 4, 1, 1, 2, 2, 1], [2, 12, 2, 1], [1, 1, 15, 1],
               [1, 2, 2, 6, 2, 1], [5, 5, 1, 1], [4, 5, 3], [3, 6, 2], [3, 1, 5, 1], [2, 1, 2, 2, 2], [1, 5, 1, 2],
               [1, 5, 1, 2], [7, 1, 2]]

    eagle_c = [[6, 6, 7], [6, 4, 5, 1], [4, 1, 3, 5, 3], [3, 2, 4, 4], [2, 1, 3], [1, 2, 4], [2, 2, 1, 6], [2, 6, 3],
               [2, 12], [2, 12], [2, 7], [2, 2, 8], [2, 1, 4, 5], [2, 1, 3, 3], [2, 3, 1, 2], [2, 9], [1, 1, 1, 2, 2],
               [2, 2, 1, 2], [2, 1, 1, 1], [2, 2, 3], [3, 3], [2, 2, 2], [2, 1, 4], [2, 2], [6]]

    g = solve(eagle_r, eagle_c)
    print("Eagle grid:\n", g)
    display_grid(g, eagle_r, eagle_c)

    # Solving multiple solution problems
    print("\n\n\nTesting puzzles with multiple valid solutions (10 x 10, 15 x 15, 20 x 20, 25 x 25)...\n")

    sa25_r = [[2, 1, 2, 2, 1, 1, 1, 1], [1, 1, 1, 1, 1, 2, 1], [2, 1, 1, 1, 1], [1, 2, 1, 1, 1, 1, 1],
              [1, 1, 2, 1, 1, 1, 1],
              [3, 1, 1, 1, 1, 1, 2], [1, 1, 1, 1, 1, 1], [2, 1, 1, 1, 2], [1, 1, 2, 1, 1, 1, 1, 2],
              [1, 1, 1, 1, 1, 1, 1],
              [1, 1, 1, 2], [1, 1, 2, 1, 1, 2], [1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1],
              [1, 1, 1, 1, 1], [1, 1, 2, 1, 1, 1], [2, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 2, 3, 2, 1],
              [1, 1, 2, 1], [1, 1, 1, 1, 3, 2, 1, 1], [1, 1, 1, 2, 1, 1], [2, 1, 1, 1, 2, 1, 1, 1],
              [2, 1, 1, 1, 2, 1, 1]]

    sa25_c = [[1, 1, 2, 1, 1, 1, 2, 1, 1], [1, 2, 1, 1, 1, 1, 2, 1, 2], [1, 3, 1, 1, 1, 2], [1, 1, 2, 1, 1, 1],
              [1, 2, 1, 1, 1, 1],
              [1, 1, 1, 1, 1, 1], [2, 1, 1, 1, 1, 1, 2, 1, 1], [2, 2, 1, 1], [1, 1, 2, 1, 2],
              [1, 1, 1, 1, 1, 1, 1, 2, 1],
              [1, 1, 1, 1, 2, 1, 1], [1, 1, 1, 1, 1, 1], [1, 1, 2, 1, 1], [1, 1, 2, 1, 1], [1, 1, 1, 2, 1, 1, 1, 2],
              [1, 1, 1, 1, 2], [1, 1, 1, 1, 1], [1, 2, 2, 1, 2], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 2, 1, 1],
              [1, 1], [1, 2, 1, 1], [1, 2, 2, 1, 1, 1, 1, 1, 1], [1, 1, 1, 2, 1, 1], [1, 1, 2, 1, 1, 1, 1]]

    sa20_r = [[2, 1, 2, 2, 1, 1], [1, 1, 1, 1, 1, 2], [2, 1, 1, 1], [1, 2, 1, 1, 1, 1], [1, 1, 2, 1, 1, 1],
              [3, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [2, 1, 1, 1], [1, 1, 2, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1],
              [1, 1, 1], [1, 1, 2, 1, 1], [1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1],
              [1, 1, 1, 1], [1, 1, 2, 1, 1], [2, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [1, 2, 3, 2]]

    sa20_c = [[1, 1, 2, 1, 1, 1, 2], [1, 2, 1, 1, 1, 1, 2, 1], [1, 3, 1, 1], [1, 1, 2, 1, 1], [1, 2, 1, 1, 1],
              [1, 1, 1, 1, 1], [2, 1, 1, 1, 1, 1, 2], [2, 2, 1], [1, 1, 2, 1], [1, 1, 1, 1, 1, 1, 1, 1],
              [1, 1, 1, 1, 2], [1, 1, 1, 1], [1, 1, 2, 1], [1, 1, 2, 1], [1, 1, 1, 2, 1, 1],
              [1, 1, 1], [1, 1, 1, 1], [1, 2, 2, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 2]]

    sa15_r = [[1, 1, 2, 2, 1], [1, 1, 1, 1, 1], [2, 1], [1, 2, 1, 1, 1], [1, 1, 2, 1, 1],
              [1, 1, 1, 1, 1], [1, 1, 1, 1], [2, 1, 1], [1, 1, 2, 1, 1], [1, 1, 1, 1, 1, 1],
              [1], [1, 1, 2, 1, 1], [1], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1]]

    sa15_c = [[1, 1, 2, 1, 1, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 2], [1, 2, 1],
              [1, 1, 1, 1], [2, 1, 1, 1, 1, 1], [2, 2, 1], [1, 1], [1, 1, 1, 1, 1, 1],
              [1, 1, 1], [1, 1, 1, 1], [1, 1, 2], [1, 1, 2, 1], [1, 1, 1, 2]]

    sa10_r = [[1, 1, 2, 1], [1, 1, 1], [2], [1, 2, 1, 1], [1, 1, 2],
              [1, 1, 1, 1], [1, 1], [2, 1, 1], [1, 1, 2], [1, 1, 1, 1, 1]]

    sa10_c = [[1, 1, 2, 1], [2, 1, 1], [1, 1, 1], [1, 1, 2], [1, 2],
              [1, 1, 1, 1], [2, 1, 1, 1], [2, 2], [1], [1, 1, 1, 1, 1]]

    g = solve(sa10_r, sa10_c)
    print("10 x 10 grid:\n", g)
    display_grid(g, sa10_r, sa10_c)

    g = solve(sa15_r, sa15_c)
    print("\n15 x 15 grid:\n", g)
    display_grid(g, sa15_r, sa15_c)

    g = solve(sa20_r, sa20_c)
    print("\n20 x 20 grid:\n", g)
    display_grid(g, sa20_r, sa20_c)

    g = solve(sa25_r, sa25_c)
    print("\n25 x 25 grid:\n", g)
    display_grid(g, sa25_r, sa25_c)


if __name__ == "__main__":
    test_functions()
