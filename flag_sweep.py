from mine import Board, Square

class FlagSweep(Board):
    def __init__(self, height, length, mine_num):
        super().__init__(height, length, mine_num)
        self.mine_list = []
        self.uncovered_list = []
    
    def uncover(self, y, x):
        self.click(y,x)

    def flag(self):
        for square in self.graph.values():
            if square.number == len([s.loc for s in square.adj if s.cover==True]) and square.number != 0 and square.cover == False:
                for adj in [s for s in square.adj if s.cover == True]:
                    if adj.flag == False:
                        adj.flag = True
    
    def sweep(self):
        click_check = False
        for square in self.graph.values():
            if square.number == len([s.loc for s in square.adj if s.flag==True]) and square.number != 0 and square.cover == False:
                for adj_loc in [s.loc for s in square.adj if s.flag==False]:
                    if self.graph[adj_loc].cover == True:
                        self.click(adj_loc[0],adj_loc[1])
                        click_check = True
        return(click_check)

    def adj_overlap(self):
        for square in [s for s in self.graph.values() if s.number > 0 and s.cover == False]:
            rem_mines = square.number - len([s.loc for s in square.adj if s.flag==True])
            square_set = set([s for s in square.adj if s.cover==True and s.flag==False])
            for adj in [s for s in square.adj if s.cover==False and s.number>0]:
                adj_square_set = set([s for s in adj.adj if s.cover==True and s.flag==False])
                adj_rem_mines = adj.number - len([s for s in adj.adj if s.flag==True])
                if adj_rem_mines == rem_mines and adj_square_set.issubset(square_set):
                    for s in square_set - adj_square_set:
                        self.click(s.loc[0], s.loc[1])


    def execute_flagsweep(self):
        click_check = True
        i = 0
        while click_check:
            i+=1
            self.flag()
            if not self.sweep():
                click_check = False
