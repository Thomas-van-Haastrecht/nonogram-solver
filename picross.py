import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from display import display_grid


def picross_solve(rows, columns):
    # row and column size
    r = rows.shape[0]
    c = columns.shape[0]
    grid = np.zeros((r, c))

    # if a row or column has zeroes -> all crosses; only needs to be checked once, not in loop
    for i in range(0, r):
        if rows[i][0] == 0:
            for j in range(0, c):
                grid[i][j] = -1

    for i in range(0, c):
        if columns[i][0] == 0:
            for j in range(0, r):
                grid[j][i] = -1

    print(grid)

    # until grid is full; all values are assigned a mark or a cross
    while 0 in grid:
        # FILL SQUARES BASED ON OUTER VALUES

        # CROSS OUT UNREACHABLE SQUARES
        # cross out rows
        row_cross_out(rows, grid)
        print(grid)
        # cross out columns
        column_cross_out(columns, grid)

        # FIND SECTIONED AREAS
        # sectioned rows and columns

        for i in range(0, r):
            new_line = grid[i]
            # test once i hits 3 or 4 debug
            grid[i] = section_line(rows[i], new_line)
            # update grid

        for i in range(0, c):
            new_line = grid[:, i]
            grid[:, i] = section_line(columns[i], new_line)
            # update grid

        # sectioned columns

    print("final:\n", grid)
    display_grid(grid)


def row_cross_out(rows, grid):

    r = grid.shape[0]

    for row_num in range(0, r):
        # only perform calculations if row is not empty
        if rows[row_num][0] != 0:
            marks = 0
            for square in range(0, r):
                if grid[row_num][square] == 1:
                    marks += 1

            s = np.sum(rows[row_num])
            if s == marks:
                for square in range(0, r):
                    if grid[row_num][square] == 0:
                        grid[row_num][square] = -1


def column_cross_out(columns, grid):

    c = grid.shape[0]

    for col_num in range(0, c):
        # only perform calculations if row is not empty
        if columns[col_num][0] != 0:
            marks = 0
            for square in range(0, c):
                if grid[square][col_num] == 1:
                    marks += 1

            s = np.sum(columns[col_num])
            if s == marks:
                for square in range(0, c):
                    if grid[square][col_num] == 0:
                        grid[square][col_num] = -1


def sub_row_fill(row_values, row_size, row):

    shift = row_size - (np.sum(row_values) + len(row_values) - 1)
    index = 0
    # for each value in a given row
    for val in row_values:
        index += shift
        for i in range(0, val - shift):
            print(row, row_values, index, shift, row_size)
            row[index] = 1
            index += 1
        # add crosses between marks if values are set
        if shift == 0 and index < row_size:
            row[index] = -1
        index += 1

    # todo find extra marks through already existing marks

    return row


def section_line(line_vals, line):
    # define buckets
    # bucket indices cover whole array (may have more index pairs than there are buckets)
    bucket_indices = []
    buckets = []
    # adds whole row to buckets
    for value in line:
        buckets.append(value)
    # define bucket b
    b = []
    i = 0
    index_start = 0
    while i < len(buckets):
        # if empty, move from buckets to b
        if len(b) == 0:
            b.append(buckets[i])
            buckets.pop(i)
        # if first is cross, remove cross, update b, i
            if b[0] == -1:
                b.pop(0)
                index_start += 1
        # if next is mark or empty, move next from buckets to b
        elif buckets[i] != -1:
            b.append(buckets.pop(i))
        # if next is cross, remove cross, start new b, after inserting b back
        else:
            # remove cross
            buckets.pop(i)
            # add b into buckets and reset b
            buckets.insert(i, b)
            # update bucket indices
            bucket_indices.append([index_start, index_start + len(b) - 1])
            index_start += len(b) + 1
            b = []
            # increment i to continue from correct indices
            i += 1

    if len(b) > 0:
        buckets.append(b)
        bucket_indices.append([index_start, line.shape[0] - 1])

    # insert indices left -> right
    L = []
    r_index = 0
    for bucket in range(0, len(buckets)):
        B = buckets[bucket]
        size = len(B)
        #make list of indices that fit into bucket B
        left = []
        for i in range(r_index, len(line_vals)):
            if line_vals[i] <= size:
                size -= line_vals[i]
                left.append(r_index)
                r_index += 1
        L.append(left)

    # insert indices right-> left
    R = []
    r_index = len(line_vals) - 1
    for bucket in range(len(buckets) - 1, -1, -1):
        B = buckets[bucket]
        size = len(B)
        # make list of indices that fit into bucket B
        right = []
        for i in range(r_index, -1, -1):
            if line_vals[i] <= size:
                size -= line_vals[i]
                right.insert(0, r_index)
                r_index -= 1
        R.insert(0, right)

    # compare
    for i in range(0, len(L)):
        left = L[i]
        right = R[i]
        if left == right:
            # rows[row_num] initial state of row
            line_values = []
            for l_val in left:
                line_values.append(line_vals[l_val])
            sub_row_size = bucket_indices[i][1] - bucket_indices[i][0] + 1
            sub_line = sub_row_fill(line_values, sub_row_size, buckets[i])
            for x in range(bucket_indices[i][0], bucket_indices[i][1]+1):
                line[x] = sub_line[x - bucket_indices[i][0]]
            # print("Solve: ", line)
            # l and r contain the same elements
            # this means that this subset of the row can be treated separately
            # for buckets[i], l contains the indices of row values that can be considered inside buckets[i]
            # treat as row
            print(left, right, buckets, bucket_indices)
    return line


hat_r = np.array([[0], [3], [3], [3], [5]])
hat_c = np.array([[1], [4], [4], [4], [1]])

key_r = np.array([[3], [1, 1], [3], [1], [2]])
key_c = np.array([[0], [3], [1, 3], [3, 1], [0]])

# i = 1
# while i < len(key_c):
#     print(len(key_c))
#     key_c = np.delete(key_c, 0)

##grid = np.zeros((5, 5))
#rows = np.array([[0], [3], [3], [3], [5]])
# grid[3,3] = -1

# section_rows(rows, grid)
picross_solve(key_r, key_c)
