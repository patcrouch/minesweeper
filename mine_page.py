import tkinter as tk
from tkinter import ttk
from mine import Board
import copy
import time

class MinePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.step_count = 0
        self.board_list = []

        self.start_loc = tk.StringVar()
        self.start_loc.set('0,0')
        self.height = tk.IntVar()
        self.height.set(16)
        self.width = tk.IntVar()
        self.width.set(16)
        self.mine_num = tk.IntVar()
        self.mine_num.set(40)
        self.random_click = (0,0)

        self.to_flag = set()
        self.to_click = set()

        self.board = Board(self.height.get(),self.width.get(),self.mine_num.get())

        height_frame = tk.Frame(self)
        height_label = tk.Label(height_frame, text="Height:",width=6,anchor='e')
        height_label.grid(row=0,column=0,columnspan=1,sticky='e',pady=4)
        height_entry = tk.Entry(height_frame,width=4,font=24,textvariable=self.height,relief=tk.GROOVE,bd=2)
        height_entry.grid(row=0,column=1,columnspan=1,sticky='w',pady=4)
        height_frame.grid(row=0,column=0)

        width_frame = tk.Frame(self)
        width_label = tk.Label(width_frame, text="Width:",width=6,anchor='e')
        width_label.grid(row=0,column=0,columnspan=1,sticky='e',pady=4)
        width_entry = tk.Entry(width_frame,width=4,font=24,textvariable=self.width,relief=tk.GROOVE,bd=2)
        width_entry.grid(row=0,column=1,columnspan=1,sticky='w',pady=4)
        width_frame.grid(row=0,column=1)

        mine_frame = tk.Frame(self)
        mine_label = tk.Label(mine_frame, text="Mines:",width=6,anchor='e')
        mine_label.grid(row=0,column=0,columnspan=1,sticky='e',pady=4)
        mine_entry = tk.Entry(mine_frame,width=4,font=24,textvariable=self.mine_num,relief=tk.GROOVE,bd=2)
        mine_entry.grid(row=0,column=1,columnspan=1,sticky='w',pady=4)
        mine_frame.grid(row=0,column=2)

        start_loc_frame = tk.Frame(self)
        start_loc_label = tk.Label(start_loc_frame, text="Starting Position y,x:",width=16,anchor='e')
        start_loc_label.grid(row=1,column=0,columnspan=2,sticky='e',pady=4)
        start_loc_entry = tk.Entry(start_loc_frame,width=5,font=24,textvariable=self.start_loc,relief=tk.GROOVE,bd=2)
        start_loc_entry.grid(row=1,column=3,columnspan=1,sticky='w',pady=4)
        start_loc_frame.grid(row=1,column=0,columnspan=3)

        step_back_button = tk.Button(self, text='<- Step',command=lambda: self.step_back())
        step_back_button.grid(row=2,column=0,sticky='e',padx=1,pady=4)

        step_button = tk.Button(self, text='Step ->',command=lambda: self.step())
        step_button.grid(row=2,column=1,sticky='w',padx=1,pady=4)

        reset_button = tk.Button(self, text="Reset",command=lambda: self.reset())
        reset_button.grid(row=2,column=2,padx=1,pady=4)

        self.step_log = tk.Text(self, height=25, width=30, state=tk.DISABLED, relief=tk.RIDGE,bd=4)
        self.step_log.grid(row=3,column=0,columnspan=3,padx=4,pady=4)
        
        self.board_canvas = tk.Canvas(self, bg='white smoke', height=self.board.height*25,width=self.board.width*25)

    def set_can_squares(self):
        for y in range(self.board.height):
            for x in range(self.board.width):
                pos = self.get_pos(y,x)
                if self.board.graph[(y,x)].cover and not self.board.graph[(y,x)].flag:
                    self.board_canvas.create_polygon(pos, fill='gray')

    def initiate_canvas(self):
        for y in range(self.board.height):
            for x in range(self.board.width):
                pos = self.get_pos(y,x)
                self.board_canvas.create_polygon(pos, fill='gray')

    def set_flags(self):
        for loc in self.to_flag:
            pos = self.get_pos(loc[0],loc[1])
            self.board_canvas.create_polygon(pos, fill='blue')
        self.to_flag = set()
    
    def set_clicked(self):
        for loc in self.to_click:
            y = loc[0]
            x = loc[1]
            pos = self.get_pos(y,x)
            text_pos = x*25+15, y*25+15
            self.board_canvas.create_polygon(pos, fill='white')
            if self.board.graph[loc].number > 0:
                self.board_canvas.create_text(text_pos,text=str(self.board.graph[(y,x)].number),anchor=tk.CENTER, font=('arial black',9), fill='gray20')
        self.to_click = set()

    def step(self):
        if self.board.game_status != 0:
            self.reset()
            self.board.game_status = 0
            return
        if self.step_count == 0:
            self.board = Board(self.height.get(),self.width.get(),self.mine_num.get())
            loc = self.start_loc.get().split(',')
            self.to_click = self.board.set_graph(int(loc[0]),int(loc[1]))
            self.board_canvas = tk.Canvas(self, bg='gray82', height=self.board.height*25+2,width=self.board.width*25+2)
            self.board_canvas.grid(row=0,column=8,rowspan=4,padx=4)
            self.initiate_canvas()
            self.set_clicked()
            self.update_log(f"{self.step_count}: Initial Click")
        else:
            self.algorithm_operations()
        self.board.check_win()
        if self.board.game_status == 1:
            self.update_log('GAME OVER')
            for mine in self.board.mine_set:
                y = mine[0]
                x = mine[1]
                if not self.board.graph[(y,x)].flag:
                    pos = self.get_pos(y,x)
                    if mine == self.random_click:
                        self.board_canvas.create_polygon(pos, fill='gray12')
                    else:
                        self.board_canvas.create_polygon(pos, fill='red')
                
        elif self.board.game_status == 2:
            self.update_log('CONGRATS!')
            self.to_flag = self.board.mine_set
        self.set_flags()
        self.set_clicked()
        self.step_count += 1
        self.board_list.append(copy.deepcopy(self.board))


    def step_back(self):
        if len(self.board_list) > 1:
            self.step_log.configure(state = tk.NORMAL)
            if self.board.game_status == 0:
                self.step_log.delete('end-2l', 'end-1c')
            else:
                self.step_log.delete('end-3l', 'end-1c')
            self.step_log.configure(state = tk.DISABLED)
            self.board_list.pop()
            self.board = copy.deepcopy(self.board_list[-1])
            self.set_can_squares()
            self.step_count -= 1

    def algorithm_operations(self):
        tc = self.board.sweep()
        if self.board.sweep_check:
            self.to_click = tc
            self.update_log(f"{self.step_count}: Sweep")
            return
        tf = self.board.flag()
        if self.board.flag_check:
            self.to_flag = tf
            self.update_log(f"{self.step_count}: Flag")
            return
        tc = self.board.overlap_sweep()
        if self.board.overlap_sweep_check:
            self.to_click = tc
            self.update_log(f"{self.step_count}: Overlap Sweep")
            return
        tf = self.board.overlap_flag()
        if self.board.overlap_flag_check:
            self.to_flag = tf
            self.update_log(f"{self.step_count}: Overlap Flag")
            return
        self.random_click, self.to_click = self.board.random_click()
        self.update_log(f"{self.step_count}: Random Click")

    def get_pos(self,y,x):
        return x*25+4, y*25+4, x*25+4, (y+1)*25+2, (x+1)*25+2, (y+1)*25+2, (x+1)*25+2, y*25+4
    
    def update_log(self, desc):
        self.step_log.configure(state = tk.NORMAL)
        self.step_log.insert(tk.END, desc+'\n')
        self.step_log.configure(state = tk.DISABLED)

    def reset(self):
        self.board_canvas.destroy()
        self.board_list = []
        self.step_count = 0
        self.board.game_status = 0
        self.step_log.configure(state=tk.NORMAL)
        self.step_log.delete(1.0, tk.END)
        self.step_log.configure(state=tk.DISABLED)
        


