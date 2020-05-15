#!/usr/bin/python3
import pygame
import multiprocessing
import AStar
import time
import tkinter as tk
from tkinter import messagebox as ms_box
# TODO: Replace tiles system with something faster.
# TODO: Add type annotations and other improvements.
# TODO: Fix variable naming conventions.


class DefineSettings(object):
    """Define settings window can be opened by calling the .open method. It then returns the settings in the form of a dict.\n
    Can be passed some default settings as an optional argument"""

    def __init__(self, settings=None):
        # Window
        self.window = tk.Tk()

        # Settings
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
        else:
            self.settings = {
                "tile size": settings["tile size"],
                "grid size": {
                    "x": settings["grid size"]["x"],
                    "y": settings["grid size"]["y"]
                },
                "draw progress": tk.BooleanVar(self.window, settings["draw progress"]),
                "diagonal enabled": tk.BooleanVar(self.window, settings["diagonal enabled"])
            }

        # Tile size input
        TileSize_Label = tk.Label(self.window, text="Tile size: ")
        TileSize_Label.grid(column=1, row=0, sticky=tk.E, pady=(10, 0))

        TileSize_Input = tk.Entry(self.window)
        TileSize_Input.configure(width=3)
        TileSize_Input.insert(0, self.settings["tile size"])
        TileSize_Input.grid(column=2, row=0, sticky=tk.W, pady=(10, 0))

        # Grid size input
        GridSizeX_Label = tk.Label(self.window, text="X:")
        GridSizeX_Label.grid(column=1, row=1, sticky=tk.E)

        GridSizeY_Label = tk.Label(self.window, text="Y:")
        GridSizeY_Label.grid(column=1, row=2, sticky=tk.E)

        GridSizeX_Input = tk.Entry(self.window)
        GridSizeX_Input.configure(width=3)
        GridSizeX_Input.insert(0, self.settings["grid size"]["x"])
        GridSizeX_Input.grid(column=2, row=1, sticky=tk.W)

        GridSizeY_Input = tk.Entry(self.window)
        GridSizeY_Input.configure(width=3)
        GridSizeY_Input.insert(0, self.settings["grid size"]["y"])
        GridSizeY_Input.grid(column=2, row=2, sticky=tk.W)

        # Draw all checkbox
        DrawAll_CheckBox = tk.Checkbutton(
            self.window, variable=self.settings["draw progress"], onvalue=True, offvalue=False)
        DrawAll_CheckBox.grid(column=2, row=3, sticky=tk.W)

        DrawAll_Label = tk.Label(self.window, text="Draw progress")
        DrawAll_Label.grid(column=1, row=3, sticky=tk.E)

        # Diagonal enabled
        DiagonalEnabled_Checkbox = tk.Checkbutton(
            self.window, variable=self.settings["diagonal enabled"], onvalue=True, offvalue=False)
        DiagonalEnabled_Checkbox.grid(column=2, row=4, sticky=tk.W)

        DiagonalEnabled_Label = tk.Label(self.window, text="Diagonal?")
        DiagonalEnabled_Label.grid(column=1, row=4, sticky=tk.E)

        # Buttons
        Submit_Button = tk.Button(
            self.window, text="Generate", command=lambda: self.__submit())
        Submit_Button.grid(column=2, row=5, columnspan=2,
                           sticky=tk.W, padx=(0, 20), pady=(10, 20))

        Cancel_Button = tk.Button(
            self.window, text="Cancel", command=lambda: self.__quit())
        Cancel_Button.grid(column=0, row=5, columnspan=2,
                           sticky=tk.E, padx=(20, 0), pady=(10, 20))

        # Set atributes
        self.window.resizable(0, 0)
        self.window.title('Define grid size.')
        self.GridSize_Input = (GridSizeX_Input, GridSizeY_Input)
        self.TileSize_Input = TileSize_Input
        self.DrawAll_Input = DrawAll_CheckBox

    def __submit(self):
        "Action of the submit button, if invalid inputs are present, the program will ask the user to re-enter the details."
        try:
            TileSize = int(self.TileSize_Input.get())
            GridSizeX = int(self.GridSize_Input[0].get())
            GridSizeY = int(self.GridSize_Input[1].get())
            DrawAll = self.settings["draw progress"].get()
            DiagonalEnabled = self.settings["diagonal enabled"].get()
            self.settings = {
                "tile size": TileSize,
                "grid size": {
                    "x": GridSizeX,
                    "y": GridSizeY
                },
                "draw progress": DrawAll,
                "diagonal enabled": DiagonalEnabled
            }
            self.close()
        except:
            MessageBox = ms_box.Message(
                self.window, icon=ms_box.WARNING, message="Invalid inputs.", title="Warning")
            MessageBox.show()

    def close(self):
        "Close the window, returns self.settings"
        self.window.destroy()
        self.window.quit()
        return self.settings

    def __quit(self):
        "Close the program"
        quit()

    def open(self):
        "Open the window (use .close method to force close)"
        self.window.mainloop()
        return self.settings


