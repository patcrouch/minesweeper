from mine import Board, Square

class FlagSweep(Board):
    def __init__(self, height, length, mine_num):
        super().__init__(height, length, mine_num)
        self.mine_list = []
        self.uncovered_list = []
        self.flag_check = False
        self.sweep_check = False
        self.overlap_flag_check = False
        self.overlap_sweep_check = False
    
    def uncover(self, y, x):
        self.click(y,x)

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

    def execute_flagsweep(self):
        self.flag()
        self.sweep()

