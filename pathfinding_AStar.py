#!/usr/bin/python3
import pygame
import multiprocessing
import AStar_multiprocessing
import tkinter as tk
from tkinter import messagebox as ms_box
from typing import Optional, Dict, Tuple
import sys


class DefineSettings(object):
    """
    Define settings window can be opened by calling the .open method. It then returns the settings in the form of a dict.
        Init parameters:
            settings (dict) - The default settings to load, defaults to None.
    """

    def __init__(self, settings: Optional[Dict]):

        # Window - The tkinter display window.
        self.window = tk.Tk()

        # Attach the exit command to the WM_DELETE_WINDOW event (causes program to close correctly)
        self.window.protocol("WM_DELETE_WINDOW", self.__quit)

        # If Settings is equal to none, then load some default settings.
        if settings == None:
            self.settings = {
                "tile size": 15,
                "grid size": {
                    "x": 50,
                    "y": 50
                },
                "draw progress": tk.BooleanVar(self.window, True),
                "diagonal enabled": tk.BooleanVar(self.window, True)
            }
        # If Settings alredy contains some values, just replace the draw progress
        # and diagonal settings with the matching tk boolean variable.
        else:
            self.settings = settings
            self.settings["draw progress"] = tk.BooleanVar(
                self.window, settings["draw progress"])
            self.settings["diagonal enabled"] = tk.BooleanVar(
                self.window, settings["diagonal enabled"])

        # Tile size input
        tile_size_label = tk.Label(self.window, text="Tile size: ")
        tile_size_label.grid(column=1, row=0, sticky=tk.E, pady=(10, 0))

        tile_size_input = tk.Entry(self.window)
        tile_size_input.configure(width=3)
        tile_size_input.insert(0, self.settings["tile size"])
        tile_size_input.grid(column=2, row=0, sticky=tk.W, pady=(10, 0))

        # Grid size input
        grid_size_x_label = tk.Label(self.window, text="X:")
        grid_size_x_label.grid(column=1, row=1, sticky=tk.E)

        grid_size_y_label = tk.Label(self.window, text="Y:")
        grid_size_y_label.grid(column=1, row=2, sticky=tk.E)

        grid_size_x_input = tk.Entry(self.window)
        grid_size_x_input.configure(width=3)
        grid_size_x_input.insert(0, self.settings["grid size"]["x"])
        grid_size_x_input.grid(column=2, row=1, sticky=tk.W)

        grid_size_y_input = tk.Entry(self.window)
        grid_size_y_input.configure(width=3)
        grid_size_y_input.insert(0, self.settings["grid size"]["y"])
        grid_size_y_input.grid(column=2, row=2, sticky=tk.W)

        # Draw all checkbox
        draw_all_input = tk.Checkbutton(
            self.window, variable=self.settings["draw progress"], onvalue=True, offvalue=False)
        draw_all_input.grid(column=2, row=3, sticky=tk.W)

        draw_all_label = tk.Label(self.window, text="Draw progress")
        draw_all_label.grid(column=1, row=3, sticky=tk.E)

        # Diagonal enabled
        diagonal_enabled_checkbox = tk.Checkbutton(
            self.window, variable=self.settings["diagonal enabled"], onvalue=True, offvalue=False)
        diagonal_enabled_checkbox.grid(column=2, row=4, sticky=tk.W)

        diagonal_enabled_label = tk.Label(self.window, text="Diagonal?")
        diagonal_enabled_label.grid(column=1, row=4, sticky=tk.E)

        # Buttons
        submit_button = tk.Button(
            self.window, text="Generate", command=lambda: self.__submit())
        submit_button.grid(column=2, row=5, columnspan=2,
                           sticky=tk.W, padx=(0, 20), pady=(10, 20))

        cancel_button = tk.Button(
            self.window, text="Cancel", command=lambda: self.__quit())
        cancel_button.grid(column=0, row=5, columnspan=2,
                           sticky=tk.E, padx=(20, 0), pady=(10, 20))

        # Set window attributes
        self.window.resizable(0, 0)
        self.window.title('Define grid size.')
        self.grid_size_input = (grid_size_x_input, grid_size_y_input)
        self.tile_size_input = tile_size_input
        self.draw_all_input = draw_all_input

    def __submit(self):
        """Action of the submit button, if invalid inputs are present, the program will ask the user to re-enter the details."""

        # Wrap in a try so that any invalid settings dont crash the program.
        try:
            tile_size = int(self.tile_size_input.get())
            grid_size_x = int(self.grid_size_input[0].get())
            grid_size_y = int(self.grid_size_input[1].get())
            draw_all = self.settings["draw progress"].get()
            diagonal_enabled = self.settings["diagonal enabled"].get()
            self.settings = {
                "tile size": tile_size,
                "grid size": {
                    "x": grid_size_x,
                    "y": grid_size_y
                },
                "draw progress": draw_all,
                "diagonal enabled": diagonal_enabled
            }

            # If the settings are updated successfully, close this window.
            self.close()
        except:
            # Show an error message
            MessageBox = ms_box.Message(
                self.window, icon=ms_box.WARNING, message="Invalid inputs.", title="Warning")
            MessageBox.show()

    def close(self) -> dict:
        """Close the window, returns self.settings"""

        self.window.destroy()
        self.window.quit()
        return self.settings

    def __quit(self):
        """Close the program"""

        sys.exit(0)

    def open(self) -> dict:
        """Open the window (use .close method to force close)"""

        self.window.mainloop()
        return self.settings


