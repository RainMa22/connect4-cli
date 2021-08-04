import argparse


class Tree:
    def __init__(self, name, data=''):
        self.children = []
        self.data = data
        self.name = name

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


class InternalEngine:
    Values = [0, 1, 2, 1, 0]
    MoveTree = {}

    def generate_moves(self, board, ply: int):
        if ply == 0: return Tree(board)
        Bo = Board()
        Bo.setup(board)
        board = Bo
        board.Legal_Moves = board.update_legal_moves(board.Board)
        boardstr = board.export()
        temp_boards = Tree(boardstr)
        for legal_moves in board.Legal_Moves:
            temp = Board()
            temp.setup(boardstr)
            temp.place(int(legal_moves))
            temp = temp.export()
            tree = Tree(temp)
            tree.children = self.generate_moves(temp, ply - 1).children
            temp_boards.children.append(tree)
        return temp_boards

    # def evaluate(boards:Tree, alpha=0, beta=0, score=0):


class Board:
    Board = []
    Side = True
    Legal_Moves = '1234567'
    Result = None
    First = True
    LatestMove = None

    def __init__(self, first=True):
        column = [None, None, None, None, None, None]
        self.Board = [column.copy(), column.copy(), column.copy(),
                      column.copy(), column.copy(), column.copy(), column.copy()]
        self.First = first

    def __str__(self):
        row = [None, None, None, None, None, None, None]
        strings = [row.copy(), row.copy(), row.copy(), row.copy(), row.copy(), row.copy()]
        board = self.Board
        for i in range(7):
            for j in range(6):
                char = board[i][j]
                if char is None:
                    char = '.'
                strings[5 - j][i] = char
        for i in range(6):
            strings[i] = ' '.join(strings[i])
        return '\n'.join(strings)

    def restart(self):
        self.__init__(self.First)
        self.Side = True

    def side(self):
        out = ('x' if self.Side else 'o')
        self.Side = not self.Side
        # print(self.Side)
        return out

    def update_legal_moves(self, board=Board):
        template = ''
        for i in range(len(board)):
            column = board[i]
            if None in column:
                template += str(i + 1)
        return template

    def checkResult(self):
        if self.Result is not None:
            return
        board = self.Board
        max_x = 7
        max_y = 6
        end = False
        for i in range(7):
            for j in range(6):
                piece = board[i][j]
                if piece is None: break
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
                    self.Result = 'Red Won!' if piece == '0' else 'Blue Won!'
                    return

    def place(self, num: int):
        move = Move(num)
        if move.isLegal(self.Legal_Moves):
            raise IllegalMoveError('Illegal Move!')
        num -= 1
        board = self.Board
        temp = None
        side = self.side()
        for j in range(7):
            if board[num][5 - j] is None and j != 6:
                temp = 5 - j
            else:
                if temp is None:
                    self.side()
                    # flip the side back
                    raise ColumnFullError('Column is Full!')
                else:
                    board[num][temp] = str(side)
        self.Board = board
        self.LatestMove = Move
        self.Legal_Moves = self.update_legal_moves()
        self.checkResult()

    def setup(self, string: str):
        if string.endswith('0') or string.endswith('1'):
            self.Side = True if string.endswith('1') else False
            string = string[:-2]
        rows = string.split('/')
        for i in range(len(rows)):
            rows[i] = [char for char in rows[i]]
            for j in range(len(rows[i])):
                rows[i][j] = None if rows[i][j] == '.' else rows[i][j]
                rows[i][j] = 'x' if rows[i][j] == 'x' else rows[i][j]
                rows[i][j] = 'o' if rows[i][j] == 'o' else rows[i][j]
                self.Board[j][5 - i] = rows[i][j]

    def export(self):
        out = str(self)
        out = out.replace(' ', '')
        out = out.replace('\n', '/')
        out += f'{1 if self.Side else 0}'
        return out

    def debug(self):
        engine = InternalEngine()
        return engine.generate_moves(self.export(), 6)


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
