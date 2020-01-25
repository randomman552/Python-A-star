#!/usr/bin/python3
import pygame
import AStar
import tkinter as tk
from tkinter import messagebox as ms_box

class DefineSettings(object):
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
            MessageBox = ms_box.Message(self.window, icon=ms_box.WARNING ,message="Invalid inputs.", title="Warning")
            MessageBox.show()

    def close(self):
        self.window.destroy()
        return self.settings
    
    def open(self):
        self.window.mainloop()
        return self.settings
class tile(object):
    def __init__(self, window, size, x_pos, y_pos):
        self.enabled = True
        self.window = window
        self.size = size
        self.x_pos = x_pos
        self.y_pos = y_pos

    def draw(self):
        if self.enabled:
            pygame.draw.rect(self.window, (255,255,255), (self.x_pos, self.y_pos, self.size, self.size))

StartWindow = DefineSettings()
Settings = StartWindow.open()

pygame.init()
windowSize = (Settings["grid size"]["x"] * Settings["tile size"], Settings["grid size"]["y"] * Settings["tile size"])
window = pygame.display.set_mode(windowSize)
pygame.display.set_caption("A* Path Finder")


running = True
while running:
    pygame.time.delay(100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    window.fill((200,200,200))
    pygame.display.update()

pygame.quit()
quit()