import random
import pandas as pd

class Square:
    def __init__(self, y, x, adj=[], number=0, mine=False, cover=True, flag=False):
        self.loc = (y,x)
        self.adj = set()
        self.number = number
        self.mine = mine
        self.cover = cover
        self.flag = flag
    
    def __str__(self):
        fs = f"({self.loc}, {self.number}, mine:{self.mine}, cover:{self.cover}, flag:{self.flag})"
        return fs

class Board:
    def __init__(self, height, width, mine_num):
        if mine_num > height*width:
            raise ValueError("Number of mines must not exceed number of cells.")
        self.height = height
        self.width = width
        self.mine_num = mine_num
        self.graph = {}
        self.game_status = 0
        self.mine_list = []
        self.uncovered_list = []
        self.flag_check = False
        self.sweep_check = False
        self.overlap_flag_check = False
        self.overlap_sweep_check = False
    
    def set_graph(self, y_click, x_click):
        squares = [(y,x) for y in range(self.height) for x in range(self.width)]
        self.graph = {(loc[0],loc[1]):Square(loc[0],loc[1]) for loc in squares}
        for loc in self.graph:
            for dis in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                if loc[0]+dis[0] in range(self.height) and loc[1]+dis[1] in range(self.width):
                    self.graph[loc].adj.add(self.graph[(loc[0]+dis[0],loc[1]+dis[1])])
        
        start_click_condition = [(y_click,x_click)]
        for adj in self.graph[(y_click,x_click)].adj:
            start_click_condition.append(adj.loc)
        mine_list = squares
        for pos in start_click_condition:
            mine_list.remove(pos)

        mines = random.sample(mine_list, self.mine_num)
        for mine in mines:
            self.graph[mine].mine = True
            self.graph[mine].number = -1
        for square in self.graph.values():
            if square.mine == False:
                square.number = len([s.loc for s in square.adj if s.mine==True])
        self.click(y_click,x_click)

    def click(self, y, x):
        if self.graph[(y,x)].cover == True:
            if self.graph[(y,x)].number == -1:
                self.graph[(y,x)].cover = False
                self.game_status = 1
            elif self.graph[(y,x)].number == 0:
                self.graph[(y,x)].cover = False
                for s in self.graph[(y,x)].adj:
                    self.click(s.loc[0], s.loc[1])
                return
            else:
                self.graph[(y,x)].cover = False
                return
        else:
            return
    
    def flag(self):
        self.flag_check = False
        for square in self.graph.values():
            if square.number == len([s.loc for s in square.adj if s.cover==True]) and square.number != 0 and square.cover == False:
                for adj in [s for s in square.adj if s.cover == True]:
                    if adj.flag == False:
                        adj.flag = True
                        self.flag_check = True

    def sweep(self):
        self.sweep_check = False
        for square in self.graph.values():
            if square.number == len([s.loc for s in square.adj if s.flag==True]) and square.number != 0 and square.cover == False:
                for adj_loc in [s.loc for s in square.adj if s.flag==False]:
                    if self.graph[adj_loc].cover == True:
                        self.click(adj_loc[0],adj_loc[1])
                        self.sweep_check = True
    
    def overlap_flag(self):
        self.overlap_flag_check = False
        for square in [s for s in self.graph.values() if s.number > 0 and s.cover == False]:
            rem_mines = square.number - len([s.loc for s in square.adj if s.flag==True])
            square_set = set([s for s in square.adj if s.cover==True and s.flag==False])
            for adj in [s for s in square.adj if s.cover==False and s.number>0]:
                adj_rem_mines = adj.number - len([s for s in adj.adj if s.flag==True])
                adj_square_set = set([s for s in adj.adj if s.cover==True and s.flag==False])
                if len(square_set.intersection(adj_square_set))>adj_rem_mines and len(square_set-adj_square_set)+adj_rem_mines==rem_mines:
                    for s in square_set - adj_square_set:
                        s.flag = True
                        self.overlap_flag_check = True

    def overlap_sweep(self):
        self.overlap_sweep_check = False
        for square in [s for s in self.graph.values() if s.number > 0 and s.cover == False]:
            rem_mines = square.number - len([s.loc for s in square.adj if s.flag==True])
            square_set = set([s for s in square.adj if s.cover==True and s.flag==False])
            for adj in [s for s in square.adj if s.cover==False and s.number>0]:
                adj_rem_mines = adj.number - len([s for s in adj.adj if s.flag==True])
                adj_square_set = set([s for s in adj.adj if s.cover==True and s.flag==False])
                if adj_rem_mines == rem_mines and adj_square_set.issubset(square_set):
                    for s in square_set - adj_square_set:
                        self.click(s.loc[0], s.loc[1])
                        self.overlap_sweep_check = True
    
    def random_click(self):
        covered = [s for s in self.graph if self.graph[s].cover==True and self.graph[s].flag==False]
        loc = random.choice(covered)
        self.click(loc[0],loc[1])

    def check_win(self):
        if len([s for s in self.graph.values() if s.flag==True]) == self.mine_num:
            self.game_status = 2

    def print_graph(self):
        df = pd.DataFrame(index=range(self.height), columns=range(self.width))
        for s in self.graph.values():
            df.loc[s.loc[0],s.loc[1]] = s.number
        print(df)
    
    def print_cover(self):
        df = pd.DataFrame(index=range(self.height), columns=range(self.width))
        for s in self.graph.values():
            df.loc[s.loc[0],s.loc[1]] = s.cover
        print(df)