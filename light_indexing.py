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
    render_matrix(drawing_3d)


