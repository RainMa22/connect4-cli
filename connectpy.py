import argparse
from abc import ABC, abstractmethod
from math import inf


class ColumnFullError(Exception):
    pass


class IllegalMoveError(Exception):
    pass


class BaseBoard(ABC):
    Array: list
    Side: bool
    Legal_Moves: str
    Result: str
    LatestMove: str
    Engine: any

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def side(self):
        pass

    @abstractmethod
    def update_legal_moves(self, board=None):
        pass

    @abstractmethod
    def evaluate(self, group):
        pass

    @abstractmethod
    def checkResult(self):
        pass

    @abstractmethod
    def place(self, num: int):
        pass

    @abstractmethod
    def setup(self, string: str):
        pass

    @abstractmethod
    def export(self):
        pass

    @abstractmethod
    def debug(self):
        pass

    @abstractmethod
    def __copy__(self):
        pass

    @abstractmethod
    def undo(self):
        pass

    @abstractmethod
    def play(self):
        pass

    def copy(self):
        return self.__copy__()


class Engine:

    def Minimax(self, board: BaseBoard, ply: int, maximize, alpha=-inf, beta=inf):
        if ply == 0:
            score = 0
            move = board.LatestMove[-1]
            x = int(move[0])
            y = int(move[1])
            if y + 3 <= 6:
                score += board.evaluate(board.Array[x][y:y + 4])
                if x - 3 >= 0:
                    temp = [board.Array[x][y], board.Array[x - 1][y + 1], board.Array[x - 2][y + 2],
                            board.Array[x - 3][y + 3]]
                    score += board.evaluate(temp)
            if x - 3 >= 0:
                temp = [board.Array[x][y], board.Array[x - 1][y], board.Array[x - 2][y], board.Array[x - 3][y]]
                score += board.evaluate(temp)
                if y - 3 >= 0:
                    temp = [board.Array[x][y], board.Array[x - 1][y - 1], board.Array[x - 2][y - 2],
                            board.Array[x - 3][y - 3]]
                    score += board.evaluate(temp)
            return score
        if maximize:
            maxEval = -inf
            for i, child in enumerate(board.Legal_Moves):
                bo: BaseBoard = board.copy()
                if child[0] != -1:
                    bo.place(i)
                    val = self.Minimax(bo, ply - 1, False, alpha, beta)[0]
                    maxEval = max(maxEval, val)
                    alpha = max(maxEval, val)
                    if beta <= alpha: break
            return maxEval
        else:
            minEval = inf
            for i, child in enumerate(board.Legal_Moves):
                bo: BaseBoard = board.copy()
                if child[0] != -1:
                    bo.place(i)
                    val = self.Minimax(bo, ply - 1, True, alpha, beta)[0]
                    minEval = min(minEval, val)
                    beta = min(minEval, val)
                    if beta <= alpha: break
            return minEval

    def play(self, board, ply, maximize, alpha=- inf, beta=inf):
        if maximize:
            maxEval = -inf
            bob = None
            for i, child in enumerate(board.Legal_Moves):
                bo: BaseBoard = board.copy()
                if child[0] != -1:
                    bo.place(i)
                    val = self.Minimax(bo, ply - 1, False, alpha, beta)[0]
                    if val > maxEval or bob is None:
                        maxEval = val
                        bob = bo.copy()
                    alpha = max(maxEval, val)
                    if beta <= alpha: break
            return maxEval, bob
        else:
            minEval = inf
            bob = None
            for i, child in enumerate(board.Legal_Moves):
                bo: BaseBoard = board.copy()
                if child[0] != -1:
                    bo.place(i)
                    val = self.Minimax(bo, ply - 1, True, alpha, beta)[0]
                    if val < minEval or bob is None:
                        minEval = val
                        bob = bo.copy()
                    beta = min(minEval, val)
                    if beta <= alpha: break
            return minEval, bob


