#!/usr/bin/python3
import pygame
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
        TileSize_Input.grid(column=2, row=0, sticky=tk.W)

        #Grid size input
        GridSizeX_Label = tk.Label(self.window, text="X:")
        GridSizeX_Label.grid(column=1, row=1, sticky=tk.E)

        GridSizeY_Label = tk.Label(self.window, text="Y:")
        GridSizeY_Label.grid(column=1, row=2, sticky=tk.E)

        GridSizeX_Input = tk.Entry(self.window)
        GridSizeX_Input.configure(width=3)
        GridSizeX_Input.grid(column=2, row=1, sticky=tk.W)

        GridSizeY_Input = tk.Entry(self.window)
        GridSizeY_Input.configure(width=3)
        GridSizeY_Input.grid(column=2, row=2, sticky=tk.W)

        #Buttons
        Submit_Button = tk.Button(self.window, text="Generate", command=lambda: self.__submit())
        Submit_Button.grid(column=2, row=3, columnspan=2, sticky=tk.W)

        Cancel_Button = tk.Button(self.window, text="Cancel", command=lambda: self.__close())
        Cancel_Button.grid(column=0, row=3, columnspan=2, sticky=tk.E)

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
            self.__close()
        except:
            MessageBox = ms_box.Message(self.window, icon=ms_box.WARNING ,message="Invalid inputs.", title="Warning")
            MessageBox.show()

    def __close(self):
        self.window.destroy()
        return self.settings
    
    def open(self):
        self.window.mainloop()
        return self.settings

StartWindow = DefineSettings()
StartWindow.open()
pygame.init()
window = pygame.display.set_mode((500,500))
pygame.display.set_caption("A* Path Finder")

running = True
while running:
    pygame.time.delay(100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.draw.rect(window, (255,255,255), (50, 50, 50, 50))
    pygame.display.update()

pygame.quit()