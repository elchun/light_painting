import time
import board
import neopixel

import random
import numpy as np


WIDTH = 11
HEIGHT = 14
NUM_PIXELS = WIDTH * HEIGHT

pixel_pin = board.D18
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin,
    NUM_PIXELS,
    brightness=0.3,
    auto_write=False,
    pixel_order=ORDER
)

def to_xy(x, y):
	if x % 2 == 0:
		return x * HEIGHT + y
	else:
		return x * HEIGHT + (HEIGHT - 1 - y)

def get_grid():
	y, x = np.meshgrid(np.arange(HEIGHT), np.arange(WIDTH))
	return x, y

def show_np(z):
	assert z.shape == (WIDTH, HEIGHT, 3)
	for x in range(WIDTH):
		for y in range(HEIGHT):
			p = tuple(z[x, y])
			pixels[to_xy(x, y)] = p
	pixels.show()


class MovingCircle():
	def __init__(self, freq, offset):
		self.centerx = WIDTH / 2
		self.centery = HEIGHT / 2
		self.freq = freq
		self.offset = offset

	def random_move_center(self, d):
		self.centerx += np.random.randn() * d
		self.centery += np.random.randn() * d
		self.centerx = (self.centerx + WIDTH) % WIDTH
		self.centery = (self.centery + HEIGHT) % HEIGHT

	def animate(self, t):
		self.random_move_center(0.6)

		t = t + self.offset
		x, y = get_grid()
		x0 = WIDTH / 2
		y0 = HEIGHT / 2
		dist = np.sqrt((x - self.centerx)**2 + (y - self.centery)**2) / WIDTH
		tt = (t % self.freq) / self.freq
		c = np.where((tt <= dist) & (dist <= (tt + 0.3)), 1, 0) * 100
		return c


class AnimateRGB():
	def __init__(self, R, G, B):
		self.R = R
		self.G = G
		self.B = B

	def show(self, t):
		t0 = (t // 3)
		if t % 3 == 0:
			rt, gt, bt = 0, 0, 0
		if t % 3 == 1:
			rt, gt, bt = 1, 0, 0
		if t % 3 == 2:
			rt, gt, bt = 1, 1, 0
		rt += t0
		gt += t0
		bt += t0
		c3 = np.stack([R.animate(rt), G.animate(gt), B.animate(bt)], axis=2)
		print(c3)
		show_np(c3)

# class MovingDot:
# 	def __init__(self, x, y, dx, dy):
# 		self.x = x
# 		self.y = y
# 		self.dx = dx
# 		self.dy = dy

# 	def animate(self, t):
# 		self.x += self.dx
# 		self.y += self.dy
# 		if self.x < 0 or self.x > HEIGHT:
# 			self.dx *= -1
# 		if self.y < 0 or self.y > WIDTH:
# 			self.dy *= -1

# 		x, y = get_grid


R = MovingCircle(freq=3, offset=3)
G = MovingCircle(freq=4, offset=5)
B = MovingCircle(freq=5, offset=10)

animator = AnimateRGB(R, G, B)

def draw(t):
#	x, y = get_grid()
	# x0 = WIDTH / 2
#	y0 = HEIGHT / 2
	# dist = np.sqrt((x - x0)**2 + (y - y0)**2) / WIDTH
#	dist = (dist - dist.min()) / (dist.max() - dist.min()) * 200
#	c = np.floor(dist).astype(np.int32)
	# tt = (t % 10) / 10
	# c = np.where((tt <= dist) & (dist <= (tt + 0.3)) , 1, 0) * 200

#	R.random_move_center(0.5)
#	G.random_move_center(0.5)
#	B.random_move_center(0.5)

#	c3 = np.stack([R.animate(t), G.animate(t), B.animate(t)], axis=2)
#	print(c3)
#	show_np(c3)

#	pixels.fill((0, 0, 0))
#	t = t % NUM_PIXELS
#	x = t // HEIGHT
#	y = t % HEIGHT
#	pixels[to_xy(x, y)] = (100, 100, 100)
#	pixels.show()
	animator.show(t)


t = 0

while True:
	draw(t)
	t += 1
	time.sleep(0.04)
