import tkinter as tk
import tkinter.messagebox as tkm
import numpy as np
from typing import List, Tuple
from random import randint
from operator import eq

bonus= {'connect5': 100_000,
        'live4': 5000,
        'rush4': 1000,
        'live3': 400,
        'sleep3': 100,
        'live2': 10,
        'sleep2': 1}
INF = 1_000_000_000_000

class gobang():
    def __init__(self, N: int, blocksize: int, maxdepth: int):
        self.chessboard = tk.Tk()
        self.chessboard.title('五子棋')
        screenwidth = self.chessboard.winfo_screenwidth()
        screenheight = self.chessboard.winfo_screenheight()
        alignstr = '%dx%d+%d+%d'%((N+1) * blocksize,(N+1) * blocksize,(screenwidth-(N+1)*blocksize)/2,(screenheight-(N+5)*blocksize)/2)
        self.chessboard.geometry(alignstr)
        self.N = N
        self.total_num = 0
        self.blocksize = blocksize
        self.maxdepth = maxdepth
        self.user = False # True：当前落子的是玩家
        self.ai_first = False
        self.waiting = True # 当前实例是否等待用户操作
        self.end = False # 当前游戏是否结束
        self.canvas = tk.Canvas(self.chessboard, bg = "peru", width = (N+1) * blocksize, height = (N+1) * blocksize)
        self.chess = np.zeros((11, 11), dtype=int)
        self.cur_choice_pos_x = 0
        self.cur_choice_pos_y = 0
        self.life2max = [[0,0,1,1,0,0],
                         [0,1,0,1,0],
                         [0,1,0,0,1,0]]
        self.life2min = [[0,0,2,2,0,0],
                         [0,2,0,2,0],
                         [0,2,0,0,2,0]]
        self.sleep2max = [[2,1,1,0,0,0],[0,0,0,1,1,2],
                          [2,1,0,1,0,0],[0,0,1,0,1,2],
                          [2,1,0,0,1,0],[0,1,0,0,1,2],
                          [0,1,0,0,0,1,0]]
        self.sleep2min = [[1,2,2,0,0,0],[0,0,0,2,2,1],
                          [1,2,0,2,0,0],[0,0,2,0,2,1],
                          [1,2,0,0,2,0],[0,2,0,0,2,1],
                          [0,2,0,0,0,2,0]]
        self.live3max = [[0,0,1,1,1,0],[0,1,1,1,0,0],
                         [0,1,1,0,1,0],[0,1,0,1,1,0]]
        self.live3min = [[0,0,2,2,2,0],[0,2,2,2,0,0],
                         [0,2,2,0,2,0],[0,2,0,2,2,0]]
        self.sleep3max = [[2,1,1,1,0,0],[0,0,1,1,1,2],
                          [2,1,1,0,1,0],[0,1,0,1,1,2],
                          [2,1,0,1,1,0],[0,1,1,0,1,2],
                          [0,1,1,0,0,1,0],[0,1,0,0,1,1,0],
                          [0,1,0,1,0,1,0],[2,0,1,1,1,0,2]
                          ]
        self.sleep3min = [[1,2,2,2,0,0],[0,0,2,2,2,1],
                          [1,2,2,0,2,0],[0,2,0,2,2,1],
                          [1,2,0,2,2,0],[0,2,2,0,2,1],
                          [0,2,2,0,0,2,0],[0,2,0,0,2,2,0],
                          [0,2,0,2,0,2,0],[1,0,2,2,2,0,1]]
        self.live4max = [[0,1,1,1,1,0]]
        self.live4min = [[0,2,2,2,2,0]]
        self.rush4max = [[2,1,1,1,1,0],[0,1,1,1,1,2],
                         [0,1,1,1,0,1,0],[0,1,0,1,1,1,0],
                         [0,1,1,0,1,1,0]]
        self.rush4min = [[1,2,2,2,2,0],[0,2,2,2,2,1],
                         [0,2,2,2,0,2,0],[0,2,0,2,2,2,0],
                         [0,2,2,0,2,2,0]]
        self.connect5 = [[1,1,1,1,1,], [2,2,2,2,2]]
        #数字坐标
        for i in range(N):
            x_label = tk.Label(self.canvas, text = str(i), fg = "black", bg = "peru")
            y_label = tk.Label(self.canvas, text = " "+str(i) if i < 10 else str(i), fg = "black", bg = "peru" , justify = 'right')
            x_label.place(x = (i+1) * blocksize-6, y = 2)
            y_label.place(x = 2, y = (i+1) * blocksize-10)
        #线条
        for i in range(1, N+1):
            self.canvas.create_line(blocksize, i*blocksize, N * blocksize, i * blocksize, fill = "black") # 横线
            self.canvas.create_line(i*blocksize, blocksize, i * blocksize, N * blocksize, fill = "black") # 竖线
        #点
        self.chessboard_point_x = [2, 2, 5, 8, 8]
        self.chessboard_point_y = [2, 8, 5, 2, 8]
        for i in range(5):
            self.canvas.create_oval(blocksize * (1+self.chessboard_point_x[i]) - (self.blocksize//10), blocksize * (1+self.chessboard_point_y[i]) - (self.blocksize//10), 
                                    blocksize * (1+self.chessboard_point_x[i]) + (self.blocksize//10), blocksize * (1+self.chessboard_point_y[i]) + (self.blocksize//10),
                                    fill = "black")
        # 选中一格时的边框
        self.left_frame = self.canvas.create_line(0,0,0,0, fill="white", dash = (4,4))
        self.up_frame = self.canvas.create_line(0,0,0,0, fill="white", dash = (4,4))
        self.right_frame = self.canvas.create_line(0,0,0,0, fill="white", dash = (4,4))
        self.down_frame = self.canvas.create_line(0,0,0,0, fill="white", dash = (4,4))
        self.canvas.pack()
        self.initialize()
        self.ai_first = tkm.askokcancel('先手', 'AI先手？')
        if self.ai_first == True:
            my_x, my_y = self.ai_do(5,5,'black')
            score = self.evaluate()
            print(score)
        self.canvas.bind("<Button-1>", self.hit) #绑定点击鼠标左键为空操作
        self.canvas.bind("<Motion>", self.move) #绑定鼠标移动为空操作
#============================  GUI  ============================#
    # 设置初始状态
    def initialize(self):
        pass
        # 设置初始状态
        # self.chess[5][5] = 1 # 这里x是行，y是列
        # self.chess[5][6] = 1
        # self.chess[5][4] = 2
        # self.chess[6][5] = 2
        # self.draw_chess(5,5,'black') # 这里x是列，y是行
        # self.draw_chess(6,5,'black')
        # self.draw_chess(4,5,'white')
        # self.draw_chess(5,6,'white')
        # self.total_num = 4
    # 从画布坐标中得到网格坐标
    def get_grid_pos(self, x: int, y: int):
        pos_x = 0
        pos_y = 0
        lower_x = x // self.blocksize
        lower_y = y // self.blocksize
        if x - (lower_x * self.blocksize) <= (self.blocksize // 2):
            pos_x = lower_x
        else:
            pos_x = lower_x + 1
        if y - (lower_y * self.blocksize) <= (self.blocksize // 2):
            pos_y = lower_y
        else:
            pos_y = lower_y + 1
        return pos_x, pos_y
    # 重置选中框
    def reset_frame(self):
        self.canvas.coords(self.left_frame, 0,0,0,0)
        self.canvas.coords(self.up_frame, 0,0,0,0)
        self.canvas.coords(self.right_frame, 0,0,0,0)
        self.canvas.coords(self.down_frame, 0,0,0,0)
    # 展示选中框
    def show_choice(self, x: int, y: int):
        pos_x, pos_y = self.get_grid_pos(x, y)
        if pos_x != self.cur_choice_pos_x or pos_y != self.cur_choice_pos_y: # 有变动才触发更新
            self.cur_choice_pos_x = pos_x
            self.cur_choice_pos_y = pos_y
            if self.cur_choice_pos_x in range(1, self.N+1) and self.cur_choice_pos_y in range(1, self.N+1):
                self.canvas.coords(self.left_frame, 
                                   self.blocksize * self.cur_choice_pos_x - (self.blocksize // 3), self.blocksize * self.cur_choice_pos_y - (self.blocksize // 3),
                                   self.blocksize * self.cur_choice_pos_x - (self.blocksize // 3), self.blocksize * self.cur_choice_pos_y + (self.blocksize // 3))
                self.canvas.coords(self.up_frame, 
                                   self.blocksize * self.cur_choice_pos_x - (self.blocksize // 3), self.blocksize * self.cur_choice_pos_y - (self.blocksize // 3),
                                   self.blocksize * self.cur_choice_pos_x + (self.blocksize // 3), self.blocksize * self.cur_choice_pos_y - (self.blocksize // 3))
                self.canvas.coords(self.right_frame, 
                                   self.blocksize * self.cur_choice_pos_x + (self.blocksize // 3), self.blocksize * self.cur_choice_pos_y - (self.blocksize // 3),
                                   self.blocksize * self.cur_choice_pos_x + (self.blocksize // 3), self.blocksize * self.cur_choice_pos_y + (self.blocksize // 3))
                self.canvas.coords(self.down_frame, 
                                   self.blocksize * self.cur_choice_pos_x - (self.blocksize // 3), self.blocksize * self.cur_choice_pos_y + (self.blocksize // 3),
                                   self.blocksize * self.cur_choice_pos_x + (self.blocksize // 3), self.blocksize * self.cur_choice_pos_y + (self.blocksize // 3))
            else:
                self.reset_frame()
    # 检测鼠标点击画布，调用落子
    def hit(self, event):
        x, y = self.get_grid_pos(event.x, event.y)
        x -= 1 # 更改坐标为棋盘坐标，此时x是横轴，y是纵轴
        y -= 1
        if self.end == True:
            pass
        else:
            self.waiting = True
            self.drop(x, y)
    # 当选择时，鼠标移动
    def move(self, event):
        self.show_choice(event.x, event.y)
    # 画棋子
    def draw_chess(self, x: int, y: int, color: str):
        self.canvas.create_oval(self.blocksize * (1+x) - (self.blocksize//3), self.blocksize * (1+y) - (self.blocksize//3), 
                                self.blocksize * (1+x) + (self.blocksize//3), self.blocksize * (1+y) + (self.blocksize//3),
                                fill = color, outline = color, tag = "piece")
    # ai落子
    def ai_do(self, x, y, color):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Motion>")
        my_x = 0
        my_y = 0
        if self.total_num == 0:
            my_x = x
            my_y = y
        else:
            my_x, my_y = self.ai(x, y)
        self.draw_chess(my_x, my_y, color)
        self.chess[my_y][my_x] = 1 if color == 'black' else 2
        self.total_num += 1
        self.canvas.bind("<Button-1>", self.hit)
        self.canvas.bind("<Motion>", self.move)
        state = self.check(my_x, my_y)
        if state == True:
            self.finish()
        return my_x, my_y
    # 落子
    def drop(self, x: int, y: int):
        if self.ai_first == True: # ai先手，黑棋
            if self.chess[y][x] == 0:
                self.user = True
                self.draw_chess(x, y, 'white')
                self.chess[y][x] = 2
                self.total_num += 1
                self.canvas.update()
                state = self.check(x, y)
                if state == True:
                    self.finish()
                self.waiting = False # 结束等待状态
            # ai行动
            if self.waiting == False and self.end == False: # 当玩家成功下子之后，ai才行动
                self.user = False
                self.ai_do(x, y, 'black')
                score = self.evaluate()
                print(score)
        else: # ai后手，白棋
            if self.chess[y][x] == 0:
                self.user = True
                self.draw_chess(x, y, 'black')
                self.chess[y][x] = 1
                self.total_num += 1
                self.canvas.update()
                state = self.check(x, y)
                if state == True:
                    self.finish()
                self.waiting = False
            if self.waiting == False and self.end == False:
                self.user = False
                self.ai_do(x, y, 'white')
                score = self.evaluate()
                print(score)
    # 检查当前落的这个棋子能不能构成5连
    def check(self, x: int, y: int) -> bool:
        ans = False
        ans = ans or self.row_check(x, y)
        ans = ans or self.col_check(x, y)
        ans = ans or self.dia_check(x, y)
        return ans            
    def in_scope(self, num: int) -> bool:
        if num >= 0 and num <= 10:
            return True
        else:
            return False
    # 计数当前棋子在d方向连续的相同棋子数，d=0：行，d=1：列，d=2：左上右下，d=3右上左下
    def count(self, x, y, d: int) -> int:
        num = 1
        if d == 0:
            test_x = x-1 # 左
            while self.in_scope(test_x) and self.chess[y][test_x] ==  self.chess[y][x]:
                num += 1
                test_x -= 1
            test_x = x+1 # 右
            while self.in_scope(test_x) and self.chess[y][test_x] ==  self.chess[y][x]:
                num += 1
                test_x += 1
            return num
        elif d == 1:
            test_y = y-1 # 上
            while self.in_scope(test_y) and self.chess[test_y][x] ==  self.chess[y][x]:
                num += 1
                test_y -= 1
            test_y = y+1 # 下
            while self.in_scope(test_y) and self.chess[test_y][x] ==  self.chess[y][x]:
                num += 1
                test_y += 1
            return num
        elif d == 2:
            test_x = x-1 # 左上
            test_y = y-1
            while self.in_scope(test_x) and self.in_scope(test_y) and self.chess[test_y][test_x] == self.chess[y][x]:
                num += 1
                test_x -= 1
                test_y -= 1
            test_x = x+1 # 右下
            test_y = y+1
            while self.in_scope(test_x) and self.in_scope(test_y) and self.chess[test_y][test_x] == self.chess[y][x]:
                num += 1
                test_x += 1
                test_y += 1
            return num
        elif d == 3:
            test_x = x+1 # 右上
            test_y = y-1
            while self.in_scope(test_x) and self.in_scope(test_y) and self.chess[test_y][test_x] == self.chess[y][x]:
                num += 1
                test_x += 1
                test_y -= 1
            test_x = x-1 # 左下
            test_y = y+1
            while self.in_scope(test_x) and self.in_scope(test_y) and self.chess[test_y][test_x] == self.chess[y][x]:
                num += 1
                test_x -= 1
                test_y += 1
            return num
    # 检查行/列/对角线，当有5连的时候返回True
    def row_check(self, x, y) -> bool:
        num = self.count(x, y, 0)
        return True if num >= 5 else False
    def col_check(self, x, y) -> bool:
        num = self.count(x, y, 1)
        return True if num >= 5 else False
    def dia_check(self, x, y) -> bool:                
        num = self.count(x, y, 2)
        if num >= 5:
            return True
        num = self.count(x, y, 3)
        return True if num >= 5 else False
    # 结束游戏
    def finish(self):
        self.end = True
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Motion>")
        self.reset_frame()
        tkm.showinfo('Game over', '{:s} win.'.format('AI' if self.user == False else 'User'))
#============================  AI  ============================#
    # ai选取一个点的坐标
    def ai(self, x, y) -> Tuple[int, int]:
        val, my_x, my_y= self.minmax(x, y, self.maxdepth, -INF, INF, self.ai_first)
        print('AI drop in [{:2d}, {:2d}] score: '.format(my_x, my_y), end="")
        self.canvas.update()
        return my_x, my_y    
    # minmax搜索，带剪枝
    def minmax(self, x, y, depth: int, a, b, max_player: bool): # player=0：max，player=1：min
        if depth == 0:
            return self.evaluate(), x, y
        if max_player == True: # max玩家
            maxval = -INF
            best_x = 0
            best_y = 0
            for point in self.get_searsh_list(x, y): # 遍历能够落子的位置列表（遍历子状态）
                next_x = point[1][0]
                next_y = point[1][1]
                self.chess[next_y][next_x] = 1 if max_player == True else 2 # 把尝试走的这一步写在地图上
                val,_,_ = self.minmax(next_x, next_y, depth-1, a, b, False)
                self.chess[next_y][next_x] = 0 # 把操作还原
                if val > maxval:
                    best_x = next_x
                    best_y = next_y
                maxval = max(val, maxval)
                a = max(val, a)
                if b <= a:
                    break
            return maxval, best_x, best_y
        else: # min玩家
            minval = +INF
            best_x = 5
            best_y = 5
            for point in self.get_searsh_list(x, y): # 遍历能够落子的位置列表（遍历子状态）
                next_x = point[1][0]
                next_y = point[1][1]
                self.chess[next_y][next_x] = 1 if max_player == True else 2 # 把尝试走的这一步写在地图上
                val,_,_ = self.minmax(next_x, next_y, depth-1, a, b, True)
                self.chess[next_y][next_x] = 0 # 把操作还原
                if val < minval:
                    best_x = next_x
                    best_y = next_y
                minval = min(val, minval)
                b = min(val, b)
                if b <= a:
                    break
            return minval, best_x, best_y
    # 形成从当前坐标开始，距离与之从小到大排列的可下的点
    def get_searsh_list(self, x, y) -> List:
        check_list = []
        for next_x in range(self.N):
            for next_y in range(self.N):
                if self.chess[next_y][next_x] == 0: # 允许落子的位置
                    d = abs(next_x - x) + abs(next_y - y)
                    check_list.append([d, [next_x, next_y]])
        return sorted(check_list) # 通过d(曼哈顿距离)来排序
    
    # 评价棋盘上的每一个点的得分
    def evaluate(self):
        total = 0
        for x in range(self.N):
            for y in range(self.N):
                if self.chess[y][x] != 0: # 没有棋子的格子可以不看
                    dir_offset=[1, 0] # 横线
                    line = self.getline(x, y, dir_offset)
                    total += self.analysisline(line)
                    dir_offset=[0, 1] #竖线
                    line = self.getline(x, y, dir_offset)
                    total += self.analysisline(line)
                    dir_offset=[1, 1] # 左上右下线
                    line = self.getline(x, y, dir_offset)
                    total += self.analysisline(line)
                    dir_offset=[1, -1] # 右上左下线
                    line = self.getline(x, y, dir_offset)
                    total += self.analysisline(line)
        return total
    
    # 返回x,y确定的棋子为中心的线，drt_offset确定移动方式（两个数，表示右/下方向），opponent是对方的代号
    def getline(self, x, y, dir_offset) -> List[int]:
        line = [0 for i in range(9)]
        temp_x = x + (-5 * dir_offset[0])
        temp_y = y + (-5 * dir_offset[1])
        for i in range(9):
            temp_x += dir_offset[0]
            temp_y += dir_offset[1]
            if self.in_scope(temp_x) and self.in_scope(temp_y):
                line[i] = self.chess[temp_y][temp_x]
            else:
                line[i] = -1
        return line
    
    # 评估这条线上的得分
    def analysisline(self, line) -> int:
        total = 0
        total += self.judge_length5(line)
        total += self.judge_length6(line)
        total += self.judge_length7(line)
        # total += self.judge2(line)
        # total += self.judge3(line)
        # total += self.judge4(line)
        # total += self.judge5(line)
        return total
    
    # 判断2连子的情况
    def judge2(self, line) -> int:
        total = 0
        # 判断活2
        '''
        self.life2max = [[0,0,1,1,0,0],
                         [0,1,0,1,0],
                         [0,1,0,0,1,0]]
        self.life2min = [[0,0,2,2,0,0],
                         [0,2,0,2,0],
                         [0,2,0,0,2,0]]
        '''
        for i in range(4):
            window = line[i:i+6]
            for sample in self.life2max:
                if eq(window, sample):
                    total += bonus['live2']
            for sample in self.life2min:
                if eq(window, sample):
                    total -= bonus['live2']
        for i in range(5):
            window = line[i:i+5]
            if eq(window, self.life2max[1]):
                total += bonus['live2']
            if eq(window, self.life2min[1]):
                total -= bonus['live2']
        # 判断眠2
        '''
        self.sleep2max = [[2,1,1,0,0,0],[0,0,0,1,1,2],
                          [2,1,0,1,0,0],[0,0,1,0,1,2],
                          [2,1,0,0,1,0],[0,1,0,0,1,2],
                          [0,1,0,0,0,1,0]]
        self.sleep2min = [[1,2,2,0,0,0],[0,0,0,2,2,1],
                          [1,2,0,2,0,0],[0,0,2,0,2,1],
                          [1,2,0,0,2,0],[0,2,0,0,2,1],
                          [0,2,0,0,0,2,0]]
        '''
        for i in range(4):
            window = line[i:i+6]
            for sample in self.sleep2max:
                if eq(window, sample):
                    total += bonus['sleep2']
            for sample in self.sleep2min:
                if eq(window, sample):
                    total -= bonus['sleep2']
        for i in range(3):
            window = line[i:i+7]
            if eq(window, self.sleep2max[1]):
                total += bonus['sleep2']
            if eq(window, self.sleep2min[1]):
                total -= bonus['sleep2']
        return total
    # 判断3连子的情况
    def judge3(self, line) -> int:
        total = 0
        # 活3
        '''
        self.live3max = [[0,0,1,1,1,0],[0,1,1,1,0,0],
                         [0,1,1,0,1,0],[0,1,0,1,1,0]]
        self.live3min = [[0,0,2,2,2,0],[0,2,2,2,0,0],
                         [0,2,2,0,2,0],[0,2,0,2,2,0]]
        '''
        for i in range(4):
            window = line[i:i+6]
            for sample in self.live3max:
                if eq(window, sample):
                    total += bonus['live3']
            for sample in self.live3min:
                if eq(window, sample):
                    total -= bonus['live3']
        # 眠3
        '''
        self.sleep3max = [[2,1,1,1,0,0],[0,0,1,1,1,2],
                          [2,1,1,0,1,0],[0,1,0,1,1,2],
                          [2,1,0,1,1,0],[0,1,1,0,1,2],
                          [0,1,1,0,0,1,0],[0,1,0,0,1,1,0],
                          [0,1,0,1,0,1,0],[2,0,1,1,1,0,2]
                          ]
        self.sleep3min = [[1,2,2,2,0,0],[0,0,2,2,2,1],
                          [1,2,2,0,2,0],[0,2,0,2,2,1],
                          [1,2,0,2,2,0],[0,2,2,0,2,1],
                          [0,2,2,0,0,2,0],[0,2,0,0,2,2,0],
                          [0,2,0,2,0,2,0],[1,0,2,2,2,0,1]]
        '''
        for i in range(4):
            window = line[i:i+6]
            for sample in self.sleep3max[0:6]:
                if eq(window, sample):
                    total += bonus['sleep3']
            for sample in self.sleep3min[0:6]:
                if eq(window, sample):
                    total -= bonus['sleep3']
        for i in range(3):
            window = line[i:i+7]
            for sample in self.sleep3max[6:10]:
                if eq(window, sample):
                    total += bonus['sleep3']
            for sample in self.sleep3min[6:10]:
                if eq(window, sample):
                    total -= bonus['sleep3']
        return total
    # 判断4连子的情况
    def judge4(self, line) -> int:
        total = 0
        # 活4
        '''
        self.live4max = [[0,1,1,1,1,0]]
        self.live4min = [[0,2,2,2,2,0]]
        '''
        for i in range(4):
            window = line[i:i+6]
            for sample in self.live4max:
                if eq(window, sample):
                    total += bonus['live4']
            for sample in self.live4min:
                if eq(window, sample):
                    total -= bonus['live4']
        # 冲4
        '''
        self.rush4max = [[2,1,1,1,1,0],[0,1,1,1,1,2],
                         [0,1,1,1,0,1,0],[0,1,0,1,1,1,0],
                         [0,1,1,0,1,1,0]]
        self.rush4min = [[1,2,2,2,2,0],[0,2,2,2,2,1],
                         [0,2,2,2,0,2,0],[0,2,0,2,2,2,0],
                         [0,2,2,0,2,2,0]]
        '''
        for i in range(4):
            window = line[i:i+6]
            for sample in self.rush4max[0:2]:
                if eq(window, sample):
                    total += bonus['rush4']
            for sample in self.rush4min[0:2]:
                if eq(window, sample):
                    total -= bonus['rush4']
        for i in range(3):
            window = line[i:i+7]
            for sample in self.sleep3max[2:5]:
                if eq(window, sample):
                    total += bonus['rush4']
            for sample in self.sleep3min[2:5]:
                if eq(window, sample):
                    total -= bonus['rush4']
        return total
    # 判断连5，无方向
    def judge5(self, line) -> int:
        total = 0
        for i in range(5): 
            window = line[i:i+5] # 取出5个
            if eq(window, self.connect5[0]):
                total += bonus['connect5']
            if eq(window, self.connect5[1]):
                total -= bonus['connect5']
        return total

    # 判断长度为5的
    def judge_length5(self, line):
        total = 0
        for i in range(5):
            window = line[i:i+5]
            if eq(window, self.life2max[1]):
                total += bonus['live2']
            if eq(window, self.life2min[1]):
                total -= bonus['live2']
            if eq(window, self.connect5[0]):
                total += bonus['connect5']
            if eq(window, self.connect5[1]):
                total -= bonus['connect5']
        return total
    # 判断长度为6的
    def judge_length6(self, line):
        total = 0
        for i in range(4):
            window = line[i:i+6]
            for sample in self.life2max:
                if eq(window, sample):
                    total += bonus['live2']
            for sample in self.life2min:
                if eq(window, sample):
                    total -= bonus['live2']
            for sample in self.sleep2max:
                if eq(window, sample):
                    total += bonus['sleep2']
            for sample in self.sleep2min:
                if eq(window, sample):
                    total -= bonus['sleep2']
            for sample in self.live3max:
                if eq(window, sample):
                    total += bonus['live3']
            for sample in self.live3min:
                if eq(window, sample):
                    total -= bonus['live3']
            for sample in self.sleep3max[0:6]:
                if eq(window, sample):
                    total += bonus['sleep3']
            for sample in self.sleep3min[0:6]:
                if eq(window, sample):
                    total -= bonus['sleep3']
            for sample in self.live4max:
                if eq(window, sample):
                    total += bonus['live4']
            for sample in self.live4min:
                if eq(window, sample):
                    total -= bonus['live4']
            for sample in self.rush4max[0:2]:
                if eq(window, sample):
                    total += bonus['rush4']
            for sample in self.rush4min[0:2]:
                if eq(window, sample):
                    total -= bonus['rush4']
        return total
    # 判断长度为7的
    def judge_length7(self, line):
        total = 0
        for i in range(3):
            window = line[i:i+7]
            if eq(window, self.sleep2max[1]):
                total += bonus['sleep2']
            if eq(window, self.sleep2min[1]):
                total -= bonus['sleep2']
            for sample in self.sleep3max[6:10]:
                if eq(window, sample):
                    total += bonus['sleep3']
            for sample in self.sleep3min[6:10]:
                if eq(window, sample):
                    total -= bonus['sleep3']
            for sample in self.sleep3max[2:5]:
                if eq(window, sample):
                    total += bonus['rush4']
            for sample in self.sleep3min[2:5]:
                if eq(window, sample):
                    total -= bonus['rush4']
        return total

def main():
    game = gobang(11, 50, 2)
    game.chessboard.mainloop()

if __name__ == '__main__':
    main()