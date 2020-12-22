import tkinter as tk
from mine import Board
import copy

#main class that contains all UI elements
class MinePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.step_count = 0     #keeps track of steps to be displayed on steplog
        self.board_list = []

        #all variables used in entries
        self.start_loc = tk.StringVar()
        self.start_loc.set('3,7')
        self.height = tk.IntVar()
        self.height.set(16)
        self.min_height = 4     #max and min values help prevent errors
        self.max_height = 16
        self.width = tk.IntVar()
        self.width.set(16)
        self.min_width = 8
        self.max_width = 30
        self.mine_num = tk.IntVar()
        self.mine_num.set(40)

        self.random_click = (0,0)   #used if random_click is called

        #used to update board after flag and sweep are called
        self.to_flag = set()
        self.to_click = set()

        #main board
        self.board = Board(self.height.get(),self.width.get(),self.mine_num.get())

        #widgets for necessary entries
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

        #buttons to perform tasks
        step_back_button = tk.Button(self, text='<- Step',command=lambda: self.step_back())
        step_back_button.grid(row=2,column=0,sticky='e',padx=1,pady=4)

        step_button = tk.Button(self, text='Step ->',command=lambda: self.step())
        step_button.grid(row=2,column=1,sticky='w',padx=1,pady=4)

        reset_button = tk.Button(self, text="Reset",command=lambda: self.reset())
        reset_button.grid(row=2,column=2,padx=1,pady=4)

        #text widget to keep track of each step
        self.step_log = tk.Text(self, height=25, width=30, state=tk.DISABLED, relief=tk.RIDGE,bd=4)
        self.step_log.grid(row=3,column=0,columnspan=3,padx=4,pady=4)
        
        #canvas widget that displays board
        self.board_canvas = tk.Canvas(self)

    #step function called when step button is pressed
    def step(self):
        #if step is pressed when a game is over, the board is reset
        if self.board.game_status != 0:
            self.reset()
            self.board.game_status = 0
            return
        #if it is te first step, canvas is initiated
        if self.step_count == 0:
            self.initiate_canvas()
        #otherwise, normal algorihtm is performed
        else:
            self.algorithm_operations()
        self.win_loss_scenarios()   #wins and losses are checked with each step

        #canvas is updated with flags and clicks
        self.set_flags()
        self.set_clicked()
        self.step_count += 1
        self.board_list.append(copy.deepcopy(self.board))   #record of the board is stored for step_back function

    def initiate_canvas(self):
        #series of conditions to ensure entries are within min and max values
        height = self.height.get()
        if height > self.max_height:
            self.height.set(self.max_height)
        if height < self.min_height:
            self.height.set(self.min_height)
        width = self.width.get()
        if width > self.max_width:
            self.width.set(self.max_width)
        if width < self.min_width:
            self.width.set(self.min_width)
        mine_num = self.mine_num.get()
        max_mines = int(height*width/4.8)
        if mine_num > max_mines:
            self.mine_num.set(max_mines)
        if mine_num < 1:
            self.mine_num.set(1)
        self.board = Board(self.height.get(),self.width.get(),self.mine_num.get())  #board initialized
        loc = self.start_loc.get().split(',')
        loc = (int(loc[0]),int(loc[1]))
        if loc[0] > self.board.height:
            loc = (self.board.height-1,loc[1])
        if loc[0] < 0:
            loc = (0,loc[1])
        if loc[1] > self.board.width:
            loc = (loc[0],self.board.width-1)
        if loc[1] < 0:
            loc = (loc[0],0)
        self.start_loc.set(f"{loc[0]},{loc[1]}")

        #board is clicked at position specified and canvas is created
        self.to_click = self.board.set_graph(loc[0],loc[1])
        self.board_canvas = tk.Canvas(self, bg='gray82', height=self.board.height*25+2,width=self.board.width*25+2)
        self.board_canvas.grid(row=0,column=8,rowspan=4,padx=4)
        #canvas is populated with gray squares to indicate covered squares
        for y in range(self.board.height):
            for x in range(self.board.width):
                pos = self.get_pos(y,x)
                self.board_canvas.create_polygon(pos, fill='gray')
        self.set_clicked()  #canvas is updated to reflect initial click
        self.update_log(f"{self.step_count}: Initial Click")
 
    #runs the four algorithms in order seen
    #if algorithm changes the board state, the function is returned
    #if not, the function continues to the next possible algorithm
    def algorithm_operations(self):
        #sweep function is redundant with overlap_sweep
        #amount of steps is decreased but it may cause more lag
        '''
        tc = self.board.sweep()
        if self.board.sweep_check:
            self.to_click = tc 
            self.update_log(f"{self.step_count}: Sweep")    
            return
        '''
        tc = self.board.overlap_sweep()
        if self.board.overlap_sweep_check:
            self.to_click = tc  #to_click and to_flag sets are updated to be reflected on canvas
            self.update_log(f"{self.step_count}: Overlap Sweep")    #log is updated with each step
            return
        tf = self.board.flag()
        if self.board.flag_check:
            self.to_flag = tf
            self.update_log(f"{self.step_count}: Flag")
            return

        tf = self.board.overlap_flag()
        if self.board.overlap_flag_check:
            self.to_flag = tf
            self.update_log(f"{self.step_count}: Overlap Flag")
            return
        self.random_click, self.to_click = self.board.random_click()
        self.update_log(f"{self.step_count}: Random Click")

    #does checks for win and loss scenarios and updates canvas and log accordingly
    def win_loss_scenarios(self):
        #if game is lost, then the clicked mine is turned black and all unflagged mines are red
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

        #if game is won, all unflagged mines are turned
        self.board.check_win()       
        if self.board.game_status == 2:
            self.update_log('CONGRATS!')
            self.to_flag = self.board.mine_set
        

    #updates canvas with flags and clicks
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

    #step_back function uses recorded board states and reverts back to the previous step
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
            self.reset_squares()    #canvas is updated to the last board state
            self.step_count -= 1

    #changes squares that were flagged or clicked in previous step back to gray
    def reset_squares(self):
        for y in range(self.board.height):
            for x in range(self.board.width):
                pos = self.get_pos(y,x)
                if self.board.graph[(y,x)].cover and not self.board.graph[(y,x)].flag:
                    self.board_canvas.create_polygon(pos, fill='gray')

    #utility functions for code legibility
    def get_pos(self,y,x):
        return x*25+4, y*25+4, x*25+4, (y+1)*25+2, (x+1)*25+2, (y+1)*25+2, (x+1)*25+2, y*25+4
    
    def update_log(self, desc):
        self.step_log.configure(state = tk.NORMAL)
        self.step_log.insert(tk.END, desc+'\n')
        self.step_log.configure(state = tk.DISABLED)

    #resets all elements of the UI by destroying the canvas, step log, and board memory
    def reset(self):
        self.board_canvas.destroy()
        self.board_list = []
        self.step_count = 0
        self.board.game_status = 0
        self.step_log.configure(state=tk.NORMAL)
        self.step_log.delete(1.0, tk.END)
        self.step_log.configure(state=tk.DISABLED)
        


