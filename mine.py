import random
import pandas as pd
import copy

class Square:
    def __init__(self, y, x, adj=[], number=0, mine=False, cover=True, flag=False):
        self.loc = (y,x)
        self.adj = set()
        self.number = number
        self.mine = mine
        self.cover = cover
        self.flag = flag
        self.adj_flags = set()
        self.adj_covered = set()
        self.adj_numbers = set()
    
    def __str__(self):
        fs = f"({self.loc}, {self.number}, mine:{self.mine}, cover:{self.cover}, flag:{self.flag})"
        return fs

class Board:
    def __init__(self, height, width, mine_num):
        if mine_num > height*width:
            raise ValueError("Number of mines must not exceed number of cells.")
        self.height = height
        self.width = width
        self.total_squares = height*width
        self.mine_num = mine_num
        self.graph = {}
        self.game_status = 0    #0: game in progress, 1: game lost, 2: game won
        self.mine_set = set()
        self.num_covered = height*width
        self.flag_check = False
        self.sweep_check = False
        self.overlap_flag_check = False
        self.overlap_sweep_check = False
        self.click_set = set()
    
    def set_graph(self, y_click, x_click):
        squares = set([(y,x) for y in range(self.height) for x in range(self.width)])
        self.graph = {(loc[0],loc[1]):Square(loc[0],loc[1]) for loc in squares}
        for loc in self.graph:
            adj = set()
            for dis in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                if loc[0]+dis[0] in range(self.height) and loc[1]+dis[1] in range(self.width):
                    adj.add((loc[0]+dis[0],loc[1]+dis[1]))
                    self.graph[loc].adj = adj
                    self.graph[loc].adj_covered = adj.copy()

        start_click_condition = set([(y_click,x_click)])
        for adj in self.graph[(y_click,x_click)].adj:
            start_click_condition.add(adj)
        mine_locs = squares
        for pos in start_click_condition:
            mine_locs.discard(pos)

        self.mine_set = random.sample(mine_locs, self.mine_num)
        for mine in self.mine_set:
            self.graph[mine].mine = True
            self.graph[mine].number = -1
        for square in self.graph.values():
            if square.mine == False:
                square.number = len([s for s in square.adj if self.graph[s].mine==True])

        self.click((y_click,x_click))
        return self.reset_click_set()

    def click(self, loc):
        if self.graph[loc].cover:
            if self.graph[loc].number == -1:
                self.graph[loc].cover = False
                self.game_status = 1
            elif self.graph[loc].number == 0:
                self.graph[loc].cover = False
                self.click_set.add(loc)
                self.num_covered -= 1
                for adj_loc in self.graph[loc].adj:
                    self.graph[adj_loc].adj_covered.discard(loc)
                    self.click(adj_loc)
                return
            else:
                square = self.graph[loc]
                square.cover = False
                self.click_set.add(loc)
                self.num_covered -= 1
                for adj_loc in square.adj:
                    adj_square = self.graph[adj_loc]
                    adj_square.adj_covered.discard(loc)
                    adj_square.adj_numbers.add(loc)
                    if adj_square.flag:
                        square.adj_flags.add(adj_loc)
                return
        else:
            return

    def reset_click_set(self):
        cs = self.click_set.copy()
        self.click_set = set()
        return cs
    
    def flag(self):
        flagged = set()
        self.flag_check = False
        for square in self.graph.values():
            if not square.cover and square.number>0:
                adj_set = square.adj_covered
                if square.number == len(adj_set):
                    for adj_loc in adj_set:
                        if not self.graph[adj_loc].flag:
                            self.set_flag(adj_loc)
                            self.flag_check = True
                            flagged.add(adj_loc)
        return flagged

    def sweep(self):
        swept = set()
        self.sweep_check = False
        for square in self.graph.values():
            if square.number != 0 and not square.cover:
                adj_flags = square.adj_flags
                if square.number == len(adj_flags):
                    for adj_loc in square.adj - adj_flags:
                        if self.graph[adj_loc].cover:
                            self.click(adj_loc)
                            swept |= self.reset_click_set()
                            self.sweep_check = True
        return swept

    def overlap_flag(self):
        flagged = set()
        self.overlap_flag_check = False
        for square in self.graph.values():
            if square.number > 0 and not square.cover:
                rem_mines = square.number - len(square.adj_flags)
                square_set = square.adj_covered - square.adj_flags
                for adj_loc in square.adj_numbers.copy():
                    adj_square = self.graph[adj_loc]
                    adj_rem_mines = adj_square.number - len(adj_square.adj_flags)
                    adj_square_set = adj_square.adj_covered - adj_square.adj_flags
                    if len(square_set.intersection(adj_square_set))>adj_rem_mines and len(square_set-adj_square_set)+adj_rem_mines==rem_mines:
                        for s in square_set - adj_square_set:
                            self.set_flag(s)
                            self.overlap_flag_check = True
                            flagged.add(s)
        return flagged

    def overlap_sweep(self):
        swept = set()
        self.overlap_sweep_check = False
        for square in self.graph.values():
            if square.number > 0 and not square.cover:
                rem_mines = square.number - len(square.adj_flags)
                square_set = square.adj_covered - square.adj_flags
                for adj_loc in square.adj_numbers.copy():
                    adj_square = self.graph[adj_loc]
                    adj_rem_mines = adj_square.number - len(adj_square.adj_flags)
                    adj_square_set = adj_square.adj_covered - adj_square.adj_flags
                    if adj_rem_mines == rem_mines and adj_square_set.issubset(square_set):
                        for s in square_set - adj_square_set:
                            self.click(s)
                            swept |= self.reset_click_set()
                            self.overlap_sweep_check = True
        return swept
    
    def random_click(self):
        covered = [s for s in self.graph if self.graph[s].cover==True and self.graph[s].flag==False]
        loc = random.choice(covered)
        self.click(loc)
        return loc, self.reset_click_set()

    def set_flag(self, loc):
        square = self.graph[loc]
        square.flag = True
        for adj_loc in square.adj:
            adj_square = self.graph[adj_loc]
            adj_square.adj_flags.add(loc)

    def check_win(self):
        if self.num_covered == self.mine_num:
            self.game_status = 2

    def print_graph(self):
        df = pd.DataFrame(index=range(self.height), columns=range(self.width))
        for s in self.graph.values():
            df.loc[s.loc[0],s.loc[1]] = s.number
        print(df)
    
    def print_cover(self, graph):
        df = pd.DataFrame(index=range(self.height), columns=range(self.width))
        for s in graph.values():
            df.loc[s.loc[0],s.loc[1]] = s.cover
        print(df)