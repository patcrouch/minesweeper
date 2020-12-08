import tkinter as tk
from tkinter import ttk
from flag_sweep import FlagSweep

class MinePage(tk.Frame):

    def __init__(self, board, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.board = board
        self.step_count = 0


        self.start_loc = tk.StringVar()
        self.start_loc.set('0 0')
        self.height = tk.IntVar()
        self.height.set(16)
        self.width = tk.IntVar()
        self.width.set(16)
        self.mine_num = tk.IntVar()
        self.mine_num.set(40)
        self.can_dict = {}

    
        height_label = tk.Label(self, text="Height:")
        height_label.grid(row=0,column=0,columnspan=2,sticky='nesw')
        height_entry = tk.Entry(self,width=4,font=24,textvariable=self.height)
        height_entry.grid(row=0,column=2,columnspan=2)

        width_label = tk.Label(self, text="Width:")
        width_label.grid(row=0,column=4,columnspan=2,sticky='nesw')
        width_entry = tk.Entry(self,width=4,font=24,textvariable=self.width)
        width_entry.grid(row=0,column=6,columnspan=2,sticky='nesw')

        mine_label = tk.Label(self, text="Mines:")
        mine_label.grid(row=0,column=8,columnspan=2,sticky='nesw')
        mine_entry = tk.Entry(self,width=4,font=24,textvariable=self.mine_num)
        mine_entry.grid(row=0,column=10,columnspan=2,sticky='nesw')

        start_loc_label = tk.Label(self, text="Starting Position y x:")
        start_loc_label.grid(row=1,column=0,columnspan=5)
        start_loc_entry = tk.Entry(self,width=5,font=24,textvariable=self.start_loc)
        start_loc_entry.grid(row=1,column=5,columnspan=3)

        step_button = tk.Button(self, text='Step ->',command=lambda: self.adj_overlap_step())
        step_button.grid(row=1,column=8,columnspan=2)

        reset_button = tk.Button(self, text="Reset",command=lambda: self.reset())
        reset_button.grid(row=1,column=10,columnspan=2)
        

    def init_squares(self):
        for y in range(self.board.height):
            for x in range(self.board.width):
                self.can_dict[(y,x)] = tk.Canvas(self, bg='white', height=20, width=20)

    def set_squares(self):
        for loc in self.can_dict:
            if self.board.graph[loc].number > 0 and self.board.graph[loc].cover == False:
                self.can_dict[loc].create_text(12,12,text = str(self.board.graph[loc].number))
            if self.board.graph[loc].cover == True:
                self.can_dict[loc]['bg'] = 'gray'
            if self.board.graph[loc].cover == False:
                self.can_dict[loc]['bg'] = 'white'
            if self.board.graph[loc].flag == True:
                self.can_dict[loc]['bg'] = 'blue'
            self.can_dict[loc].grid(row=loc[0]+2,column=loc[1])
      
    def flagsweep_step(self):
        if self.step_count == 0:
            self.board = FlagSweep(self.height.get(),self.width.get(),self.mine_num.get())
            loc = self.start_loc.get()
            self.board.set_graph(int(loc[0]),int(loc[-1]))
            self.init_squares()
        elif self.step_count%2 == 1:
            self.board.flag()
        else:
            self.board.sweep()
        self.set_squares()
        self.step_count += 1

    def adj_overlap_step(self):
        if self.step_count == 0:
            self.board = FlagSweep(self.height.get(),self.width.get(),self.mine_num.get())
            loc = self.start_loc.get()
            self.board.set_graph(int(loc[0]),int(loc[-1]))
            self.init_squares()
        else:
            self.board.adj_overlap()
        self.set_squares()
        self.step_count += 1

    def reset(self):
        for can in self.can_dict.values():
            can.destroy()
        self.can_dict = {}
        self.step_count = 0