class Board(BaseBoard):
    Array = []
    Side = True
    Legal_Moves = []
    Result = ''
    LatestMove = []
    Engine = Engine()

    def __init__(self):
        super().__init__()
        for i in range(6):
            self.Array.append([])
            for j in range(7):
                self.Array[i].append(0)
        for i in range(7):
            self.Legal_Moves.append(5)

    def __str__(self):
        strings = []
        for i in range(6):
            string = ' '.join(str(char) for char in self.Array[i])
            string = string.replace('0', '.').replace('1', 'x').replace('2', 'o')
            strings.append(string)
        return '\n'.join(strings)

    def restart(self):
        self.__init__()
        self.Side = True

    def side(self):
        self.Side = not self.Side
        return not self.Side

    def update_legal_moves(self, board=None):
        if board is None: board = self.Array
        for i, num in enumerate(self.Legal_Moves):
            while self.Array[num][i] != 0 and num >= 0:
                num -= 1
            else:
                self.Legal_Moves[i] = num

    def evaluate(self, group):
        piece = 1
        other_piece = 2
        score = 0
        if group.count(piece) == 4:
            score += inf
        elif group.count(piece) == 3 and group.count(0) == 1:
            score += 5
        elif group.count(piece) == 2 and group.count(0) == 2:
            score += 2

        if group.count(other_piece) == 4:
            score -= inf
        elif group.count(other_piece) == 3 and group.count(0) == 1:
            score -= 5
        elif group.count(other_piece) == 2 and group.count(0) == 2:
            score -= 2

        return score

    def checkResult(self):
        score = 0
        for i, row in enumerate(self.Array):
            for j, column in enumerate(row):
                if j + 3 <= 6:
                    score += self.evaluate(row[j:j + 4])
                    if i - 3 >= 0:
                        temp = [column, self.Array[i - 1][j + 1], self.Array[i - 2][j + 2], self.Array[i - 3][j + 3]]
                        score += self.evaluate(temp)
                if i - 3 >= 0:
                    temp = [column, self.Array[i - 1][j], self.Array[i - 2][j], self.Array[i - 3][j]]
                    score += self.evaluate(temp)
                    if j - 3 >= 0:
                        temp = [column, self.Array[i - 1][j - 1], self.Array[i - 2][j - 2], self.Array[i - 3][j - 3]]
                        score += self.evaluate(temp)
        if score == inf:
            self.Result = 'Red Won!'
        elif score == -inf:
            self.Result = 'Blue Won!'
        return score

    def place(self, num: int):
        if self.Legal_Moves[num] != -1:
            self.Array[self.Legal_Moves[num]][num] = 1 if self.side() else 2
            self.LatestMove.append((num, self.Legal_Moves[num]))
            self.update_legal_moves()
            self.checkResult()
        else:
            raise ColumnFullError('Column is Full!')

    def setup(self, string: str):
        self.restart()
        for char in string:
            self.place(int(char))
        self.update_legal_moves()
        self.checkResult()

    def export(self):
        return ''.join([str(move[0]) for move in self.LatestMove])

    def debug(self):
        pass

    def __copy__(self):
        copy = Board()
        copy.setup(self.export())
        return copy

    def play(self, ply=6):
        bob: BaseBoard = self.Engine.play(self.copy(), ply, self.Side)[1]
        move = bob.LatestMove[-1]
        self.place(int(move[0]))
        return str(self)

    def undo(self):
        move = self.LatestMove[:-1]
        self.Array[move[0]][move[1]] = '0'
        self.Result = ''
        self.update_legal_moves()
        self.checkResult()


if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    arg.add_argument('-t', '--text', help='receive text input and outputs text', type=bool, default=True)
    arg.add_argument('-f', '--first', help='human play first', type=bool, default=True)
    arg.add_argument('-p', '--ply', help='the depth of calculation', type=int, default=6)
    args = arg.parse_args()
    board = Board()
    ply = args.ply
    if not args.first: board.play(ply)
    while board.Result == '' and args.text:
        cmd = input('connect4-cli >> ')
        cmd = cmd.split(' ')
        tip = '\n'.join(['To place a piece： place column #',
                         'To place restart a game: restart',
                         'To display the Board: d',
                         'To Toggle play against a computer: on',
                         'To set the depth of computer calculation: ply',
                         'To export a board string: export'
                         'To load a setup: setup [board string]',
                         'P.S board string is the board display, except that Enter is replaced with /'
                         ])
        if cmd[0] == 'place':
            try:
                board.place(int(cmd[1]))
                board.checkResult()
                if board.on:
                    board.play(ply)
                    print(board)
            except TypeError:
                print('please use numbers, and numbers only!')
            except ColumnFullError as cfe:
                print(str(cfe))
            except IllegalMoveError as ime:
                print(str(ime))
            #except IndexError:
            #    print('please add a value after "place"')
        elif cmd[0] == 'd':
            print(str(board))
        elif cmd[0] == 'restart':
            board.restart()
            print('restart successful')
        elif cmd[0] == 'on':
            if board.on:
                print('you are no longer playing against a computer!')
            else:
                print('you are now playing against a computer!')
            board.on = not board.on
        elif cmd[0] == 'ply':
            try:
                ply = int(cmd[1])
            except IndexError:
                print('please add a value after "ply"')
        elif cmd[0] == 'setup':
            try:
                if len(cmd) > 1:
                    board.setup(cmd[1])
                else:
                    print('please add a value after "setup"')
            except Exception as e:
                print(str(e))
        elif cmd[0] == 'export':
            print(board.export())
        elif cmd[0] == 'play':
            try:
                if len(cmd) >= 2:
                    print(board.play(int(cmd[1])))
                else:
                    print(board.play(ply))
            except Exception as e:
                print(e)
        elif cmd[0] == 'debug':
            print(board.debug())
        else:
            print(tip)
    print(board.Result)
    print(board)
    input('[Press Enter to Exit program]')
