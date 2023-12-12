# To create & start using python venv:
#       python -m venv venv
#       source venv/bin/activate

# Install specific modules with pip:
# f.e.:   pip install pygame

# Requirements
# 1. Make simulation real time
# 2. Add pause / resume logic
# 3. Add save / load logic

# High-level logic
# 1. Create and init the simulation grid
# 2. Start the simulation with a tick interval of <n> seconds
# 3. At each tick:
#   3.1. Update the grid - loop over each element of the board
#   3.2. Render new generation

# General approach
# 1. Plan & write down the general workflow
#  1.1. Define Input&Output 
#  1.2. Consider adding validation
# 2. Separate the main algorithms / actors in the code. Try to abstract as much common code as possible
# 3. Define communication between the objects
# 4. List the patterns you could apply
# 5. Build PoCs (Proof of concepts). Try to separate implementation of specific steps. Prepare smaller modules
#    and combine them into a complete application
# 6. Refine if needed

# Deadline - 15th of December 2023
# Mail with: 
# 1. short screen recording demonstrating the new features
# 2. Linked code
# 3. Short description of the changes. Which design patterns you used and how you applied them. 

import pygame
import numpy as np
import os
from settingsLoader import SettingsLoader

from abc import abstractmethod

# Initialize Pygame
pygame.init()

# Initialize Settings Loader
config = SettingsLoader()

# Screen dimensions
width, height = config.get_setting("SCREEN_WIDTH"), config.get_setting("SCREEN_HEIGHT")
screen = pygame.display.set_mode((width, height))

# Grid dimensions
n_cells_x, n_cells_y = config.get_setting("CELLS_X"), config.get_setting("CELLS_Y")
cell_width = width // n_cells_x
cell_height = height // n_cells_y

# Game state
game_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])

# Define a timer event for automatic progression
AUTO_NEXT_GEN_EVENT = pygame.USEREVENT + 1
auto_next_gen_interval = config.get_setting("AUTO_NEXT_GEN_TIME_MS")

# Colors
white = config.get_setting("COLOR_WHITE")
black = config.get_setting("COLOR_BLACK")
gray = config.get_setting("COLOR_GRAY")
green = config.get_setting("COLOR_GREEN")
red = config.get_setting("COLOR_RED")

# Button Click Strategy
class ClickStrategy:
    @abstractmethod
    def click(self):
        pass

class DefaultClickStrategy(ClickStrategy):
    def click(self):
        pass

class NextGenClickStrategy(ClickStrategy):
    def click(self):
        next_generation()

class SaveClickStrategy(ClickStrategy):
    def click(self):
        save_game_state()

class LoadClickStrategy(ClickStrategy):
    def click(self):
        load_game_state()

class PlayClickStrategy(ClickStrategy):
    def click(self):
        global play_button_state
        if play_button_state == "play":
            pygame.time.set_timer(AUTO_NEXT_GEN_EVENT, auto_next_gen_interval)
            play_button_state = "pause"
            play_button.text = "Pause"
            play_button.color = red
        else:
            pygame.time.set_timer(AUTO_NEXT_GEN_EVENT, 0)
            play_button_state = "play"
            play_button.text = "Play"
            play_button.color = green
            
# Button Factory:
class ButtonFactory:
    def create_button(self, x, y, width, height, text, color, click_strategy=DefaultClickStrategy()):
        return Button(x, y, width, height, text, color, click_strategy)
    def create_next_gen_button(self, x, y, width, height, text, color):
        return Button(x, y, width, height, text, color, NextGenClickStrategy())
    def create_save_button(self, x, y, width, height, text, color):
        return Button(x, y, width, height, text, color, SaveClickStrategy())
    def create_load_button(self, x, y, width, height, text, color):
        return Button(x, y, width, height, text, color, LoadClickStrategy())
    def create_play_button(self, x, y, width, height, text, color):
        return Button(x, y, width, height, text, color, PlayClickStrategy())

class Button:
    def __init__(self, x, y, width, height, text, color, click_strategy=DefaultClickStrategy()):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.click_strategy = click_strategy
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.Font(None, 36)
        text = font.render(self.text, True, black)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

    def is_clicked(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height
    
    def click(self):
        self.click_strategy.click()

    def setColor(self, color):
        self.color = color
    
# Button instances
button_width, button_height = config.get_setting("STANDARD_BUTTON_WIDTH"), config.get_setting("STANDARD_BUTTON_HEIGHT")
button_factory = ButtonFactory()
next_gen_button = button_factory.create_next_gen_button(width // 2 - button_width - 10, height - button_height - 20, button_width, button_height, "Next Gen", green)
play_button = button_factory.create_play_button(width // 2 + 10, height - button_height - 20, button_width, button_height, "Play", green)
save_button = button_factory.create_save_button(20, 230, button_width, button_height, "Save", green)
load_button = button_factory.create_load_button(20, 300, button_width, button_height, "Load", green)

# Buttons dimensions
play_button_state = "play"

def draw_grid():
    for y in range(0, height, cell_height):
        for x in range(0, width, cell_width):
            cell = pygame.Rect(x, y, cell_width, cell_height)
            pygame.draw.rect(screen, gray, cell, 1)

def next_generation():
    global game_state
    new_state = np.copy(game_state)

    for y in range(n_cells_y):
        for x in range(n_cells_x):
            n_neighbors = game_state[(x - 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x)     % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y - 1) % n_cells_y] + \
                          game_state[(x - 1) % n_cells_x, (y)     % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y)     % n_cells_y] + \
                          game_state[(x - 1) % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state[(x)     % n_cells_x, (y + 1) % n_cells_y] + \
                          game_state[(x + 1) % n_cells_x, (y + 1) % n_cells_y]

            if game_state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                new_state[x, y] = 0
            elif game_state[x, y] == 0 and n_neighbors == 3:
                new_state[x, y] = 1

    game_state = new_state

def draw_cells():
    for y in range(n_cells_y):
        for x in range(n_cells_x):
            cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            if game_state[x, y] == 1:
                pygame.draw.rect(screen, black, cell)

def save_game_state():
    global game_state
    with open("game_state.txt", "w") as file:
        for row in game_state:
            file.write(' '.join(str(cell) for cell in row) + '\n')

def load_game_state():
    global game_state
    try:
        with open("game_state.txt", "r") as file:
            lines = file.readlines()
            game_state = np.array([list(map(int, line.split())) for line in lines])
    except:
        pass

def check_save_file_exists():
    return os.path.isfile("game_state.txt")

def update_load_button_color():
    if check_save_file_exists():
        load_button.setColor(green)
    else:
        load_button.setColor(red)

running = True
while running:
    screen.fill(white)

    update_load_button_color()

    draw_grid()
    draw_cells()
    next_gen_button.draw()
    save_button.draw()
    load_button.draw()
    play_button.draw()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if next_gen_button.is_clicked(event.pos):
                next_gen_button.click()
            elif save_button.is_clicked(event.pos):
                save_button.click()
            elif load_button.is_clicked(event.pos):
                load_button.click()
            elif play_button.is_clicked(event.pos):
                play_button.click()
            else:
                x, y = event.pos[0] // cell_width, event.pos[1] // cell_height
                game_state[x, y] = not game_state[x, y]
        elif event.type == AUTO_NEXT_GEN_EVENT:
            next_generation()

pygame.quit()