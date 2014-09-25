import random


NAME_FILE = 'names.txt'

names = []



# POSSIBLE AI TYPES:
#   SMART: FAVOUR USING CHARACTERS THAT ARE BETTER AGAINST OPPONENT'S LETTERS
#   PASSIVE: FAVOUR FILLING EMPTY SPACES
#   AGGRESSIVE: FAVOUR GOING DIRECTLY TOWARD THE OPPONENT'S SPACES



class Player:
    def __init__(self, name=None, colour=None):
        self.name = name.upper() if name else random_name().upper()
        self.colour = colour if colour else random_colour()
        self.spaces = []


    def __repr__(self):
        return '<Player {}>'.format(self.name)


    def next_move(self):
        possible_moves = [m for s in self.spaces for m in s.possible_moves()]
        return random.choice(possible_moves)


class Move:
    def __init__(self, space, player, letter, attributes=None):
        self.space = space
        self.player = player
        self.letter = letter
        self.attributes = attributes if attributes else player.colour


class Conflict:
    def __init__(self, space):
        self.space = space
        self.options = [{'letter': c.letter, 'attributes': c.attributes}
                        for c in space.claims]
        self.options.append({'letter': space.letter,
                             'attributes': space.attributes})


def random_name():
    if not names:
        with open(NAME_FILE, 'r') as f:
            for line in f:
                names.append(line.split(' ', 1)[0])

    return random.choice(names)


def random_colour():
    pass
