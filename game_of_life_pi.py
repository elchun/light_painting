import time
import board
import neopixel
import numpy as np

pixel_pin = board.D18
num_pixels=154
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

n_rows = 14
n_cols = 11

def flip_to_snake(matrix: np.ndarray):
    # Set every other column to the reverse
    output = matrix.copy()
    output[:, 1::2, :] = output[::-1, 1::2, :]
    return output

def snake_to_arr(matrix: np.ndarray):
    # Flip x and y, then reshape to flatten
    output = matrix.copy()
    output = np.einsum("xyz->yxz", output)
    output = output.reshape(-1, output.shape[-1])
    return output

def render_matrix(matrix: np.ndarray):
    output = flip_to_snake(matrix)
    output = snake_to_arr(output)

    for i in range(len(pixels)):
        pixels[i] = output[i]
    pixels.show()

def generate_dummy():
    matrix = np.arange(0, 154).reshape(11, 14, 1)
    matrix = np.einsum("xyz->yxz", matrix)
    zeros = np.zeros((14, 11, 1)).astype(int)
    matrix = np.concatenate([matrix, zeros, zeros], axis=2)
    return matrix

def game_of_life(n_rows, n_cols):
    n_start = 80
    MAX_STEPS = 50
    color = np.random.randint(0, 200, 3).reshape(1, 1, 3)
    # r = np.random.randint(0, 255, 1)
    # g = np.random.randint(0, r, 1)
    # b = np.random.randint(0, g, 1)
    # color = np.array([r, g, b]).squeeze().reshape(1, 1, 3)
    board = np.zeros((n_rows, n_cols)).astype(int)

    board = initialize(board, np.random.randint(60, board.shape[0] * board.shape[1], 1)[0])


    for i in range(MAX_STEPS):
        last_board = board.copy()
        board_neighbors = get_neighbors(board)
        board = run_step(board, board_neighbors)

        board_renderable = board[:, :, None] * color
        render_matrix(board_renderable)

        if np.sum(board) == 0:
            return False

        time.sleep(0.05)
    return True


def get_neighbors(board):
    # Do convolution with 3x3 1s array
    output_arr = np.zeros((board.shape[0], board.shape[1])).astype(int)
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            for i_offset in (-1, 0, 1):
                for j_offset in (-1, 0, 1):
                    if i_offset == 0 and j_offset == 0:
                        continue
                    i_n_idx = i + i_offset
                    j_n_idx = j + j_offset

                    if i_n_idx < 0 or i_n_idx >= board.shape[0] or j_n_idx < 0 or j_n_idx >= board.shape[1]:
                        continue
                    output_arr[i, j] += board[i_n_idx, j_n_idx]
    return output_arr

def run_step(board, neighbors):
    # Any live cell with fewer than two live neighbours dies, as if by underpopulation.
    # Any live cell with two or three live neighbours lives on to the next generation.
    # Any live cell with more than three live neighbours dies, as if by overpopulation.
    death_mask = (board > 0) & (neighbors != 2)

    # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
    life_mask = (board == 0) & (neighbors == 3)
    board[death_mask] = 0
    board[life_mask] = 1
    return board


def initialize(board, n_seeds):
    n_rows, n_cols = board.shape
    start_pixels = np.stack((np.random.randint(0, n_rows, n_seeds), np.random.randint(0, n_cols, n_seeds)), axis=1)
    for x, y in start_pixels:
        board[x, y] = 1
    return board



drawing = [
        0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,
        0,1,0,0,0,0,1,0,0,1,0,
        0,1,0,0,0,0,1,0,0,1,0,
        0,1,0,0,0,0,1,0,0,0,0,
        0,1,0,0,0,0,1,0,0,1,0,
        0,1,1,1,1,1,1,0,0,1,0,
        0,1,0,0,0,0,1,0,0,1,0,
        0,1,0,0,0,0,1,0,0,1,0,
        0,1,0,0,0,0,1,0,0,1,0,
        0,1,0,0,0,0,1,0,0,1,0,
        0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,
        ]
drawing = np.array(drawing) * 50
drawing = drawing.reshape((14, 11, 1))
zeros = np.zeros((14, 11, 1)).astype(int)
drawing_3d = np.concatenate([drawing, zeros, zeros], axis=2)


while True:
    # render_matrix(drawing_3d)
    game_of_life(14, 11)


