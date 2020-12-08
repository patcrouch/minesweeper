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
        self.game_status = True
    
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
                self.game_status = False
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
'''
b = Board(5,5,2)
b.set_graph()
b.click(4,4)
b.print_graph()

for i in b.graph:
    print(b.graph[i])
'''