class MapCreationWindow(object):
    """
    Pygame window with removable tiles, allows for editing of the map and running of the path finding algorithm.
        Init parameters:
            settings - The dict of settings created by the DefineSettings object.
    """

    def __init__(self, settings: dict):

        # Init pygame
        pygame.init()
        pygame.font.init()

        self.__borderSize = settings["border"]
        self.__tileSize = settings["tile size"]
        self.__x_tiles = settings["grid size"]["x"]
        self.__y_tiles = settings["grid size"]["y"]
        self.__controlPanelSize = 100
        self.diagonal_enabled = settings["diagonal enabled"]
        self.__output_progress = settings["draw progress"]
        self.__bg_color = settings["bg color"]

        # Initalise the multiprocessing manager (used for shared memory with the solving process)
        self.Manager = multiprocessing.Manager()

        # Initalise the pygame window
        self.windowSize = (self.__x_tiles * self.__tileSize + self.__borderSize,
                           self.__y_tiles * self.__tileSize + self.__borderSize + self.__controlPanelSize)
        self.window = pygame.display.set_mode(self.windowSize)
        pygame.display.set_caption("A* Path Finder")

        # Call reset to carry out the rest of the setup process for us
        self.reset()

    def reset(self):
        """Reset the object to its default state"""

        # This variable is used to itterate the navigation node number, so that the order of placement can be found.
        self.node_num = 0
        self.Process = None
        self.shared_memory = self.Manager.dict({
            "visited": set(),
            "path": set(),
            "nodes considered": 0,
            "time taken": 0
        })
        self.updated_tiles = set()

        # Create the tiles matrix
        self.__tiles = [[0 for _ in range(self.__x_tiles)]
                        for _ in range(self.__y_tiles)]

    def get_tile_coords(self, pos: tuple) -> tuple:
        """When given an x and y coordinate in the form (x,y) will return the coords of the tile that occupies that space."""

        tile_x = int((pos[0] - self.__borderSize // 2) / self.__tileSize)
        tile_y = int((pos[1] - self.__borderSize // 2) / self.__tileSize)
        return (tile_x, tile_y)

    def __mouse_handler(self) -> None:
        """Handles mouse actions."""

        # Prevent editing the grid after the route has been generated.
        if len(self.shared_memory["visited"]) == 0:
            mouse_presses = pygame.mouse.get_pressed()
            mouse_position = pygame.mouse.get_pos()
            tile_pos = self.get_tile_coords(mouse_position)

            # Check if tile position is within the bounds of the map.
            if tile_pos[0] < len(self.__tiles) and tile_pos[1] < len(self.__tiles[0]):

                # If user left clicks on a tile, hide it
                if mouse_presses[0]:
                    self.__tiles[tile_pos[0]][tile_pos[1]] = 1
                # If a user middle clicks on the tile, make it into a nav node, add the node_num to store the order of placement
                elif mouse_presses[1]:
                    self.__tiles[tile_pos[0]][tile_pos[1]] = 2 + self.node_num
                    self.node_num += 1
                # If a user right clicks on a tile, reset it to the default state
                elif mouse_presses[2]:
                    self.__tiles[tile_pos[0]][tile_pos[1]] = 0

    def __key_handler(self) -> None:
        """Handles key actions."""

        key_presses = pygame.key.get_pressed()
        if key_presses[pygame.K_r]:
            self.reset()
        elif key_presses[pygame.K_ESCAPE]:
            self.close()
        elif key_presses[pygame.K_RETURN]:
            self.start_pathfinding()

    def start_pathfinding(self):
        """Initialise the A* pathfinding algorithm"""

        def generate_base_forbidden() -> set:
            """
            Returns the base of the forbidden list (forms a barrier around the arena to prevent pathfinding around obstacles).\n
            Actually generates a wall which is 1 tile outside of the board space.
            """

            forbidden = set()
            for x in range(-1, self.__x_tiles + 1):
                forbidden.add((x, self.__y_tiles))
                forbidden.add((x, -1))
            for y in range(-1, self.__y_tiles + 1):
                forbidden.add((self.__x_tiles, y))
                forbidden.add((-1, y))

            return forbidden

        # If the solving process hasn't already been initiated
        if self.Process == None:
            allowed_set = set()
            forbidden_set = generate_base_forbidden()
            nav_nodes = []

            # Go thorugh the tiles on screen, assigning each to an appropriate group
            # Tiles with a value of 1 are not allowed, all else are.
            # Any tiles with a value of 2 or more are navigation nodes (there should only be 2.)
            for x in range(len(self.__tiles)):
                for y in range(len(self.__tiles[x])):
                    tile_value = self.__tiles[x][y]
                    tile_coords = (x, y)

                    if tile_value == 1:
                        forbidden_set.add(tile_coords)
                    else:
                        allowed_set.add(tile_coords)
                        if tile_value >= 2:
                            nav_nodes.append(tile_coords)

            # If the user has not created enough nav_nodes (or too many), display an error message and do not continue.
            if len(nav_nodes) != 2:
                temp = tk.Tk()
                messagebox = ms_box.Message(temp, message="You must create exactly 2 navigation nodes (middle click).",
                                            title="Input error", type=ms_box.OK, icon=ms_box.WARNING)
                temp.withdraw()
                messagebox.show()
            else:
                # Add the forbidden and nav tiles to the updated tiles, so they are not changed by the update_tiles method.
                self.updated_tiles = forbidden_set.copy()
                self.updated_tiles = self.updated_tiles.union(nav_nodes)

                # Sort the nav_nodes list to obtain the order of them.
                nav_nodes = sorted(
                    nav_nodes, key=lambda coords: self.__tiles[coords[0]][coords[1]])

                # Create and start process
                self.Process = AStar_multiprocessing.Movement2DProcess(
                    nav_nodes[0], nav_nodes[1], self.shared_memory, allowed_set, forbidden_set, self.diagonal_enabled)
                self.Process.start()

    def update_tiles(self) -> None:
        """Update the tiles in the matrix to represent the algorithms progress."""

        visited_draw_set = set(
            node for node in self.shared_memory["visited"] if node not in self.updated_tiles)
        for node in visited_draw_set:
            # Check the node is in bounds
            if (node[0] >= 0 and node[0] < self.__x_tiles) and (node[1] >= 0 and node[1] < self.__y_tiles):
                self.__tiles[node[0]][node[1]] = -1
                self.updated_tiles.add(node)

        if self.shared_memory["path"] != -1:
            self.Process = None
            for node in self.shared_memory["path"]:
                # Check the node is in bounds
                if (node[0] >= 0 and node[0] < self.__x_tiles) and (node[1] >= 0 and node[1] < self.__y_tiles):
                    self.__tiles[node[0]][node[1]] = -2

    def __draw(self) -> None:
        """This function draws the interface on the pygame window."""

        def draw_tiles():
            """Draw the updated tiles on the screen."""

            # For each tile on the screen, draw the tile
            for x in range(len(self.__tiles)):

                column = self.__tiles[x]

                for y in range(len(column)):

                    # The tile value is treated as its mode.
                    # A value of 0 is normal, 1 is disabled and anything >= 2 is start or end node.
                    # -1 means they have been visited by the algorithm, and -2 means they are part of the found path.
                    tile_value = column[y]
                    color = (255, 255, 255)

                    if tile_value == 1:
                        color = (255, 128, 128)
                    elif tile_value >= 2:
                        color = (255, 128, 255)
                    elif tile_value == -1:
                        color = (128, 128, 255)
                    elif tile_value == -2:
                        color = (128, 255, 128)

                    # Calculate the x and y coordinate for this tile to be drawn at.
                    draw_x = self.__borderSize // 2 + x * self.__tileSize
                    draw_y = self.__borderSize // 2 + y * self.__tileSize

                    # Draw the rectangle on screen
                    pygame.draw.rect(
                        self.window, color, (draw_x + 1, draw_y + 1, self.__tileSize - 2, self.__tileSize - 2))

        def draw_control_panel():
            """Draw the instructions at the bottom of the screen"""

            font = pygame.font.Font(
                "freesansbold.ttf", self.windowSize[0] // 60)
            text = font.render(
                "Controls: R - Reset screen, M1 - Remove tile, M2 - Reset tile, M3 - Set navigation node, ESC - Close window", True, (0, 0, 0), self.__bg_color)
            text_rect = text.get_rect()
            text_rect.center = (
                self.windowSize[0] // 2, self.windowSize[1] - 50)
            self.window.blit(text, text_rect)

        # Fill the background with the corresponding color
        self.window.fill(self.__bg_color)

        # Call the local draw functions.
        draw_tiles()
        draw_control_panel()

        # Update the changes to the display.
        pygame.display.update()

    def open(self):
        """Opens the tiles window, and allows for editing."""

        self.running = True
        mouse_down = False
        key_down = False

        # Main event loop
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_down = False
                elif event.type == pygame.KEYDOWN:
                    key_down = True
                elif event.type == pygame.KEYUP:
                    key_down = False

            # Handle keyboard and mouse events if process is not currently active
            if self.Process == None:
                if mouse_down:
                    self.__mouse_handler()
                elif key_down:
                    self.__key_handler()

            # Update the tiles matrix
            self.update_tiles()

            # Call the draw function to update the display
            self.__draw()

        if self.Process != None:
            self.Process.close()
        pygame.quit()

    def close(self):
        """Close the map window."""

        self.running = False


if __name__ == "__main__":
    settings = None
    while True:
        settings_window = DefineSettings(settings)
        settings = settings_window.open()

        settings["border"] = 10
        settings["bg color"] = (200, 200, 200)
        Window = MapCreationWindow(settings)
        Window.open()