class MapCreationWindow(object):
    "Pygame window with removable tiles, allows for editing of the map and running of the path finding algorithm."

    def __init__(self, settings):
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
        self.Manager = multiprocessing.Manager()
        self.windowSize = (self.__x_tiles * self.__tileSize + self.__borderSize,
                           self.__y_tiles * self.__tileSize + self.__borderSize + self.__controlPanelSize)
        self.window = pygame.display.set_mode(self.windowSize)
        pygame.display.set_caption("A* Path Finder")
        self.reset()

    def reset(self):
        "Reset the map to its default state"
        self.Process = None
        self.shared_memory = self.Manager.dict({
            "visited": set(),
            "path": set(),
            "nodes considered": 0,
            "time taken": 0
        })
        self.__nav_num = 0
        self.updated_tiles = set()

        # Create the tiles matrix
        self.__tiles = [[0 for _ in range(self.__x_tiles)]
                        for _ in range(self.__y_tiles)]

    def get_tile_coords(self, pos: tuple) -> tuple:
        """
        When given an x and y coordinate in the form (x,y) will return the coords of the tile that occupies that space.
        """

        tile_x = int((pos[0] - self.__borderSize // 2) / self.__tileSize)
        tile_y = int((pos[1] - self.__borderSize // 2) / self.__tileSize)
        return (tile_x, tile_y)

    def __mousehandler(self) -> None:
        """
        Handles mouse actions.
        """

        # Prevent editing the grid after the route has been generated.
        if len(self.shared_memory["visited"]) == 0:
            mousePresses = pygame.mouse.get_pressed()
            mousePosition = pygame.mouse.get_pos()
            tile_pos = self.get_tile_coords(mousePosition)

            # Check if tile position is within the bounds of the map.
            if tile_pos[0] < len(self.__tiles) and tile_pos[1] < len(self.__tiles[0]):

                # If user left clicks on a tile, hide it
                if mousePresses[0]:
                    self.__tiles[tile_pos[0]][tile_pos[1]] = 1
                # If a user middle clicks on the tile, make it into a nav node.
                elif mousePresses[1]:
                    self.__tiles[tile_pos[0]][tile_pos[1]] = 2
                # If a user right clicks on a tile, reset it to the default state
                elif mousePresses[2]:
                    self.__tiles[tile_pos[0]][tile_pos[1]] = 0

    def __key_handler(self) -> None:
        """
        Handles key presses.
        """

        keyPresses = pygame.key.get_pressed()
        if keyPresses[pygame.K_r]:
            self.reset()
        elif keyPresses[pygame.K_ESCAPE]:
            self.close()
        elif keyPresses[pygame.K_RETURN]:
            self.start_pathfinding()

    def start_pathfinding(self) -> None:
        """
        Initialise the A* pathfinding algorithm
        """

        def generate_base_forbidden() -> set:
            """
            Returns the base of the forbidden list (forms a barrier around the arena to prevent pathfinding around obstacles).
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
                # Add the forbidden_
                self.updated_tiles = forbidden_set.copy()
                # Create and start process
                self.Process = process(
                    nav_nodes[0], nav_nodes[1], self.shared_memory, allowed_set, forbidden_set, self.diagonal_enabled)
                self.Process.start()

    def update_tiles(self) -> None:
        """
        Update the tiles in the matrix to represent the algorithms progress.
        """

        visited_draw_set = set(
            node for node in self.shared_memory["visited"] if node not in self.updated_tiles)
        for node in visited_draw_set:
            # Check the node is not in the path
            if node not in self.shared_memory["path"]:
                # Check the node is in bounds
                if (node[0] >= 0 and node[0] < self.__x_tiles) and (node[1] >= 0 and node[1] < self.__y_tiles):
                    self.__tiles[node[0]][node[1]] = -1
                    self.updated_tiles.add(node)

        if self.shared_memory["path"]:
            self.Process = None
            for node in self.shared_memory["path"]:
                # Check the node is in bounds
                if (node[0] >= 0 and node[0] < self.__x_tiles) and (node[1] >= 0 and node[1] < self.__y_tiles):
                    self.__tiles[node[0]][node[1]] = -2

    def __draw(self) -> None:
        """
        This function draws the interface on the pygame window.
        """
        def draw_tiles():
            """
            Draw the updated tiles on the screen.
            """

            # For each tile on the screen, draw the tile
            for x in range(len(self.__tiles)):

                column = self.__tiles[x]

                for y in range(len(column)):

                    # The tile value is treated as its mode.
                    # A value of 0 is normal, 1 is disabled and 2 is start or end node.
                    # -1 means they have been visited by the algorithm, and -2 means they are part of the found path.
                    tile_value = column[y]
                    color = (255, 255, 255)

                    if tile_value == 1:
                        color = (255, 128, 128)
                    elif tile_value == 2:
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
            """
            Draw the instructions at the bottom of the screen
            """

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
        "Opens the tiles window, and allows for editing."
        self.running = True
        mouseDown = False
        keyDown = False
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouseDown = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouseDown = False
                elif event.type == pygame.KEYDOWN:
                    keyDown = True
                elif event.type == pygame.KEYUP:
                    keyDown = False

            # Handle keyboard and mouse events if process is not currently active
            if self.Process == None:
                if mouseDown:
                    self.__mousehandler()
                elif keyDown:
                    self.__key_handler()

            # Update the tiles matrix
            self.update_tiles()

            # Call the draw function to update the display
            self.__draw()

        # Exit program
        if self.Process != None:
            self.Process.close()
        pygame.quit()

    def close(self):
        self.running = False


class process(multiprocessing.Process):
    "For running the pathfinding process on another process (to allow for updating of the pygame display to happen in parallel)"

    def __init__(self, start, goal, shared_memory, allowed_list, forbidden_list, diagonal_enabled):
        super(process, self).__init__()
        self.start_pos = start
        self.goal_pos = goal
        self.shared_memory = shared_memory
        self.allowed_states = allowed_list
        self.forbidden_states = forbidden_list
        self.diagonal_enabled = diagonal_enabled

    def run(self):
        a = self.Movement_2D_Solver(self.start_pos, self.goal_pos, self.shared_memory,
                                    self.allowed_states, self.forbidden_states, self.diagonal_enabled)
        try:
            a.Solve()
        except Exception as e:
            self.shared_memory["path"] = -1
            print(e)
        self.shared_memory["nodes considered"] = a.nodes_considered
        self.shared_memory["time taken"] = a.time_taken

    class Movement_2D_Solver(AStar.Movement_2D_Solver):
        "Sub-class of the normal Movement_2D_Solver in order make sure data is recieved properly by the main process."

        def __init__(self, start, goal, shared_memory, allowed_states=None, forbidden_states=None, diagonal_enabled=False):
            super().__init__(tuple(start), tuple(goal), allowed_states, forbidden_states)
            self.shared_memory = shared_memory
            self.diagonal_enabled = diagonal_enabled
            self.start_state = self.__get_start_state()

        def __get_start_state(self):
            return AStar.State_2D_Movement(self.start, 0, self.diagonal_enabled, self.start, self.goal)

        def Solve(self):
            """Creates a solution on how to get from the start, to the goal.\n
            This method returns the path created, but it can also be gained by using the .path atribute.\n
            The .paths_considered and .time_taken atributes can be looked at if you want to gauge the performance of this algorithm.\n
            If no solution is found, this method will raise an exception, which can then be caught with a try except."""
            start_time = time.time()
            startState = self.start_state
            # Check if startState is set.
            if startState != None:
                count = 0
                self.PriorityQueue.put((0, count, startState))
                while (not self.path) and (self.PriorityQueue.qsize()):
                    closestChild = self.PriorityQueue.get()[2]
                    closestChild.CreateChildren(self.visitedQueue)
                    # If the goal and start value are the same, then nothing needs to be done.
                    if closestChild.value == self.goal:
                        self.path = closestChild.path
                        break
                    for child in closestChild.children:
                        if not(closestChild.value in self.visitedQueue):
                            count += 1
                            if not child.dist:
                                self.path = child.path
                                break
                            self.PriorityQueue.put((child.dist, count, child))
                    self.visitedQueue.add(closestChild.value)
                    self.shared_memory["visited"] = self.visitedQueue
                if not self.path:
                    raise Exception("No path")
                end_time = time.time()
                self.time_taken = int(round((end_time - start_time) * 1000, 0))
                self.nodes_considered = count
                self.shared_memory["path"] = set(self.path)
                return self.path
            else:
                # If the startState is not set, raise an exception
                raise Exception(
                    "startState is not set. Are you instansiating the wrong class?")


if __name__ == "__main__":
    settings = None
    while True:
        settings_window = DefineSettings(settings)
        settings = settings_window.open()

        settings["border"] = 10
        settings["bg color"] = (200, 200, 200)
        Window = MapCreationWindow(settings)
        Window.open()
