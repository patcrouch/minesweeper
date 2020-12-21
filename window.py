import tkinter as tk
from tkinter import ttk
from mine_page import MinePage
from mine import Board

'''
Window class is baseline for all tkinter apps
Each frame that is added to the frame dictionary is a new object
The objects are defined in separate classes
'''

class Window(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        #pack pushes the element to one side
        #fill fills space alloted by pack
        #expand allows to fill available white space
        container.pack(side='top', fill='both', expand=True)

        #0 sets minimum size
        #weight sets priority
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #dictionary of frames to be used in the main window
        self.frames = {}
        mineframe = MinePage(container, self)
        self.frames['Mine'] = mineframe
        mineframe.grid(row=0, column=0, sticky='nsew')


        #sets starting frame page
        #parent is container, controller is itself
        #optiframe = OptimizerPage(self.optimizer, container, self)
        #self.frames['Optimizer'] = optiframe

        #grid allows for better placement of elements
        #sticky parameter stretches everything to direction specified
        #optiframe.grid(row=0, column=0, sticky='nsew')
        #playerframe.grid(row=0, column=0, sticky='nsew')

        '''
        tabs = ttk.Notebook(container)

        for frame in self.frames:
            tabs.add(self.frames[frame], text = '   '+frame+'   ')

        tabs.grid()

        self.show_frame('Optimizer')
        self.show_frame('Players')
        '''
        self.show_frame('Mine')

    #moves given frame from frames to front
    def show_frame(self, page):
        frame = self.frames[page]
        #moves frame to the front
        frame.tkraise()

    def get_page(self, page):
        return self.frames[page]
