#! /usr/bin/python


import curses, random, time

from player import Player, Move, Conflict


DEFAULT_SIZE = 15
DELAY = 0.1


def main():
    try:
        game = Game('MICHAEL', 'CURTIS')
        game.play()

    finally:
        curses.endwin()


class Game:
    def __init__(self, player_1=None, player_2=None, size=DEFAULT_SIZE):
        # Initialize player objects.
        self.player_1 = Player(player_1)
        self.player_2 = Player(player_2)

        # What if the board size is smaller than someone's name?
        max_length = max([len(self.player_1.name), len(self.player_2.name)])
        if size < max_length: size = max_length

        # Initialize the board.
        self.board = Board(size)
        self.player_1.colour = curses.color_pair(1)
        self.player_2.colour = curses.color_pair(2)

        # Initial placement of names.
        self.board.place(word=self.player_1.name, player=self.player_1,
                         x=0, y=0, attributes=curses.A_BOLD)
        self.board.place(word=self.player_2.name, player=self.player_2, 
                         x=size-1, y=size-1, direction='l',
                         attributes=curses.A_BOLD)


    def play(self):
        curses.curs_set(False)
        self.board.window.clear()
        self.board.display()
        time.sleep(DELAY)

        while self.player_1.spaces and self.player_2.spaces:
            # Player one claims a space.
            move = self.player_1.next_move()
            move.space.claim(move)

            # Player two claims a space.
            move = self.player_2.next_move()
            move.space.claim(move)

            # Resolve what happens and display it.
            self.board.resolve()
            self.board.display()

            # Pause for humans.
            time.sleep(DELAY)


class Board:
    def __init__(self, size):
        self.width = size
        self.height = size

        # Initialize the screen for display purposes.
        self.screen = curses.initscr()
        self.window = curses.newwin(size, size * 2, 1, 1)

        # Can't get curses' border() or box() functions to work...
        # self.window.box()
        self.draw_border()

        # Initialize the spaces on the board.
        self.spaces = [Space(x, y, self)
                       for x in range(size) for y in range(size)]

        # Initialize the "conflict zones" (where spaces will turn over).
        self.conflicts = []

        # Initialize player colours.
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)


    def draw_border(self):
        w, h = self.window.getmaxyx()

        try:
            self.window.addch(0, 0, curses.ACS_ULCORNER)
            self.window.addch(0, w, curses.ACS_URCORNER)
            self.window.addch(h, 0, curses.ACS_LLCORNER)
            self.window.addch(h, w, curses.ACS_LRCORNER)

        except curses.error:
            pass


    def display(self):
        # Display conflicts.
        # CONFLICTS GO HERE
        # AFTER DISPLAY, REMOVE FROM CONFLICTS LIST.

        # Display new board state.
        for s in self.spaces:
            s.display()

        self.screen.refresh()
        self.window.refresh()


    def resolve(self):
        # SHOULD PROBABLY KEEP TRACK OF PENDING MOVES.
        for s in self.spaces:
            if s.claims: s.resolve()


    def place(self, word, player, x, y, direction='r', attributes=0):
        for l in word:
            space = next(s for s in self.spaces if s.x == x and s.y == y)
            space.claim(Move(space, player, l, player.colour | attributes))
            space.resolve()

            if direction == 'r': x += 1
            elif direction == 'l': x -= 1
            elif direction == 'd': y += 1
            elif direction == 'u': y -= 1
            else: raise Exception('Invalid direction specified.')


class Space:
    def __init__(self, x, y, board, player=None, letter=None, attributes=0):
        self.x = x
        self.y = y
        self.board = board
        self.player = player
        self.letter = letter
        self.attributes = attributes
        self.claims = []


    def display(self):
        if self.letter:
            try:
                self.board.window.addstr(self.y, self.x * 2, self.letter,
                                         self.attributes)
            except curses.error:
                pass


    def claim(self, move):
        self.claims.append(move)


    def resolve(self):
        """
        Each letter has a very high chance of beating the letters in the
        alphabet that immediately follow it, which slowly decreases to 50/50 as
        we approach letters halfway across the alphabet, until the probability
        that "A" will defeat "N" is only 50/50. After thirteen letters away,
        the probability of a loss increases, until we reach the letter directly
        before our chosen letter, which has a very high chance of defeating us!

        The chance of letter A winning against letter B may be calculated thus:
            probability = ((ord(A) - ord(B)) % 26) / 26

        In the case of a probability of zero (both letters are the same), we
        assign a probability of 0.5.
        """

        if self.claims:
            # Add this space as a "conflict zone" for display purposes.
            self.board.conflicts.append(Conflict(self))

        while self.claims:
            move = self.claims.pop()

            if self.letter:
                chance = ((ord(move.letter) - ord(self.letter)) % 26) / 26.0
                if not chance: chance = 0.5
            else:
                chance = 1.0

            if random.random() < chance:
                # The challenger is victorious!
                if self.player:
                    self.player.spaces.remove(self)

                self.letter = move.letter
                self.player = move.player
                self.attributes = move.attributes

                self.player.spaces.append(self)

                # if chance == 0.1:
                #     ADD TEXT TO READOUT INDICATING A MOVE.
                # if chance < 0.1:
                #     ADD TEXT INDICATING A NARROW VICTORY.
                # else
                #     ADD TEXT TO READOUT INDICATING A TAKEOVER.


    def possible_moves(self):
        spaces = [s for s in self.board.spaces if s.player != self.player and
                  (abs(s.x - self.x) + abs(s.y - self.y) == 1)]

        return [Move(s, self.player, self.letter) for s in spaces]


if __name__ == "__main__":
    main()
