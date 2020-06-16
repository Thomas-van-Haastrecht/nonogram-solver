import pygame
import os
import time
import numpy as np

# Set window position close to top left
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50, 50)

CELL_SIZE = 48
BORDER_SIZE = 10

MARK = pygame.image.load('game_symbols/pygame_mark.png')
BLANK = pygame.image.load('game_symbols/pygame_blank.png')
CROSS = pygame.image.load('game_symbols/pygame_cross.png')
TEMP = pygame.image.load('game_symbols/pygame_temp.png')


def picross_init(rows, cols):
    # Pull grid size from input
    r = len(rows)
    c = len(cols)

    set_len = [len(row) for row in rows]
    set_len.extend([len(column) for column in cols])
    m = max(set_len)
    print(m)

    # Initialize game window to be appropriate size
    pygame.init()
    height = (r + m) * CELL_SIZE
    width = (c + m) * CELL_SIZE
    board = pygame.display.set_mode((height + 2 * BORDER_SIZE, width + 2 * BORDER_SIZE))
    board.fill((255, 255, 255))
    pygame.display.set_caption('Picross')

    # Draw all necessary squares into the grid
    x_position = m * CELL_SIZE + BORDER_SIZE
    y_position = m * CELL_SIZE + BORDER_SIZE
    pygame.draw.rect(board, (0, 0, 0), (x_position, y_position, r * CELL_SIZE, c * CELL_SIZE), 2)

    for i in range(r):
        for j in range(c):
            pygame.draw.rect(board, (0, 0, 0), (x_position + i * CELL_SIZE, y_position + j * CELL_SIZE, CELL_SIZE,
                                                CELL_SIZE), 1)

    running = True

    pygame.font.init()
    font = pygame.font.Font('JAi_____.TTF', 32)

    x_position = (m - 0.5) * CELL_SIZE + BORDER_SIZE
    y_position = (m + 0.5) * CELL_SIZE + BORDER_SIZE
    for i, row in enumerate(rows):
        for j, run in enumerate(row):
            text = font.render(str(run), True, (0, 0, 0))
            pos = text.get_rect(center=(x_position - j * CELL_SIZE, y_position + i * CELL_SIZE))
            board.blit(text, pos)

    x_position = (m + 0.5) * CELL_SIZE + BORDER_SIZE
    y_position = (m - 0.5) * CELL_SIZE + BORDER_SIZE
    for i, col in enumerate(cols):
        for j, run in enumerate(col):
            text = font.render(str(run), True, (0, 0, 0))
            pos = text.get_rect(center=(x_position + i * CELL_SIZE, y_position - j * CELL_SIZE))
            board.blit(text, pos)

    # board.blit(pygame.image.load('pygame_cross.png'), (m * CELL_SIZE + BORDER_SIZE, m * CELL_SIZE + BORDER_SIZE))

    board_copy = board.copy()

    # add cursor after copy
    pygame.draw.rect(board, (255, 200, 0), (m * CELL_SIZE + BORDER_SIZE, m * CELL_SIZE + BORDER_SIZE, CELL_SIZE, CELL_SIZE), 3)

    pygame.display.update()

    grid = np.array(np.zeros((r, c)))

    cursor_position = [0, 0]
    marking = False
    crossing = False
    temping = False

    removing = False

    clock = pygame.time.Clock()

    while running:

        clock.tick(12)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_LEFT]:
            cursor_position[0] -= 1
            if cursor_position[0] < 0:
                cursor_position[0] = c - 1

        elif keys_pressed[pygame.K_RIGHT]:
            cursor_position[0] += 1
            if cursor_position[0] >= c:
                cursor_position[0] = 0

        elif keys_pressed[pygame.K_UP]:
            cursor_position[1] -= 1
            if cursor_position[1] < 0:
                cursor_position[1] = r - 1

        elif keys_pressed[pygame.K_DOWN]:
            cursor_position[1] += 1
            if cursor_position[1] >= r:
                cursor_position[1] = 0

        # Updating the game grid

        if keys_pressed[pygame.K_z] or keys_pressed[pygame.K_x] or keys_pressed[pygame.K_c]:
            # if previously pressed and no longer pressed, booleans are reset
            if marking and not keys_pressed[pygame.K_z]:
                marking = False
                removing = False
            if crossing and not keys_pressed[pygame.K_x]:
                crossing = False
                removing = False
            if temping and not keys_pressed[pygame.K_c]:
                temping = False
                removing = False

            current = grid[cursor_position[0]][cursor_position[1]]

            if marking or crossing or temping:
                if marking and keys_pressed[pygame.K_z]:
                    if removing and current == 1:
                        current = 0
                    elif not removing and current == 0 or current == -2:
                        current = 1

                elif crossing and keys_pressed[pygame.K_x]:
                    if removing and current == -1:
                        current = 0
                    elif not removing and current == 0 or current == -2:
                        current = -1

                elif temping and keys_pressed[pygame.K_c]:
                    if removing and current == -2:
                        current = 0
                    elif not removing and current == 0:
                        current = -2


            elif keys_pressed[pygame.K_z] or keys_pressed[pygame.K_x] or keys_pressed[pygame.K_c]:
                if keys_pressed[pygame.K_z]:
                    if current == 0 or current == -2:
                        current = 1
                    elif current == 1:
                        current = 0
                        removing = True
                    marking = True

                elif keys_pressed[pygame.K_x]:
                    if current == 0 or current == -2:
                        current = -1
                    elif current == -1:
                        current = 0
                        removing = True
                    crossing = True

                elif keys_pressed[pygame.K_c]:
                    if current == 0:
                        current = -2
                    elif current == -2:
                        current = 0
                        removing = True
                    temping = True

            # update board
            update_board(board_copy, cursor_position, m, current)
            grid[cursor_position[0]][cursor_position[1]] = current

        else:
            marking = False
            crossing = False
            temping = False
            removing = False

        board.blit(board_copy, (0, 0))
        pygame.draw.rect(board, (0, 255, 100), ((m + cursor_position[0]) * CELL_SIZE + BORDER_SIZE, (m + cursor_position[1]) * CELL_SIZE + BORDER_SIZE, CELL_SIZE, CELL_SIZE), 3)

        pygame.display.update()

    print(grid)
    pygame.quit()


def update_board(board, cursor_position, m, img):
    if img == 1:
        symbol = MARK
    elif img == 0:
        symbol = BLANK
    elif img == -1:
        symbol = CROSS
    elif img == -2:
        symbol = TEMP
    board.blit(BLANK, ((m + cursor_position[0]) * CELL_SIZE + BORDER_SIZE,
                        (m + cursor_position[1]) * CELL_SIZE + BORDER_SIZE))
    board.blit(symbol, ((m + cursor_position[0]) * CELL_SIZE + BORDER_SIZE,
                        (m + cursor_position[1]) * CELL_SIZE + BORDER_SIZE))


if __name__ == "__main__":
    sa10_r = [[1, 1, 2, 1], [1, 1, 1], [2], [1, 2, 1, 1], [1, 1, 2],
              [1, 1, 1, 1], [1, 1], [2, 1, 1], [1, 1, 2], [1, 1, 1, 1, 1]]

    sa10_c = [[1, 1, 2, 1], [2, 1, 1], [1, 1, 1], [1, 1, 2], [1, 2],
              [1, 1, 1, 1], [2, 1, 1, 1], [2, 2], [1], [1, 1, 1, 1, 1]]

    picross_init(sa10_r, sa10_c)
