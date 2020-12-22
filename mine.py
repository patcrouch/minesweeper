import random
import copy

#Square class allows for easier access to check properties of a certain cell
#Each square has a number, location, and boolean value for having a mine, being hidden, or being flagged
#Each square also has a set of adjacent square, and subsets with helpful attributes
class Square:
    def __init__(self, y, x, adj=[], number=0, mine=False, cover=True, flag=False):
        self.loc = (y,x)
        self.number = number #-1: mine, 0: empty, >0: adjacent mines
        self.mine = mine
        self.cover = cover
        self.flag = flag
        self.adj = set()
        self.sphere = set()
        self.adj_flags = set()
        self.adj_covered = set()
        self.adj_numbers = set()

#Board class is the main class used in the game
class Board:
    def __init__(self, height, width, mine_num):
        self.height = height
        self.width = width
        self.mine_num = mine_num
        self.graph = {}     #graph is used to store all squares in the game
        self.game_status = 0    #0: game in progress, 1: game lost, 2: game won
        self.mine_set = set()
        self.num_covered = height*width     #used to check win condition
        self.flag_check = False     #check values are used to help the step function in the GUI
        self.sweep_check = False
        self.overlap_flag_check = False
        self.overlap_sweep_check = False
        self.click_set = set()      # used in click functions to reduce lag
    
    #initiates graph
    def set_graph(self, y_click, x_click):

        #populates graphs with squares and sets the correct adjacent sets
        squares = set([(y,x) for y in range(self.height) for x in range(self.width)])
        self.graph = {(loc[0],loc[1]):Square(loc[0],loc[1]) for loc in squares}
        for loc in self.graph:
            adj_set = set()
            for dis in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                if loc[0]+dis[0] in range(self.height) and loc[1]+dis[1] in range(self.width):
                    adj_set.add((loc[0]+dis[0],loc[1]+dis[1]))
                    self.graph[loc].adj = adj_set
                    self.graph[loc].adj_covered = adj_set.copy()    #adj_covered is initialized to contain all adj squares
            sphere_set = set()
            for dis in [(-2,-1),(-2,0),(-2,1),(-1,-2),(-1,2),(0,-2),(0,2),(1,-2),(1,2),(2,-1),(2,0),(2,1)]:
                if loc[0]+dis[0] in range(self.height) and loc[1]+dis[1] in range(self.width):
                    sphere_set.add((loc[0]+dis[0],loc[1]+dis[1]))
                    self.graph[loc].sphere = adj_set.copy().union(sphere_set)

        #assures first click is an empty space
        start_click_condition = set([(y_click,x_click)])
        for adj_loc in self.graph[(y_click,x_click)].adj:
            start_click_condition.add(adj_loc)
        mine_locs = squares
        for pos in start_click_condition:
            mine_locs.discard(pos)
        self.mine_set = random.sample(mine_locs, self.mine_num)
        for mine in self.mine_set:
            self.graph[mine].mine = True
            self.graph[mine].number = -1
        for square in self.graph.values():
            if not square.mine:
                square.number = len([s for s in square.adj if self.graph[s].mine==True])

        #clicks first square and returns all squares that were clicked, to be used in GUI
        self.click((y_click,x_click))
        return self.reset_click_set()

    #click function uncovers a clicked square
    #acts recursively if an empty square is clicked to uncover all adjacent empty squares, mimicking the game
    def click(self, loc):
        if self.graph[loc].cover:
            #if clicked square is a mine, game status is changed to loss and the rest of the funciton is irrelevant
            if self.graph[loc].number == -1:
                self.graph[loc].cover = False
                self.game_status = 1
            #if square is empty, it is uncovered and all adjacent squares are clicked recursively
            elif self.graph[loc].number == 0:
                self.graph[loc].cover = False
                self.click_set.add(loc)
                self.num_covered -= 1       #num_covered is reduced with each click
                for adj_loc in self.graph[loc].adj:
                    self.graph[adj_loc].adj_covered.discard(loc)    #square is removed from adj_covered sets of adjacent squares
                    self.click(adj_loc)
                return
            #if the square is a number, it is simply uncovered and recursion is halted
            else:
                square = self.graph[loc]
                square.cover = False
                self.click_set.add(loc)
                self.num_covered -= 1
                #adj sets are updated for each adjacent square
                for adj_loc in square.sphere:
                    adj_square = self.graph[adj_loc]
                    if adj_loc in square.adj:
                        adj_square.adj_covered.discard(loc)
                    adj_square.adj_numbers.add(loc)
                return
        else:
            return

    #utility function to aid in GUI implementation
    def reset_click_set(self):
        cs = self.click_set.copy()
        self.click_set = set()
        return cs
    
    #flag function is used to flag squares known to be mines
    #it works by checking to see if the number of a square is equal to the number of adjacent covered squares
    #if so, the adjacent squares are flagged
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
                            self.flag_check = True  #check variables tell mine_page if the function actually changed the board
                            flagged.add(adj_loc)    #flagged set is used to update flagged squares in GUI
        return flagged

    #sweep function is used to click squares known to not contain mines
    #it works by checking to see id the number of adjacent flags is equal to its number
    #if so, all other non-flagged adjacent squares are clicked
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

    #similar to flag, overlap_flag identifies mines through overlapping sets
    #if the interescton of the adj_sets of two adjacent numbers has to many squares for one of them,
    #flags are placed in the spots that we know contain mines by process of elimination
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

    #using similar logic as overlap_flag, overlap_sweep clicks squares we know to not have mines by process of elimination
    #if one adj_set is a subset of another and the numbers are equal, we know the set difference does not contain mines
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
    
    #simple function to click a random square if other algorithm functions cannot be performed
    def random_click(self):
        covered = [s for s in self.graph if self.graph[s].cover and not self.graph[s].flag]
        loc = random.choice(covered)
        self.click(loc)
        return loc, self.reset_click_set()  #returns clicked square so that it can be marked in GUI

    #utility function to set adj_flag sets without redundancy
    def set_flag(self, loc):
        square = self.graph[loc]
        square.flag = True
        for adj_loc in square.adj:
            adj_square = self.graph[adj_loc]
            adj_square.adj_flags.add(loc)

    #checks to see if all non-mine squares are clicked, game_status changed accordingly
    def check_win(self):
        if self.num_covered == self.mine_num:
            self.game_status = 2