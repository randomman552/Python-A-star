#!/usr/bin/python3
import pygame
import AStar
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
        self.window = window
        self.size = size
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = (255,255,255)

    def draw(self):
        "Draw the tile on the pygame window"
        if self.enabled:
            pygame.draw.rect(self.window, self.color, (self.x_pos + 1, self.y_pos + 1, self.size - 2, self.size - 2))
class MapCreationWindow(object):
    "Pygame window with removable tiles, allows for editing of the map and running of the path finding algorithm."
    def __init__(self, borderSize, tileSize, x_tiles, y_tiles):
        pygame.init()
        self.windowSize = (x_tiles * tileSize + borderSize, y_tiles * tileSize + borderSize)
        self.window = pygame.display.set_mode(self.windowSize)
        pygame.display.set_caption("A* Path Finder")
        self.__borderSize = borderSize
        self.__tileSize = tileSize
        self.__x_tiles = x_tiles
        self.__y_tiles = y_tiles
        self.tile_list = self.__create_tiles()

    def __create_tiles(self):
        "Create the tileList variable filled with tile objects. Each tile represents a portion of the screen."
        tile_list = []
        for x in range(self.__x_tiles):
            for y in range(self.__y_tiles):
                tileSize = self.__tileSize
                borderSize = self.__borderSize
                tile_list.append(tile(self.window, tileSize, borderSize // 2 + x * tileSize, borderSize // 2 + y * tileSize))
        return tile_list

    def get_cur_tile(self, pos):
        "When given an x and y coordinate in the form (x,y), will return the tile that occupies that position."
        #If the cursor is in the lower border, return None to prevent the changing of the opposite tiles
        if pos[0] < borderSize // 2 or pos[1] < borderSize // 2:
            return None
        x_num = self.__x_tiles
        y_num = self.__y_tiles
        tile_x = int(((pos[1] - self.__borderSize // 2) / self.__tileSize) + 1)
        tile_y = int(((pos[0] - self.__borderSize // 2) / self.__tileSize) + 1)
        #If the tile selected is outside of the array, return None to prevent crashes
        if tile_x > x_num or tile_y > y_num:
            return None
        tile = self.tile_list[((tile_y - 1) * x_num) + tile_x - 1]
        return tile

    def open(self):
        "Opens the tiles window, and allows for editing."
        running = True
        mouseDown = False
        window = self.window
        tile_list = self.tile_list
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouseDown = True 
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouseDown = False
            
            if mouseDown:
                mousePresses = pygame.mouse.get_pressed()
                mousePosition = pygame.mouse.get_pos()
                tile = self.get_cur_tile(mousePosition)
                if tile != None:
                    if mousePresses[0]:
                        tile.enabled = False
                    elif mousePresses[1]:
                        tile.enabled = True
                        tile.color = (0,0,255)
                    elif mousePresses[2]:
                        tile.enabled = True
                        tile.color = (255,255,255)
            window.fill((200,200,200))
            for tile in tile_list:
                tile.draw()
            pygame.display.update()

    def close(self):
        pygame.quit()

settings_window = DefineSettings()
settings = settings_window.open()

borderSize = 10
Window = MapCreationWindow(borderSize, settings["tile size"], settings["grid size"]["x"], settings["grid size"]["y"])
Window.open()