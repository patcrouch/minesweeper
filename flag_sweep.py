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

    def execute_flagsweep(self):
        click_check = True
        i = 0
        while click_check:
            print(f"flagsweep: {i}")
            i+=1
            self.flag()
            if not self.sweep():
                click_check = False
