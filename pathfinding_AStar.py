#!/usr/bin/python3
import pygame
import multiprocessing
import AStar
import time
import tkinter as tk
from tkinter import messagebox as ms_box

class DefineSettings(object):
    "Define settings window can be opened by calling the .open method. It then returns the settings in the form of a dict."
    def __init__(self):
        #Window
        self.window = tk.Tk()

        #Tile size input
        TileSize_Label = tk.Label(self.window, text="Tile size: ")
        TileSize_Label.grid(column=1, row=0, sticky=tk.E)
    
        TileSize_Input = tk.Entry(self.window)
        TileSize_Input.configure(width=3)
        TileSize_Input.insert(0, "50")
        TileSize_Input.grid(column=2, row=0, sticky=tk.W)

        #Grid size input
        GridSizeX_Label = tk.Label(self.window, text="X:")
        GridSizeX_Label.grid(column=1, row=1, sticky=tk.E)

        GridSizeY_Label = tk.Label(self.window, text="Y:")
        GridSizeY_Label.grid(column=1, row=2, sticky=tk.E)

        GridSizeX_Input = tk.Entry(self.window)
        GridSizeX_Input.configure(width=3)
        GridSizeX_Input.insert(0, "15")
        GridSizeX_Input.grid(column=2, row=1, sticky=tk.W)

        GridSizeY_Input = tk.Entry(self.window)
        GridSizeY_Input.configure(width=3)
        GridSizeY_Input.insert(0, "15")
        GridSizeY_Input.grid(column=2, row=2, sticky=tk.W)

        #Buttons
        Submit_Button = tk.Button(self.window, text="Generate", command=lambda: self.__submit())
        Submit_Button.grid(column=2, row=3, columnspan=2, sticky=tk.W)

        Cancel_Button = tk.Button(self.window, text="Cancel", command=lambda: self.close())
        Cancel_Button.grid(column=0, row=3, columnspan=2, sticky=tk.E)
        
        #Set atributes
        self.window.resizable(0,0)
        self.window.title('Define grid size.')
        self.GridSize_Input = (GridSizeX_Input, GridSizeY_Input)
        self.TileSize_Input = TileSize_Input
        self.settings = {
            "tile size": 0,
            "grid size": {
                "x": 0,
                "y": 0
            }
        }

    def __submit(self):
        "Action of the submit button, if invalid inputs are present, the program will ask the user to re-enter the details."
        try:
            TileSize = int(self.TileSize_Input.get())
            GridSizeX = int(self.GridSize_Input[0].get())
            GridSizeY = int(self.GridSize_Input[1].get())
            self.settings = {
                "tile size": TileSize,
                "grid size": {
                    "x": GridSizeX,
                    "y": GridSizeY
                }
            }
            self.close()
        except:
            MessageBox = ms_box.Message(self.window, icon=ms_box.WARNING, message="Invalid inputs.", title="Warning")
            MessageBox.show()

    def close(self):
        "Close the window, returns self.settings."
        self.window.destroy()
        return self.settings
    
    def open(self):
        "Open the window, returns self.settings after the .close method is called."
        self.window.mainloop()
        return self.settings
class tile(object):
    """Tile object, used on the pygame window.\n
    Window argument is the pygame window to draw on.\n
    Size argument is the size of the rect to be drawn (tiles are always square).\n
    x_pos and y_pos are the position of the tile."""
    def __init__(self, window, size, x_pos, y_pos):
        self.enabled = True
        self.state = 0
        self.window = window
        self.size = size
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = (255,255,255)

    def draw(self):
        "Draw the tile on the pygame window"
        if self.enabled:
            if self.state == 0:
                pygame.draw.rect(self.window, self.color, (self.x_pos + 1, self.y_pos + 1, self.size - 2, self.size - 2))
            else:
                pygame.draw.rect(self.window, (255,0,255), (self.x_pos + 1, self.y_pos + 1, self.size - 2, self.size - 2))
