import random

# Maze symbol constants
WALL = '#'
OPEN = ' '
PLAYER = 'A'

START_POSITION = (1, 1)

POKEMON = {
    'P': 'Pikachu',
    'Z': 'Zubat',
    'D': 'Doduo',
    'R': 'Rattata',
    'W': 'Weedle',
    '?': '???'
}

GOOD_POKEMON = 'P'
BAD_POKEMON = 'ZDRW'

DIRECTIONS = 'nsew'

DIRECTION_DELTAS = {
    'n': (-1, 0),
    'e': (0, 1),
    's': (1, 0),
    'w': (0, -1)
}

HELP_TEXT = """? - Help.
n - Move North one square.
s - Move South one square.
e - Move East one square.
w - Move West one square.
r - Reset to the beginning.
b - Back up a move.
p - List all legal directions from the current position.
q - Quit."""

LOSE_TEXT = "Oh no! A wild {} appeared - you lose :("
WIN_TEXT = "Congratulations - you found {}!"

def load_maze(filename):
    """
    Loads a maze from file, ignoring surrounding whitespace.

    load_maze(str) -> str
    """

    with open(filename, 'r') as f:
        return f.read().strip()

def maze_columns(maze):
    """
    Returns the number of columns in the maze.

    maze_columns(str) -> int
    """

    return maze.find('\n')

def maze_rows(maze):
    """
    Returns the number of rows in the maze.

    maze_rows(str) -> int
    """

    return maze.count('\n') + 1

def position_to_index(position, columns):
    """
    Converts a (row, column) position pair into a single index.

    position_to_index((int, int), int) -> int
    """

    row, column = position
    return row * (columns + 1) + column

def index_to_position(index, columns):
    """
    Converts a single index into a (row, column) position pair.

    index_to_position(int, int) -> (int, int)
    """

    row = index // (columns + 1)
    column = index % (columns + 1)

    return row, column

##########


def index_position_mapping_test(rows=3, columns=None):
    if not columns:
        columns = rows

    for row in range(rows):
        for column in range(columns):
            works = (row, column) == index_to_position(
                position_to_index((row, column), columns), columns)
            print("{} -> {}: {}".format((row, column),
                                        position_to_index((row, column),
                                                          columns), works))

    for i in range(rows * (columns + 1)):
        works = i == position_to_index(index_to_position(i, columns),
                                       columns)
        print(
            "{} -> {}: {}".format(i, index_to_position(i, columns), works))