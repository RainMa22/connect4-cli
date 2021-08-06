import argparse
from abc import ABC, abstractmethod
from math import inf


class ColumnFullError(Exception):
    pass


class IllegalMoveError(Exception):
    pass


class BaseBoard(ABC):
    Board: list
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
    def evaluate(self, group, piece):
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

    def copy(self):
        return self.__copy__()


class Board(BaseBoard):
    array = []
    Side = True
    Legal_Moves = []
    Result = ''
    LatestMove = ''
    Engine = None

    def __init__(self):
        for i in range(6):
            self.array.append([])
            for j in range(7):
                self.array[i].append(0)
                self.Legal_Moves.append(6)

    def __str__(self):
        strings = []
        for i in range(6):
            string = ' '.join(chr(char) for char in self.array[i])
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
        if board is None: board = self.array
        for i, num in enumerate(self.Legal_Moves):
            while self.array[num][i] != 0 and num >= 0:
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

    def checkResult(self):
        score=0
        for i, row in enumerate(self.array):
            for j, column in enumerate(row):
                if j+3 <= 7:
                    score += self.evaluate(row[j:j+4])

    def place(self, num: int):
        pass

    def setup(self, string: str):
        pass

    def export(self):
        pass

    def debug(self):
        pass

    def __copy__(self):
        pass

    def undo(self):
        pass


if __name__ == '__main__':
    arg = argparse.ArgumentParser()
    arg.add_argument('-t', '--text', help='receive text input and outputs text', type=bool, default=True)
    arg.add_argument('-f', '--first', help='human play first', type=bool, default=True)
    arg.add_argument('-p', '--ply', help='the depth of calculation', type=int, default=6)
    args = arg.parse_args()
    board = Board()
    ply = args.ply
    if not args.first: board.play(ply)
    while board.Result is None and args.text:
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
            except IndexError:
                print('please add a value after "place"')
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