class MapCreationWindow(object):
    "Pygame window with removable tiles, allows for editing of the map and running of the path finding algorithm."
    def __init__(self, borderSize, tileSize, x_tiles, y_tiles, diagonal_enabled = False):
        pygame.init()
        self.windowSize = (x_tiles * tileSize + borderSize, y_tiles * tileSize + borderSize)
        self.window = pygame.display.set_mode(self.windowSize)
        pygame.display.set_caption("A* Path Finder")
        self.bg_color = (200,200,200)
        self.__borderSize = borderSize
        self.__tileSize = tileSize
        self.__x_tiles = x_tiles
        self.__y_tiles = y_tiles
        self.Manager = multiprocessing.Manager()
        self.diagonal_enabled = diagonal_enabled
        self.reset()

    def reset(self):
        "Reset the map to its default state"
        self.Process = None
        self.Process_Run = False
        self.shared_memory = self.Manager.dict({
            "visited": set(),
            "path": set()
        })
        self.tile_list = self.__create_tiles()
        self.__nav_num = 0
        self.updated_tiles = []

    def __create_tiles(self):
        "Create the tileList variable filled with tile objects. Each tile represents a portion of the screen."
        tile_list = []
        for y in range(self.__y_tiles):
            for x in range(self.__x_tiles):
                tileSize = self.__tileSize
                borderSize = self.__borderSize
                tile_list.append(tile(self.window, tileSize, borderSize // 2 + x * tileSize, borderSize // 2 + y * tileSize))
        return tile_list

    def get_tile_coords(self, pos):
        "When given an x and y coordinate in the form (x,y) will return the coords of the tile that occupies that space."
        tile_x = int(((pos[0] - self.__borderSize // 2) / self.__tileSize) + 1)
        tile_y = int(((pos[1] - self.__borderSize // 2) / self.__tileSize) + 1)
        return (tile_x, tile_y)

    def get_cur_tile(self, pos):
        "When given an x and y coordinate in the form (x,y), will return the tile that occupies that position."
        #If the cursor is in the lower border, return None to prevent the changing of the opposite tiles
        if pos[0] < borderSize // 2 or pos[1] < borderSize // 2:
            return None
        coords = self.get_tile_coords(pos)
        tile_x = coords[0]
        tile_y = coords[1]
        return self.get_tile(tile_x, tile_y)

    def get_tile(self, x, y):
        """Returns the tile at the specified x and y in the tile list.\n
        If an invalid x or y coordinate is passed, will return none."""
        if x <= self.__x_tiles and y <= self.__y_tiles:
            return self.tile_list[((y - 1) * self.__x_tiles) + x - 1]
        else:
            return None
    
    def mouse_handler(self):
        "Handles mouse actions."
        mousePresses = pygame.mouse.get_pressed()
        mousePosition = pygame.mouse.get_pos()
        tile = self.get_cur_tile(mousePosition)
        if tile != None:
            if mousePresses[0]:
                tile.enabled = False
            elif mousePresses[1]:
                tile.enabled = True
                tile.state = self.__nav_num
                self.__nav_num += 1
            elif mousePresses[2]:
                tile.enabled = True
        
    def key_handler(self):
        "Handles key presses."
        keyPresses = pygame.key.get_pressed()
        if keyPresses[pygame.K_r]:
            self.reset()
        elif keyPresses[pygame.K_ESCAPE]:
            self.close()
        elif keyPresses[pygame.K_RETURN]:
            self.start_pathfinding()

    def start_pathfinding(self):
        "Initialise the A* pathfinding algorithm"
        if self.Process == None:
            allowed_list = []
            forbidden_list = []
            nav_nodes = []
            for tile in self.tile_list:
                if tile.enabled:
                    allowed_list.append(self.get_tile_coords([tile.x_pos, tile.y_pos]))
                    if tile.state > 0:
                        nav_nodes.append(self.get_tile_coords([tile.x_pos, tile.y_pos]))
                else:
                    forbidden_list.append(self.get_tile_coords([tile.x_pos, tile.y_pos]))
            start = nav_nodes[0]
            goal = nav_nodes[1]
            self.Process = process(start, goal, self.shared_memory, allowed_list, forbidden_list, self.diagonal_enabled)
            self.Process.start()
    
    def update_tiles(self):
        "draw the current state of the tiles on screen"
        if not(self.shared_memory["path"]):
            visited_draw_list = set([tuple(node) for node in self.shared_memory["visited"] if node not in self.updated_tiles])
            for node in visited_draw_list:
                tile = self.get_tile(node[0], node[1])
                if tile != None:
                    tile.color = (0,128,255)
                self.updated_tiles.append(node)
        else:
            for node in self.shared_memory["path"]:
                tile = self.get_tile(node[0], node[1])
                if tile != None:
                    tile.color = (0,255,0)
    
    def open(self):
        "Opens the tiles window, and allows for editing."
        self.running = True
        mouseDown = False
        keyDown = False
        window = self.window
        tile_list = self.tile_list
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
            
            #Handle keyboard and mouse events
            if mouseDown:
                self.mouse_handler()
            elif keyDown:
                self.key_handler()
                
                if tile_list != self.tile_list:
                    #If the tile_list has been changed by another source, reasign it
                    tile_list = self.tile_list
            
            self.update_tiles()
            
            #Fill the window and draw the tiles on it
            window.fill(self.bg_color)
            for tile in tile_list:
                tile.draw()
            pygame.display.update()
        
        #Exit program
        if self.Process != None:
            self.Process.close()
        quit()
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
        a = self.Movement_2D_Solver(self.start_pos, self.goal_pos, self.shared_memory, self.allowed_states, self.forbidden_states, self.diagonal_enabled)
        a.Solve()
        for item in a.path:
            self.shared_memory["path"].add(item)
        print("Process complete!")
    class Movement_2D_Solver(AStar.Movement_2D_Solver):
        "Sub-class of the normal Movement_2D_Solver in order make sure data is recieved properly by the main process."
        def __init__(self, start, goal, shared_memory, allowed_states = None, forbidden_states = None, diagonal_enabled = False):
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
            #Check if startState is set.
            if startState != None:
                count = 0
                self.PriorityQueue.put((0, count, startState))
                while (not self.path) and (self.PriorityQueue.qsize()):
                    closestChild = self.PriorityQueue.get()[2]
                    closestChild.CreateChildren()
                    #If the goal and start value are the same, then nothing needs to be done.
                    if closestChild.value == self.goal:
                        self.path = closestChild.path
                        break
                    for child in closestChild.children:
                        if not(closestChild.value in self.visitedQueue) and (self.allowed_states == None or child.value in self.allowed_states) and (self.forbidden_states == None or child.value not in self.forbidden_states):
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
                #If the startState is not set, raise an exception
                raise Exception("startState is not set. Are you instansiating the wrong class?")

if __name__ == "__main__":
    settings_window = DefineSettings()
    settings = settings_window.open()

    borderSize = 10
    Window = MapCreationWindow(borderSize, settings["tile size"], settings["grid size"]["x"], settings["grid size"]["y"])
    Window.open()