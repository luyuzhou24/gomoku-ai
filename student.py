from typing import override
from agent import Agent
from gomoku import make_move, is_board_full,check_win

import numpy as np


class Search(Agent):
    def __init__(self, player):
        super().__init__(player)
        # TODO: 在这里添加任何你需要的初始化代码
        self.flag_skill=1
        # self.limit=3
    def make_move(self, board):
        # TODO: 在这里实现你的搜索算法来选择最佳移动
        if self.flag_skill==1: #先判断能否使用技能
            put=self.put_skill(board)
            if put is not None:
                self.flag_skill=0
                return put
        moves=self.get_emptyspot(board)
        moves.sort(key=lambda move: self.quick_sort(board,move),reverse=True)

        if not moves:
            return (len(board)//2,len(board)//2),None
        best_score=-float('inf')
        best_move = moves[0]
        alpha = -float('inf')
        beta = float('inf')
        for move in moves:
            y,x=move
            board[y][x]=self.player
            curr_score=self.minimax(board,alpha=alpha,beta=beta,limit=2,prev_move=(y,x),is_player=False)
            board[y][x]=0
            if curr_score>best_score:
                best_score=curr_score
                best_move=move
            alpha = max(alpha,best_score)
        return best_move,None

    def evaluate(self, board):
        value_table={"011110":100000,
                     "01111*":10000,
                     "*11110":10000,
                     "10111":10000,
                     "11011":10000,
                     "11101":10000,
                     "001110":1000,
                     "011100":1000,
                     "010110":1000,
                     "011010":1000,
                     "*01110*":100,
                     "*01101*":100,
                     "*10110*":100} #几种情况
        situation= self.get_situation(board,self.player)
        player_score = opponent_score = 0
        for line in situation:
            for pattern, value in value_table.items():
                occur=line.count(pattern)
                if occur>0:
                    player_score+=value*occur
        new_situation=self.get_situation(board,self.opponent)
        for line in new_situation:
            for pattern, value in value_table.items():
                occur=line.count(pattern)
                if occur>0:
                    opponent_score+=value*occur
        return player_score-opponent_score*1.2 #给对手加权，便于之后判断时优先考虑处理对手问题，让 AI “宁可不赢，也绝对不能输”

    def minimax(self, board, limit=3, alpha=-float('inf'), beta=float('inf'), is_player=True, prev_move=None):#在depth的限制下递归（？），depth是为了防止搜索到底导致时间成本过大
        if check_win(board, prev_move[0], prev_move[1]): #终止条件
            if is_player: return -100000000
            else:return 100000000
        if limit==0 or is_board_full(board): return self.evaluate(board) #终止条件
        moves=self.get_emptyspot(board)
        if not moves: return self.evaluate(board)

        if is_player:
            best_score=-float('inf')
            for move in moves:
                y,x=move
                board[y][x]=self.player
                curr_score=self.minimax(board,limit-1,alpha,beta,False,(y,x))
                board[y][x]=0
                best_score=max(best_score,curr_score)
                alpha = max(alpha,best_score)
                if beta<=alpha:
                    break
            return best_score
        else:
            worst_score = float('inf')
            for move in moves:
                y, x = move
                board[y][x] = self.opponent
                curr_score = self.minimax(board, limit - 1, alpha, beta, True, (y,x))
                board[y][x] = 0
                worst_score = min(worst_score, curr_score)
                beta = min(beta, worst_score)
                if beta <= alpha:
                    break
            return worst_score


    def get_situation(self, board,user):
        lines=[]
        size=len(board)
        for i in range(size):
            lines.append(board[i,:])
            lines.append(board[:,i])
        for i in range(-size+5,size-4):
            lines.append(board.diagonal(i)) #主对角线
            lines.append(board[:, ::-1].diagonal(i)) #副对角线

        situation = []
        for line in lines: #将棋盘上的数字进行分类处理，改成字符串格式
            line_str="*"
            for num in line:
                if num==0 or num== user+2:line_str+="0" #空位&user的技能点，因为调用的时候可能是player，也可能是opponent
                elif num==(3-user) or num==(3-user)+2 :line_str+="*" #对手&对手的技能点：绝对不能下的地方
                else: line_str+="1"
            line_str+="*"
            situation.append(line_str)
        return situation

    def put_skill(self,board): #判断是否需要使用skill
        for y in range(len(board)):
            for x in range(len(board)):
                if board[y][x]!=0:
                    if self.detect_opponent(x,y,board): return self.detect_opponent(x,y,board) #先判断是否被对方将军，如果是就先处理对手
                    if self.detect_player(x,y,board): return self.detect_player(x,y,board) #否则查看己方能不能用技能将对方的军
        return None #都不需要就不用

    def detect_opponent(self,x, y,board):
        size = len(board)
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)] #找是否存在活四（将军辣！）情况，四个方向找6个格子，和get_situation不同是为了找坐标值
        for d_x, d_y in directions:
            buffers = []
            spot = ""
            for i in range(6):
                nx, ny = x + i * d_x, y + i * d_y
                if 0 <= nx < size and 0 <= ny < size:
                    if board[ny, nx] == self.opponent or board[ny, nx] == self.opponent + 2:
                        spot += '*'
                    elif board[ny, nx] == self.player:
                        spot += '1'
                    elif board[ny, nx] == 0:
                        spot += '0'
                else:
                    spot += '1'
                buffers.append((ny, nx))
            if spot == "0****0":
                return buffers[0], buffers[5]
        return None

    def detect_player(self,x, y,board):
        size = len(board)
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for d_x, d_y in directions:
            buffers = []
            spot = ""
            for i in range(6):
                nx, ny = x + i * d_x, y + i * d_y
                if 0 <= nx < size and 0 <= ny < size:
                    if board[ny, nx] == self.opponent or board[ny, nx] == self.opponent + 2:
                        spot += '*'
                    elif board[ny, nx] == self.player:
                        spot += '1'
                    elif board[ny, nx] == 0:
                        spot += '0'
                else:
                    spot += '*'
                buffers.append((ny, nx))#找己方有没有活三/类似活三的东西，用一下技能就能创造出活四/冲四，绝杀对面
            if spot[:5]=="00111":return buffers[0], buffers[1]
            elif spot[:5]=="10011":return buffers[1], buffers[2]
            elif spot[:5]=="11001":return buffers[2], buffers[3]
            elif spot[:5]=="11100":return buffers[3], buffers[4]
            elif spot[1:]=="00111":return buffers[1], buffers[2]
            elif spot[1:]=="10011":return buffers[2], buffers[3]
            elif spot[1:]=="11001":return buffers[3], buffers[4]
            elif spot[1:]=="11100":return buffers[4], buffers[5]
        return None

    def get_emptyspot(self,board):
        size = len(board)
        spot_list=[]
        directions = [(1, 0),(-1,0),(0,-1), (0, 1),(-1,1),(-1,-1), (1, 1), (1, -1)]
        for x in range(size):
            for y in range(size):
                if board[y][x]!=0:
                    for dx,dy in directions:
                        if 0<= x + dx <size and 0<=y+dy<size and board[y + dy][x + dx]==0:
                            if (y + dy,x + dx) not in spot_list:
                                spot_list.append((y + dy,x + dx))
        return spot_list

    def quick_sort(self,board,move):
        y,x = move
        board[y][x]=self.player
        score=self.evaluate(board)
        board[y][x]=0
        return score