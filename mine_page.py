import tkinter as tk
from tkinter import ttk
from mine import Board

class MinePage(tk.Frame):

    step_button_set = {
        'set': {}
    }

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
        self.square_dict = {}
    
        height_label = tk.Label(self, text="Height:",width=6,anchor='e')
        height_label.grid(row=0,column=0,columnspan=1,sticky='e',pady=4)
        height_entry = tk.Entry(self,width=4,font=24,textvariable=self.height)
        height_entry.grid(row=0,column=1,columnspan=1,sticky='w',pady=4)

        width_label = tk.Label(self, text="Width:",width=6,anchor='e')
        width_label.grid(row=0,column=2,columnspan=1,sticky='e',pady=4)
        width_entry = tk.Entry(self,width=4,font=24,textvariable=self.width)
        width_entry.grid(row=0,column=3,columnspan=1,sticky='w',pady=4)

        mine_label = tk.Label(self, text="Mines:",width=6,anchor='e')
        mine_label.grid(row=0,column=4,columnspan=1,sticky='e',pady=4)
        mine_entry = tk.Entry(self,width=4,font=24,textvariable=self.mine_num)
        mine_entry.grid(row=0,column=5,columnspan=1,sticky='w',pady=4)

        start_loc_label = tk.Label(self, text="Starting Position y x:",width=16,anchor='e')
        start_loc_label.grid(row=0,column=6,columnspan=1,sticky='e',pady=4)
        start_loc_entry = tk.Entry(self,width=5,font=24,textvariable=self.start_loc)
        start_loc_entry.grid(row=0,column=7,columnspan=1,sticky='w',pady=4)

        step_button = tk.Button(self, text='Step ->',command=lambda: self.step())
        step_button.grid(row=1,column=2,columnspan=1)

        reset_button = tk.Button(self, text="Reset",command=lambda: self.reset())
        reset_button.grid(row=1,column=3,columnspan=1)

        self.step_log = tk.Text(self, height=20, width=30, state=tk.DISABLED)
        self.step_log.grid(row=2,column=0,rowspan=16,columnspan=6)
        
        self.board_canvas = tk.Canvas(self)
        #self.set_can_squares()
        #self.board_canvas.grid(row=0,column=6,rowspan=4)

    def init_squares(self):
        for y in range(self.board.height):
            for x in range(self.board.width):
                self.can_dict[(y,x)] = tk.Canvas(self, bg='white', height=20, width=20)

    def set_can_squares(self):
        for y in range(self.board.height):
            for x in range(self.board.width):
                pos = x*20+1, y*20+1, x*20+1, (y+1)*20-1, (x+1)*20-1, (y+1)*20-1, (x+1)*20-1, y*20+1
                text_pos = x*20+10, y*20+10

                if self.board.graph[(y,x)].cover == False:
                    self.board_canvas.create_polygon(pos, fill='white')
                if self.board.graph[(y,x)].number > 0:  
                    self.board_canvas.create_text(text_pos,text=str(self.board.graph[(y,x)].number),anchor=tk.CENTER)
                if self.board.graph[(y,x)].cover == True:
                    self.board_canvas.create_polygon(pos, fill='gray')
                if self.board.graph[(y,x)].flag == True:
                    self.board_canvas.create_polygon(pos, fill='blue')
                if self.board.graph[(y,x)].mine == True and self.board.graph[(y,x)].cover == False:
                    self.board_canvas.create_polygon(pos, fill='red')
                

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
            if self.board.graph[loc].mine == True and self.board.graph[loc].cover == False:
                self.can_dict[loc]['bg'] = 'red'
            self.can_dict[loc].grid(row=loc[0],column=loc[1]+6)

    def step(self):
        if self.board.game_status != 0:
            self.reset()
            self.board.game_status = 0
            return
        if self.step_count == 0:
            self.board = Board(self.height.get(),self.width.get(),self.mine_num.get())
            loc = self.start_loc.get()
            self.board.set_graph(int(loc[0]),int(loc[-1]))
            self.board_canvas = tk.Canvas(self, bg='white smoke', height=self.board.height*20,width=self.board.width*20)
            self.board_canvas.grid(row=0,column=8,rowspan=4)
            self.set_can_squares()
            self.update_log(f"{self.step_count}: Initial Click")
        else:
            self.algorithm_operations()
        self.board.check_win()
        if self.board.game_status == 1:
            self.update_log('GAME OVER')
            for s in [s for s in self.board.graph.values() if s.mine==True and s.flag==False]:
                s.cover = False
        elif self.board.game_status == 2:
            self.update_log('CONGRATS!')
            for s in [s for s in self.board.graph.values() if s.mine==False and s.cover==True]:
                s.cover = False
        #self.set_squares()
        self.set_can_squares()
        self.step_count += 1

    def algorithm_operations(self):
        self.board.flag()
        if self.board.flag_check:
            self.update_log(f"{self.step_count}: Flag")
            return
        self.board.sweep()
        if self.board.sweep_check:
            self.update_log(f"{self.step_count}: Sweep")
            return
        self.board.overlap_flag()
        if self.board.overlap_flag_check:
            self.update_log(f"{self.step_count}: Overlap Flag")
            return
        self.board.overlap_sweep()
        if self.board.overlap_sweep_check:
            self.update_log(f"{self.step_count}: Overlap Sweep")
            return
        self.board.random_click()
        self.update_log(f"{self.step_count}: Random Click")
    
    def update_log(self, desc):
        self.step_log.configure(state = tk.NORMAL)
        self.step_log.insert(tk.END, desc+'\n')
        self.step_log.configure(state = tk.DISABLED)

    def reset(self):
        self.board_canvas.destroy()
        self.step_count = 0
        self.step_log.configure(state=tk.NORMAL)
        self.step_log.delete(1.0, tk.END)
        self.step_log.configure(state=tk.DISABLED)
        


