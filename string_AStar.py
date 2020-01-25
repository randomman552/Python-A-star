#!/usr/bin/python3
import tkinter as tk
import tkinter.scrolledtext as tkst
import AStar
import random

String_Change = tk.Tk()
String_Change.resizable(0,0)
String_Change.title('A* - String Change')
ForDisplay = [] # List to store all elements for the display.

#Start Input
StartInput = tk.Entry(String_Change)
StartInput.grid(column=2, row=2, sticky=tk.W)
StartInputLabel = tk.Label(String_Change, text="Enter start text here: ")
StartInputLabel.grid(column=1, row=2, sticky=tk.E)

#Goal Input
GoalInput = tk.Entry(String_Change)
GoalInput.grid(column=2, row=0, sticky=tk.W)
StartInputLabel = tk.Label(String_Change, text="Enter goal text here: ")
StartInputLabel.grid(column=1, row=0, sticky=tk.E)

#Submit button
def submit_action():
    Submit.configure(state=tk.DISABLED)
    Shuffle.configure(state=tk.DISABLED)
    goal = GoalInput.get()
    start = StartInput.get()
    path = []
    time_taken = 0
    nodes_considered = -0
    try:
        a = AStar.String_Solver(start, goal)
        a.Solve()
        path = a.path
        time_taken = a.time_taken
        nodes_considered = a.nodes_considered
    except: 
        path = ["No path"]
    OutputBox.configure(state=tk.NORMAL)
    OutputBox.delete(1.0, tk.END)
    for num,step in enumerate(path):
        OutputBox.insert(tk.END, str(num) + ": " + str(step) + "\n")
    OutputBox.insert(tk.END, "Time Taken: " + str(time_taken) + "ms\n")
    OutputBox.insert(tk.END, "Nodes Considered: " + str(nodes_considered) + "\n")
    OutputBox.configure(state=tk.DISABLED)
    Submit.configure(state=tk.NORMAL)
    Shuffle.configure(state=tk.NORMAL)
Submit = tk.Button(String_Change, text="Submit", command=lambda: submit_action())
Submit.grid(column=2, row=3, sticky=tk.W, padx=(5,0))

#Auto-shuffle button:
def shuffle_action(goal):
    temp = list(goal)
    random.shuffle(temp)
    start = ""
    for char in temp:
        start += char
    StartInput.delete(0, tk.END)
    StartInput.insert(0, start)
Shuffle = tk.Button(String_Change, text="Shuffle", command=lambda: shuffle_action(GoalInput.get()))
Shuffle.grid(column=1, row=3, sticky=tk.E, padx=(0,5))

#Output
OutputBox = tkst.ScrolledText(String_Change, state=tk.DISABLED, width=40, height=10)
OutputBox.grid(column=0, columnspan=4, row=4, rowspan=1)
String_Change.mainloop()