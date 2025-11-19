import time
import board
import neopixel
import random
import numpy as np
from collections import deque
import sys
import termios
import tty
import threading

# Grid setup
WIDTH = 11
HEIGHT = 14
NUM_PIXELS = WIDTH * HEIGHT

# NeoPixel setup
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
    """Convert 2D coordinates to 1D LED strip index"""
    if x % 2 == 0:
        return x * HEIGHT + y
    else:
        return x * HEIGHT + (HEIGHT - 1 - y)

def show_np(z):
    """Display a numpy array on the LED matrix"""
    assert z.shape == (WIDTH, HEIGHT, 3)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            p = tuple(z[x, y].astype(int))
            pixels[to_xy(x, y)] = p
    pixels.show()


class KeyboardInput:
    """Handle keyboard input in a non-blocking way"""
    def __init__(self):
        self.key = None
        self.running = True
        
    def getch(self):
        """Get a single character from stdin"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def listen(self):
        """Listen for keyboard input in a separate thread"""
        while self.running:
            try:
                self.key = self.getch()
            except:
                pass
    
    def start(self):
        """Start the keyboard listener thread"""
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()
    
    def get_key(self):
        """Get and clear the last pressed key"""
        key = self.key
        self.key = None
        return key


class SnakeGame:
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Initialize/reset the game"""
        # Start snake in the middle
        start_x = WIDTH // 2
        start_y = HEIGHT // 2
        self.snake = deque([(start_x, start_y)])
        
        # Initial direction (moving right)
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        
        # Game state
        self.food = None
        self.spawn_food()
        self.score = 0
        self.game_over = False
        self.speed = 0.15  # seconds per frame
    
    def spawn_food(self):
        """Spawn food at a random location not occupied by snake"""
        while True:
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def change_direction(self, new_direction):
        """Queue a direction change (prevents reversing into self)"""
        # Can't reverse direction
        if (new_direction[0] + self.direction[0] == 0 and 
            new_direction[1] + self.direction[1] == 0):
            return
        self.next_direction = new_direction
    
    def update(self):
        """Update game state for one frame"""
        if self.game_over:
            return
        
        # Update direction
        self.direction = self.next_direction
        
        # Get new head position
        head_x, head_y = self.snake[0]
        new_head = (
            (head_x + self.direction[0]) % WIDTH,
            (head_y + self.direction[1]) % HEIGHT
        )
        
        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            return
        
        # Add new head
        self.snake.appendleft(new_head)
        
        # Check if food eaten
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
            # Speed up slightly
            self.speed = max(0.05, self.speed - 0.005)
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
    def render(self):
        """Render the game state to the LED matrix"""
        # Create empty grid
        grid = np.zeros((WIDTH, HEIGHT, 3), dtype=int)
        
        if self.game_over:
            # Flash red on game over
            if int(time.time() * 4) % 2 == 0:
                grid[:, :] = [100, 0, 0]
        else:
            # Draw snake (gradient from head to tail)
            snake_length = len(self.snake)
            for i, (x, y) in enumerate(self.snake):
                # Head is brightest, tail fades out
                brightness = int(200 * (1 - i / (snake_length + 5)))
                if i == 0:
                    # Head is cyan
                    grid[x, y] = [0, brightness, brightness]
                else:
                    # Body is green
                    grid[x, y] = [0, brightness, 0]
            
            # Draw food (pulsing red)
            pulse = int(abs(np.sin(time.time() * 3)) * 150 + 50)
            if self.food:
                fx, fy = self.food
                grid[fx, fy] = [pulse, 0, 0]
        
        show_np(grid)


def main():
    """Main game loop with keyboard controls"""
    game = SnakeGame()
    keyboard = KeyboardInput()
    
    print("Snake Game Starting!")
    print("Score: 0")
    print("\nControls:")
    print("  W or w = Up")
    print("  A or a = Left")
    print("  S or s = Down")
    print("  D or d = Right")
    print("  Q or q = Quit")
    print("\nPress Ctrl+C to exit\n")
    
    # Start keyboard listener
    keyboard.start()
    
    last_score = 0
    
    while True:
        # Handle keyboard input
        key = keyboard.get_key()
        if key:
            if key.lower() == 'w':
                game.change_direction((0, -1))  # Up
            elif key.lower() == 'a':
                game.change_direction((-1, 0))  # Left
            elif key.lower() == 's':
                game.change_direction((0, 1))  # Down
            elif key.lower() == 'd':
                game.change_direction((1, 0))  # Right
            elif key.lower() == 'q':
                print("Quitting...")
                break
        
        if not game.game_over:
            game.update()
            game.render()
            
            # Print score updates
            if game.score > last_score:
                last_score = game.score
                print(f"Score: {game.score} | Speed: {game.speed:.3f}s")
        else:
            game.render()  # Show game over animation
            print(f"\nGame Over! Final Score: {game.score}")
            print("Restarting in 3 seconds...")
            time.sleep(3)
            game.reset()
            last_score = 0
            print("New game started! Score: 0\n")
        
        time.sleep(game.speed)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame stopped by user!")
    finally:
        # Clean up - turn off all LEDs
        pixels.fill((0, 0, 0))
        pixels.show()
        print("LEDs turned off. Goodbye!")

