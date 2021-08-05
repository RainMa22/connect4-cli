import argparse
from abc import ABC, abstractmethod
from math import inf


class Tree:
    def __init__(self, name, move: int=None, data=''):
        self.children = []
        self.data = data
        self.name = name
        self.move = move

    def __str__(self):
        out = ':'.join([self.name, self.data])
        children = []
        for child in self.children:
            children.append(str(child))
        out = ':'.join([out, ':'.join(children)])
        return out


class ColumnFullError(Exception):
    pass


class IllegalMoveError(Exception):
    pass


class Move:
    number = None

    def __init__(self, num):
        self.number = num

    def isLegal(self, legal_moves: str):
        return str(self.number) in legal_moves.split()


class BaseBoard(ABC):
    Board: list
    Side: bool
    Legal_Moves: str
    Result: str
    First: bool
    LatestMove: Move

    @abstractmethod
    def restart(self):
        pass

    @abstractmethod
    def side(self):
        pass

    @abstractmethod
    def update_legal_moves(self, board):
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
        return None

    @abstractmethod
    def debug(self):
        return None


class InternalEngine:
    Values = [0, 1, 2, 3, 2, 1, 0]
    MoveTree = {}

    def generate_moves(self, board: str, ply: int):
        if ply == 0: return Tree(board)
        Bo = Board()
        Bo.setup(board)
        board = Bo
        board.Legal_Moves = board.update_legal_moves()
        boardstr = board.export()
        temp_boards = Tree(boardstr)
        for legal_move in board.Legal_Moves:
            temp = Board()
            temp.setup(boardstr)
            temp.place(int(legal_move))
            temp = temp.export()
            tree = Tree(temp)
            tree.move = legal_move
            tree.children = self.generate_moves(temp, ply - 1).children
            temp_boards.children.append(tree)
        return temp_boards

    def minimax(self, boards: Tree, maximize: bool, ply: int, alpha=-inf, beta=inf):
        if ply == 0:
            eval = self.evaluate(boards)
            boards.data = eval
            return self.evaluate(boards)
        if maximize:
            maxEval = -inf
            for child in boards.children:
                eval = self.minimax(child, False, ply - 1, alpha, beta)
                maxEval = max(maxEval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            boards.data = maxEval
            return maxEval
        else:
            minEval = inf
            for child in boards.children:
                eval = self.minimax(child, True, ply - 1, alpha, beta)
                minEval = min(minEval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            boards.data = minEval
            return minEval

    def evaluate(self, node: Tree):
        board = Board()
        board.setup(node.name)
        board.checkResult()
        value = 0
        if board.Result is not None:
            return inf if board.Result == 'Red Won!' else -inf
        else:
            for row in board.Board:
                for i, column in enumerate(row):
                    if column == '.': continue
                    value += self.Values[i] if column == 'x' else -self.Values[i]
        return value

    def play(self, board: str, maximize: bool, ply=6):
        moves = self.generate_moves(board, ply + 1)
        self.minimax(moves, maximize, ply + 1)
        maxscore = 0
        bestmove = None
        for child in moves.children:
            #child.data = self.minimax(child, not maximize, ply)
            if maxscore < child.data:
                bestmove = child.move
                maxscore = child.data
        return bestmove


class Board(BaseBoard):
    Board = []
    Side = True
    Legal_Moves = '1234567'
    Result = None
    First = True
    LatestMove = None

    def __init__(self, first=True):
        row = ['.', '.', '.', '.', '.', '.', '.']
        self.Board = [row.copy(), row.copy(), row.copy(),
                      row.copy(), row.copy(), row.copy()]
        self.First = first

    def __str__(self):
        board = self.Board
        strings = []
        for column in board:
            strings.append(' '.join(column))
        return '\n'.join(strings)

    def restart(self):
        self.__init__(self.First)
        self.Side = True

    def side(self):
        out = ('x' if self.Side else 'o')
        self.Side = not self.Side
        # print(self.Side)
        return out

    def update_legal_moves(self, board=None):
        if board is None: board = self.Board
        template = ''
        for i in range(7):
            if board[0][i] == '.':
                template += str(i + 1)
        return template

    def checkResult(self):
        if self.Result is not None:
            return
        board = self.Board
        max_x = 6
        max_y = 7
        for i in range(6):
            for j in range(7):
                piece = board[i][j]
                if piece == '.': break
                end1 = i + 3 < max_x
                end3 = j + 3 < max_y
                end2 = end1 and end3
                end4 = j - 3 >= 0 and end1
                for e in range(3):
                    if end1:
                        end1 = (board[i + e + 1][j] == piece)
                    if end2:
                        end2 = (board[i + e + 1][j + e + 1] == piece)
                    if end3:
                        end3 = (board[i][j + e + 1] == piece)
                    if end4:
                        end4 = (board[i + e + 1][j - e - 1] == piece)
                end = end1 or end2 or end3 or end4
                if end:
                    self.Result = 'Red Won!' if piece == 'x' else 'Blue Won!'
                    return

    def place(self, num: int):
        move = Move(num)
        if move.isLegal(self.Legal_Moves):
            raise IllegalMoveError('Illegal Move!')
        num -= 1
        board = self.Board
        side = self.side()
        i = 0
        prev = None
        while i <= 5 and board[i][num] == '.':
            prev = i
            i += 1
        else:
            if prev is None:
                self.side()
                raise ColumnFullError('Column is Full!')
            else:
                board[prev][num] = side
        self.Board = board
        self.LatestMove = move
        self.Legal_Moves = self.update_legal_moves()
        self.checkResult()

    def setup(self, string: str):
        if string.endswith('0') or string.endswith('1'):
            self.Side = True if string.endswith('1') else False
            string = string[:-1]
        rows = string.split('/')
        for i, row in enumerate(rows):
            self.Board[i] = [char for char in row]

    def export(self):
        out = str(self)
        out = out.replace(' ', '')
        out = out.replace('\n', '/')
        out += f'{1 if self.Side else 0}'
        return out

    def debug(self):
        engine = InternalEngine()
        return engine.play(self.export(), self.Side)


if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    arg.add_argument('-t', '--text', help='receive text input and outputs text', type=bool, default=True)
    arg.add_argument('-f', '--first', help='play first', type=bool, default=True)
    args = arg.parse_args()
    board = Board(args.first)
    while board.Result is None and args.text == True:
        cmd = input('connect4-cli >> ')
        cmd = cmd.split(' ')
        tip = '\n'.join(['To place a piece： place column #',
                         'To place restart a game: restart',
                         'To display the Board: d',
                         'To export a board string: export'
                         'To load a setup: setup [board string]',
                         'P.S board string is the board display, except that Enter is replaced with /'
                         ])
        if cmd[0] == 'place':
            try:
                board.place(int(cmd[1]))
            except TypeError:
                print('please use numbers, and numbers only!')
            except ColumnFullError as cfe:
                print(str(cfe))
            except IllegalMoveError as ime:
                print(str(ime))
            except IndexError:
                print('please add a value after "place"')
        elif cmd[0] == 'd':
            print(str(board))
        elif cmd[0] == 'restart':
            board.restart()
            print('restart successful')
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
        elif cmd[0] == 'debug':
            print(board.debug())
        else:
            print(tip)
    print(board.Result)
    print(board)
    input('[Press Enter to Exit program]')
