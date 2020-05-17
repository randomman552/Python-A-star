#!/usr/bin/python3
import tkinter as tk
import tkinter.scrolledtext as tkst
import AStar
import random

# Create tkinter window
string_change = tk.Tk()
string_change.resizable(0, 0)
string_change.title('A* - String Change')

# Start Input
start_input = tk.Entry(string_change)
start_input.grid(column=2, row=2, sticky=tk.W)
start_inputLabel = tk.Label(string_change, text="Enter start text here: ")
start_inputLabel.grid(column=1, row=2, sticky=tk.E)

# Goal Input
goal_input = tk.Entry(string_change)
goal_input.grid(column=2, row=0, sticky=tk.W)
start_inputLabel = tk.Label(string_change, text="Enter goal text here: ")
start_inputLabel.grid(column=1, row=0, sticky=tk.E)

# Submit button

submit = tk.Button(string_change, text="submit",
                   command=lambda: submit_action())
submit.grid(column=2, row=3, sticky=tk.W, padx=(5, 0))


def submit_action():
    """
    Submit the information and begin the string reorganisation process.
    """

    # Disable the buttons
    submit.configure(state=tk.DISABLED)
    shuffle.configure(state=tk.DISABLED)

    # Get our start and goal strings
    goal = goal_input.get()
    start = start_input.get()

    # Initalise variables to store results
    path = []
    time_taken = 0
    nodes_considered = 0

    # Create the sovler object, and initiate the solving process
    try:
        solver = AStar.StringSolver(start, goal)
        solver.solve()
        path = solver.path
        time_taken = solver.time_taken
        nodes_considered = solver.nodes_considered
    except:
        path = ["No path"]

    # Enable the output box and empty it
    output_box.configure(state=tk.NORMAL)
    output_box.delete(1.0, tk.END)

    # Put the results in the output box
    for num, step in enumerate(path):
        output_box.insert(tk.END, str(num) + ": " + str(step) + "\n")
    output_box.insert(tk.END, "Time Taken: " + str(time_taken) + "ms\n")
    output_box.insert(tk.END, "Nodes Considered: " +
                      str(nodes_considered) + "\n")

    # Disable the output box so the user can't type in it
    output_box.configure(state=tk.DISABLED)

    # Re-enable submit and shuffle buttons
    submit.configure(state=tk.NORMAL)
    shuffle.configure(state=tk.NORMAL)

# Auto-shuffle button


shuffle = tk.Button(string_change, text="shuffle",
                    command=lambda: shuffle_action(goal_input.get()))
shuffle.grid(column=1, row=3, sticky=tk.E, padx=(0, 5))


def shuffle_action(goal):
    """
    Shuffle the text in the start box and put the results in the goal text box.
    """

    temp = list(goal)
    random.shuffle(temp)
    start = ""
    for char in temp:
        start += char
    start_input.delete(0, tk.END)
    start_input.insert(0, start)


# Output box
output_box = tkst.ScrolledText(
    string_change, state=tk.DISABLED, width=40, height=10)
output_box.grid(column=0, columnspan=4, row=4, rowspan=1)

# Open the window
string_change.mainloop()
