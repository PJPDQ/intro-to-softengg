import itertools
import bisect
import random
from ee import *
import tkinter as tk

# Number of rows/columns in the grid
GRID_SIZE = 6

GRID_CELL_WIDTH = GRID_CELL_HEIGHT = 80  # Pixel width/height of grid cell
GRID_PADDING = 14  # Pixel width/height to use as padding between cells.

# Pixel width/height of grid
GRID_WIDTH = 550  # (GRID_SIZE - 1) * GRID_PADDING + GRID_SIZE * GRID_CELL_WIDTH
GRID_HEIGHT = 550  # (GRID_SIZE - 1) * GRID_PADDING + GRID_SIZE * GRID_CELL_HEIGHT

# The size of the player/enemy
CHARACTER_WIDTH = 200
CHARACTER_HEIGHT = GRID_HEIGHT

# A run must have at least this many cells in a straight line to be removed
MINIMUM_STRAIGHT_RUN = 3

PERFORMANCE_SCALE = 400  # For CSSE7030 students
SLOWNESS = 1  # A positive integer to increase the slowness of animation

DROP_TIME = 250 * SLOWNESS  # Time to take dropping a cell by one row
DROP_STEPS = 5  # Number of steps to take while dropping a tile
# Time to wait before dropping tile another step
DROP_TIME_STEP = DROP_TIME // DROP_STEPS

# Time to wait between removing next run (prior to dropping new tiles)
RUN_REMOVE_STEP = 250 * SLOWNESS

# Direction labels/deltas
NORTH = 'n'
EAST = 'e'
SOUTH = 's'
WEST = 'w'

DIRECTION_DELTAS = {
    NORTH: (-1, 0),
    EAST: (0, 1),
    SOUTH: (1, 0),
    WEST: (0, -1)
}

# Task 1 format strings
SCORE_FORMAT = "Score: {: >9}"
SWAPS_FORMAT = "{} swap{} made"

# 1 swap
# 2 swaps
# 3 swaps

# Task 2 format strings
SWAPS_LEFT_FORMAT = "{} swap{} left"
HEALTH_FORMAT = "Health: {:>6}"
LEVEL_FORMAT = "Level {}"

# Colours for each tile
TILE_COLOURS = {
    'fire': 'red',
    'poison': 'green',
    'water': 'blue',
    'coin': 'gold',
    'psychic': 'purple',
    'ice': 'light sky blue'
}

# Ratio of probabilities that a tile of this type will be generated.
TILE_PROBABILITIES = {
    'fire': 20,
    'poison': 20,
    'water': 20,
    'coin': 10,
    'psychic': 20,
    'ice': 20
}

# Ratio of probabilities that an enemy of this type will be generated.
ENEMY_PROBABILITIES = {
    'fire': 1,
    'water': 1,
    'poison': 1,
    'psychic': 1,
    'ice': 1
}

# Player defaults
SWAPS_PER_TURN = 5
PLAYER_BASE_HEALTH = 500
PLAYER_BASE_ATTACK = 10

# Values used to generate enemies
ENEMY_BASE_HEALTH = 500
ENEMY_BASE_ATTACK = 100
ENEMY_ATTACK_RANGE = .8, 1.25
ENEMY_HEALTH_RANGE = .8, 1.25

ENEMY_HEALTH_DELTA = 200
ENEMY_ATTACK_DELTA = 40

def generate_enemy_stats(level):
    """
    Generates health and attack stats for an enemy found on a given level.

    generate_enemy_stats(int) -> (int, (int, int))
    """
    health_factor = (level + 1) // 2  # Boost attack on odd levels
    attack_factor = level // 2  # Boost attack on even levels

    health = ENEMY_BASE_HEALTH + health_factor * ENEMY_HEALTH_DELTA
    attack = ENEMY_BASE_ATTACK + attack_factor * ENEMY_ATTACK_DELTA

    min_factor, max_factor = ENEMY_ATTACK_RANGE
    attack = int(min_factor * attack), int(max_factor * attack)

    health *= random.uniform(*ENEMY_HEALTH_RANGE)

    return int(health), attack

class WeightedTable:
    """Provides random choice between multiple items, according to their
    relative probability weightings."""

    def __init__(self, items):
        """
        Constructor(dict(*: num))

        Precondition: each value in items is >= 0
        """

        self._values, self._weights = zip(*items)
        cumsum = list(itertools.accumulate(self._weights))
        total = cumsum[-1]
        self._p = [i / total for i in cumsum]

    def choose(self):
        """
        Returns a random option, based upon the probability weights.
        """
        i = bisect.bisect(self._p, random.random())
        return self._values[i]

    def clone(self, removed=None, added=None):
        """
        Clones this WeightedTable, and removes/adds certain items.

        WeightedTable.clone(WeightedTable, set, dict) -> WeightedTable

        :param removed: An iterable of items to remove from the cloned table.
                        Defaults to None.
        :param added: A dictionary of {items: weights} of new items to add to
                      the cloned table. Defaults to None.
        """

        if not removed:
            removed = set()
        else:
            removed = set(removed)

        items = [(value, weight) for value, weight in
                 zip(self._values, self._weights) if
                 value not in removed]

        if added:
            items += added

        return WeightedTable(items)

    def __repr__(self):
        return "WeightedTable({!r})".format(
            list(zip(self._values, self._weights)))


class Tile:
    "Represents a tile in the game."

    def __init__(self, type):
        """
        Constructor(str)
        :param type: The type of this tile.
        """
        self._type = type
        self._selected = False

    def get_type(self):
        """
        Returns the type of this tile.

        Tile.get_type(Tile) -> str
        """
        return self._type

    def set_type(self, type):
        """
        Sets the type of this tile.

        Tile.set_type(Tile, str)
        """
        self._type = type

    def get_selected(self):
        """
        Returns whether this tile is selected.

        Tile.get_selected(Tile) -> bool
        """
        return self._selected

    def set_selected(self, selected):
        """
        Sets whether this tile is selected.

        Tile.get_selected(Tile) -> bool
        """
        self._selected = selected

    def get_colour(self):
        """
        Returns the colour of this tile.
        Tile.get_colour(Tile) -> str
        """
        return TILE_COLOURS[self._type]

    def __eq__(self, other):
        "Returns True iff this tile is equal to the other."
        return self._type == other._type

    def equivalent_to(self, other):
        "Returns True if this tile is equivalent to the other."
        return self._type == other._type

    def __repr__(self):
        "Returns Pythonic representation of this object."
        return "Tile({!r})".format(self._type)


class GridManager:
    "Manages positions in a grid, with methods for validation and navigation."

    def __init__(self, size=None):
        """
        Constructor(GridManager, (int, int))
        Constructor(GridManager)

        :param size: The size of the grid, in (rows, columns). Defaults to None.
        """

        self._size = size

    def set_size(self, size):
        """
        Sets the size of the grid to the given (row, column) pair.

        GridManager.set_size(GridManager, (int, int)) -> None
        """
        self._size = size

    def is_cell_position_valid(self, position):
        """
        Returns True iff the given position is valid for the grid.

        Precondition: size has been set to a (row, column) pair.

        GridManager.is_cell_position_valid(GridManager, (int, int)) -> bool

        :param position: (row, column) position to check.
        """
        row, column = position
        rows, columns = self._size

        return 0 <= row < rows and 0 <= column < columns

    def move(self, position, direction):
        """
        Returns new position after moving in direction from position.

        Precondition: direction in DIRECTION_DELTAS

        :param position: (row, column) position.
        :param direction: Direction to move. One of NORTH, SOUTH, EAST, WEST.
        """

        row, column = position
        drow, dcolumn = DIRECTION_DELTAS[direction]

        return row + drow, column + dcolumn

    def get_valid_neighbours(self, position, directions=None):
        """
        Yields sequence of valid neighbours surrounding position. Excludes
        neighbours that are out of bounds.

        :param position: Position to find neighbours of.
        :param directions: Sequence of directions to move.
                           Defaults to DIRECTION_DELTAS.
        """
        if not directions:
            directions = DIRECTION_DELTAS

        for neighbour in self.get_neighbours(position, directions):
            if self.is_cell_position_valid(neighbour):
                yield neighbour

    def get_neighbours(self, pos, directions=None):
        """
        Yields sequence of neighbours surrounding position. Includes neighbours
        without valid positions (i.e. out of bounds).

        :param position: Position to find neighbours of.
        :param directions: Sequence of directions to move.
                           Defaults to DIRECTION_DELTAS.
        """
        for direction in directions:
            yield self.move(pos, direction)

    def explore(self, position, *directions, include=None):
        """
        Yields every neighbour of position in given directions.

        :param position: Position to explore from.
        :param directions: Sequence of directions to move.
        :param include: Function that accepts a (row, column) pair as an
                        argument and returns True iff the given position should
                        be included, else False. If this function returns False,
                        exploration in the current direction ceases.
        """
        for direction in directions:
            if not include:
                include = lambda position: True

            while True:
                position = self.move(position, direction)
                if not include(position):
                    return
                yield position


class Span:
    "A span has distances to four corners (of the compass)."

    def __init__(self, distances):
        """
        Constructor(Span, {str: num})

        :param distances: Dictionary with keys NORTH, SOUTH, EAST, WEST, and values that
                     are distances from a centre point.
        """
        self._distances = distances

    def get_dimensions(self):
        """
        Returns the dimensions of the span, in the form:
            ((width, height), (horizontal skew), (vertical skew))

        get_dimensions(Span) -> ((int, int), (int, int))


        """
        v_skew = abs(self._distances[NORTH] - self._distances[SOUTH])
        h_skew = abs(self._distances[EAST] - self._distances[WEST])

        width = self._distances[NORTH] + self._distances[SOUTH]
        height = self._distances[EAST] + self._distances[WEST]

        return (width, height), (h_skew, v_skew)

    def dominates(self, other):
        """
        Returns True if span dominates other.

        dominates(Span, Span) -> bool
        """
        (width, height), (h_skew, v_skew) = self.get_dimensions()
        (o_width, o_height), (o_h_skew, o_v_skew) = other.get_dimensions()

        # Span dominated by other (not necessarily absolutely)
        if width < o_width or height < o_height:
            return False

        # Equally dominant, but with better skews
        if width == o_width and height == o_height:
            return h_skew >= o_h_skew and v_skew >= o_v_skew

        # Span absolutely dominates other
        return width >= o_width and height >= o_height


class Run:
    """
    Represents a run of connected cells.
    """

    def __init__(self, cells):
        """
        Constructor()
        """
        self._cells = cells
        self._pm = GridManager()

        self._calculate_dimensions()

    @staticmethod
    def from_set(cells_set, tile=None):
        """
        Builds a run from a set of cell positions.

        Run.from_set(set) -> Run
        Run.from_set(set, tile|None) -> Run
        """
        return Run(dict.fromkeys(cells_set, tile))

    def _calculate_dimensions(self):
        """
        Calculates the dimensions of this run, in the form:
            (longest horizontal, longest vertical)
        """
        width = height = 0
        pm = self._pm
        cells = self._cells
        include = lambda position: position in cells

        ns_visited = set()
        ew_visited = set()

        for cell in self._cells:
            ns_visited.add(cell)
            ns_run = {cell}

            # North/South
            for pos in pm.explore(cell, NORTH, SOUTH, include=include):
                ns_visited.add(pos)
                ns_run.add(pos)

            height = max(height, len(ns_run))

            ew_visited.add(cell)
            ew_run = {cell}

            # East/West
            for pos in pm.explore(cell, EAST, WEST, include=include):
                ew_visited.add(pos)
                ew_run.add(pos)

            width = max(width, len(ew_run))

        self._dimensions = width, height
        return self._dimensions

    def find_dominant_cell(self):
        """
        Returns the dominant cell of this run.

        A dominant cell is the one in the centre of the longest combined
        horizontal and vertical runs, with ties being decided by the cell
        closest to the centre.
        """
        dominant_span = Span({d: 0 for d in DIRECTION_DELTAS})
        dominant_cell = None
        pm = self._pm
        cells = self._cells
        include = lambda position: position in cells

        for cell in self._cells:
            distances = {}
            # Explore all directions
            for direction in DIRECTION_DELTAS:
                distance = 0
                for pos in pm.explore(cell, direction, include=include):
                    distance += 1
                distances[direction] = distance

            span = Span(distances)

            if span.dominates(dominant_span):
                dominant_span = span
                dominant_cell = cell

        return dominant_cell

    def remove(self, cell):
        """
        Removes a cell from this Run.

        Run.remove((int, int)) -> None
        """
        self._cells.pop(cell)

        self._calculate_dimensions()

    def get_dimensions(self):
        """
        Returns a pair of longest straight paths in this run, of the form:
            (horizontal, vertical)

        Run.get_dimensions() -> (int, int)
        """
        return self._dimensions

    def get_max_dimension(self):
        """
        Returns the size of the longest straight path in this run.

        Run.get_max_dimension() -> int
        """
        return max(self._dimensions)

    def __len__(self):
        """
        Returns the number of cells in this Run.
        """
        return len(self._cells)

    def __getitem__(self, cell):
        """
        Returns the value associated with cell.

        Raises KeyError if cell is not in this run.
        """
        return self._cells[cell]

    def __setitem__(self, cell, value):
        """
        Sets the value associated with cell.
        """
        self._cells[cell] = value

    def __delitem__(self, cell):
        """
        Removes a cell from this run.
        """
        return self.remove(cell)

    def __iter__(self):
        """
        Returns an iterator over all cells in this Run.
        """
        return iter(self._cells)

    def items(self):
        """
        Returns an iterator over all cell, value pairs in this Run.
        """
        return self._cells.items()

    def __repr__(self):
        return "Run({!r})".format(set(self._cells.keys()))


class TileGrid(EventEmitter):
    """"
    Models a tile grid.

    Emits:
        - swap (from_pos, to_pos): When a swap is initiated.
        - swap_resolution (from_pos, to_pos):   When a swap has been completely
                                                resolved.
        - run (run_number, runs):   When a group of runs has been detected and is
                                    about to be removed.
    """

    def __init__(self, types, rows=GRID_SIZE, columns=GRID_SIZE):
        """
        Constructor(WeightedTable, int, int)
        :param types: A WeightedTable of the probability of generating each tile.
        :param rows: The number of rows in the grid.
        :param columns: The number of columns in this grid.
        """
        super().__init__()

        self._cells = [[None for j in range(columns)] for i in range(rows)]
        self._types = WeightedTable(types.items())

        self._size = rows, columns

        self._grid_manager = GridManager(self._size)

        self.generate()

    def generate(self):
        """
        Populates the TileGrid with tiles.

        TileGrid.generate(TileGrid) -> None
        """
        rows, columns = self._size

        for i in range(rows):
            for j in range(columns):
                self._cells[i][j] = self.generate_cell()

        # Remove runs
        for run in self.find_runs():
            # print("----RUN----")
            # print(run)
            while run.get_max_dimension() >= MINIMUM_STRAIGHT_RUN:
                dominant = run.find_dominant_cell()
                dominant_tile = self[dominant]
                old_type = dominant_tile.get_type()

                # print(
                #     "{} is dominant in {}: {}".format(dominant, old_type, run))

                types = {old_type}

                for position in self._grid_manager.get_valid_neighbours(
                        dominant):
                    types.add(self[position].get_type())

                types = self._types.clone(types)
                new_type = types.choose()
                # print(
                #     "Changing from {} to {}, with {}".format(old_type, new_type,
                #                                              types))
                self[dominant].set_type(new_type)

                run.remove(dominant)

    def generate_cell(self):
        """
        Returns a randomly generated tile.

        TileGrid.generate_cell(TileGrid) -> Tile
        """
        return Tile(self._types.choose())

    def get_grid_manager(self):
        """
        Returns the grid manager used by this TileGrid.

        TileGrid.get_grid_manager(TileGrid) -> GridManager
        """
        return self._grid_manager

    def get_size(self):
        """
        Returns the (row, column) size of this TileGrid.

        TileGrid.get_size(TileGrid) -> (int, int)
        """
        return self._size

    def __getitem__(self, position):
        """
        Returns the cell at (row, column) position.

        Enables tile_grid[(row, column)] syntax.
        """
        row, column = position
        return self._cells[row][column]

    def __setitem__(self, position, tile):
        """
        Sets the cell at (row, column) position to tile.

        Enables tile_grid[(row, column)] = tile syntax.
        """
        row, column = position
        self._cells[row][column] = tile

    def __contains__(self, position):
        """
        Returns True iff position corresponds to a (row, column) position on this TileGrid and
        there exists a tile at that position.

        Enables position in tile_grid syntax
        """
        return position >= (0, 0) and self[position] is not None

    def pop(self, position):
        """
        Removes and returns  the tile at the given (row, column) position from
        this TileGrid.

        TileGrid.pop(TileGrid, (int, int)) -> Tile
        """
        tile = self[position]
        self[position] = None
        return tile

    def __iter__(self):
        """
        Returns an iterator over all tiles in this TileGrid.

        Enables for cell in tile_grid: pass syntax.
        :return:
        """
        rows, columns = self._size
        for i in range(rows):
            for j in range(columns):
                yield ((i, j), self._cells[i][j])

    def swap(self, from_pos, to_pos):
        """
        Swaps the cells at the given (row, column) positions.

        Yields changes that occur as a result.
        """
        tmp = self[from_pos]
        self[from_pos] = self[to_pos]
        self[to_pos] = tmp

        self.emit('swap', from_pos, to_pos)

        def run_detector():
            # repeatedly detect runs
            for runs_num in itertools.count():
                runs = self.find_runs()

                empty = [0 for i in range(self._size[1])]

                results = []

                deleted_per_col = [[] for i in range(self._size[1])]

                # remove cells in runs
                for run in runs:
                    for cell in run:
                        row, column = cell
                        bisect.insort(deleted_per_col[column], row)
                        tile = self.pop(cell)
                        empty[column] += 1

                    result = run
                    results.append(result)

                # print("Need to generate: {}".format(empty))

                new_per_col = [[self.generate_cell() for i in range(removed)]
                               for removed in empty]

                # drop cells
                drops = {}
                for column, rows in enumerate(deleted_per_col):
                    rows = rows[:]

                    minimum = -len(rows)
                    replacements = []

                    if minimum < 0:
                        replacements = [i for i in range(minimum, rows[-1] + 1)
                                        if i not in rows]
                        # Clean up
                        for i in replacements:
                            if i not in rows:
                                bisect.insort(rows, i)

                        replacements.reverse()
                        rows.reverse()

                        for to_row, from_row in zip(rows, replacements):
                            to_cell = to_row, column
                            from_cell = from_row, column

                            if from_row >= 0:
                                self[to_cell] = self.pop(from_cell)
                            else:
                                self[to_cell] = new_per_col[column][from_row]

                                # print("{} moved to {}".format(from_cell, to_cell))

                    deleted_per_col[column] = zip(rows, replacements)

                if not len(results):
                    break

                self.emit('run', runs_num, runs)

                yield results, deleted_per_col, new_per_col

            self.emit('swap_resolution', from_pos, to_pos)

        return run_detector()

    # def _move_in_dir(self, position, run, direction, path=None):
    #
    #     if not path:
    #         path = set()
    #
    #     last_position = position
    #     while True:
    #         last_position = self._grid_manager.move(last_position,
    #                                                 direction)
    #
    #         if last_position not in run:
    #             break
    #
    #         path.add(last_position)
    #
    #     return path

    def find_runs(self, positions=None):
        """
        Finds runs in this TileGrid that start at each position in positions.
        If position is None, all positions in this grid are considered.

        TileGrid.find_runs(TileGrid[, set((int, int))) -> list(Run)
        """
        runs = []

        rows, columns = self._size

        if not positions:
            positions = set(itertools.product(range(rows), range(columns)))

        # Implementation of repeated depth-first search to find potential runs
        while len(positions):
            v = positions.pop()
            root = self[v]

            S = set()
            S.add(v)

            run = set()

            while len(S):
                v = S.pop()

                if v not in run:
                    run.add(v)
                    for w in self._grid_manager.get_valid_neighbours(v):
                        neighbour = self[w]
                        if root == neighbour:
                            S.add(w)

            if len(run) >= MINIMUM_STRAIGHT_RUN:
                run = Run({cell: self[cell] for cell in run})

                for pos in run:
                    try:
                        positions.remove(pos)
                    except KeyError:
                        pass

                if max(run.get_dimensions()) >= MINIMUM_STRAIGHT_RUN:
                    runs.append(run)

        return runs


class TileGridView(tk.Canvas):
    "Visual representation of a TileGrid."

    def __init__(self, master, grid, *args, width=GRID_WIDTH,
                 height=GRID_HEIGHT,
                 cell_width=GRID_CELL_WIDTH, cell_height=GRID_CELL_HEIGHT,
                 **kwargs):
        """
        Constructor(tk.Frame, TileGrid, *, int, int, int, int, *)

        :param master: The tkinter master widget/window.
        :param width: Total width of the grid.
        :param height: Total height of the grid.
        :param cell_width: Width of each cell.
        :param cell_height: Height of each cell.
        """

        super().__init__(master, width=width, height=height, **kwargs)

        self._master = master

        self._resolving = False

        self._sprites = {}

        self._selected = []

        self._enabled = True

        self._grid = grid

        self._width = width
        self._height = height

        self._cell_width = cell_width
        self._cell_height = cell_height

        rows, columns = self._grid.get_size()

        self._x_padding = (self._width - columns * (self._cell_width)) // (
            columns - 1)
        self._y_padding = (self._height - rows * (self._cell_height)) // (
            rows - 1)

        self._x_width = cell_width + self._x_padding
        self._y_height = cell_height + self._y_padding

        self._calculate_positions()

        self.draw()

        self.bind('<Button-1>', self._click)
        self.bind('<ButtonRelease-1>', self._release)

    def is_resolving(self):
        """Returns True iff this TileGridView is currently resolving a swap.

        TileGridView.is_resolving(TildGridView)"""
        return self._resolving

    def xy_to_rc(self, xy_pos):
        """
        Converts an (x, y) position to (row, column) position on this TileGrid,
        else None.

        TileGridView.xy_to_rc(TileGridView, (int, int)) -> (int, int)
        TileGridView.xy_to_rc(TileGridView, (int, int)) -> None
        """
        x, y = xy_pos
        x_rem = x % self._x_width
        x_on = x_rem <= self._cell_width

        if not x_on:
            return

        y_rem = y % self._y_height
        y_on = y_rem <= self._cell_height

        if not y_on:
            return

        return y // self._y_height, x // self._x_width

    def rc_to_xy_centre(self, rc_pos):
        """
        Converts a (row, column) position on this TileGrid to the (x, y)
        position of the cell's centre.

        TileGridView.rc_to_xy_centre(TileGridView, (int, int)) -> None
        """
        row, column = rc_pos

        return self._xs[column], self._ys[row]

    def undraw_tile_sprite(self, position):
        """Undraws the sprite for the tile at given (row, column) position.

        TileGridView.undraw_tile_sprite(TileGridView, (int, int)) -> None"""
        if position in self._sprites:
            self.delete(self._sprites[position])
            self._sprites[position] = None

    def draw_tile_sprite(self, xy_pos, tile, selected):
        """Draws the sprite for the given tile at given (x, y) position.

        TileGridView.undraw_tile_sprite(TileGridView, (int, int), Tile, bool)
                                                                    -> None"""
        colour = tile.get_colour()

        width, height = self._calculate_tile_size(xy_pos, selected)
        x, y = xy_pos
        return self.create_rectangle(
            x - width, y - height, x + width, y + height, fill=colour)

    def redraw_tile(self, rc_pos, selected=False, tile=None, offset=(0, 0)):
        """Redraws the sprite for the tile at given (row, column) position.

        TileGridView.undraw_tile_sprite(TileGridView, (int, int)) -> None"""
        if not tile:
            tile = self._grid[rc_pos]

        self.undraw_tile_sprite(rc_pos)

        x, y = self.rc_to_xy_centre(rc_pos)

        x += offset[0]
        y += offset[1]

        self._sprites[rc_pos] = self.draw_tile_sprite((x, y), tile, selected)

    def _calculate_tile_size(self, pos, selected):
        """Calculates and returns the size of a tile depending upon whether
        it is selected."""
        if selected:
            return (self._cell_width + self._x_padding) // 2, (
                self._cell_height + self._y_padding) // 2
        else:
            return self._cell_width // 2, self._cell_height // 2

    def draw(self):
        """Draws every cell in this TileGridView."""
        self.delete(tk.ALL)

        for pos, cell in self._grid:
            self.redraw_tile(pos, selected=False, tile=cell)

    def disable(self):
        """Disables this TileGridView."""
        self._enabled = False

    def enable(self):
        """Enables this TileGridView."""
        self._enabled = True

    def _click(self, ev):
        """Handles left mouse click."""
        if self._resolving or not self._enabled:
            return

        pos = self.xy_to_rc((ev.x, ev.y))

        if pos is None:
            return

        selected = self._selected == [] or pos not in self._selected

        self.redraw_tile(pos, selected=selected)

        if selected:
            self._selected.append(pos)
        else:
            self._selected.remove(pos)

    def _release(self, ev=None):
        """Handles left mouse release."""
        if self._resolving or not self._enabled:
            return

        if len(self._selected) == 2:
            from_pos, to_pos = self._selected
            self.swap(from_pos, to_pos)
            self._selected = []

    ###########################################################################
    ######################## BEGIN COMPLICATED METHODS ########################
    ################### (Students needn't understand these) ###################
    ###########################################################################

    def _calculate_positions(self):

        half_width = self._cell_width // 2
        half_height = self._cell_height // 2

        rows, columns = self._grid.get_size()

        self._positions = [[None for j in range(columns)] for i in range(rows)]

        xs = [half_width + i * (self._cell_width + self._x_padding) for i in
              range(columns)]
        ys = [half_height + j * (self._cell_height + self._y_padding) for j in
              range(rows)]

        self._xs = xs
        self._ys = ys

        for i in range(rows):
            for j in range(columns):
                self._positions[i][j] = xs[j], ys[i]

    def _animate_drops_step(self, cell_steps):
        while len(cell_steps):
            for key in list(cell_steps.keys()):
                to_row, column = key
                from_row, steps = cell_steps[key]

                to_cell = to_row, column

                steps -= 1

                # get tile
                tile = self._grid[to_cell]

                # redraw with offset
                dy = -self._y_height * steps / DROP_STEPS

                self.redraw_tile(to_cell, tile=tile,
                                 offset=(0, dy))

                if steps == 0:
                    cell_steps.pop((to_row, column))
                    continue

                cell_steps[key] = from_row, steps

            yield

    def _animate_runs_step(self, runs):
        for run in runs:
            for cell in run:
                self.undraw_tile_sprite(cell)
                if cell not in self._grid:
                    continue

            yield

    def _create_animation_stepper(self, steps, delay, callback=None):
        def stepper():
            try:
                next(steps)
                if delay is not None:
                    self._master.after(delay, stepper)
            except StopIteration:
                if callback:
                    callback()

        return stepper

    def swap(self, from_pos, to_pos):
        if self._resolving:
            return

        self._resolving = True
        run_steps = self._grid.swap(from_pos, to_pos)
        self.redraw_tile(from_pos, selected=False)
        self.redraw_tile(to_pos, selected=False)

        # this is a crap fest
        def process_run_string(done):

            data = {}

            fns = {
                'remove_runs': lambda data,
                                      callback: self._create_animation_stepper(
                    self._animate_runs_step(data['changes']),
                    RUN_REMOVE_STEP,
                    callback),
                'drop_tiles': lambda data,
                                     callback: self._create_animation_stepper(
                    self._animate_drops_step(
                        data['cell_steps']), DROP_TIME_STEP, callback)
            }

            # process runs
            for changes, deleted_per_col, new in run_steps:
                data['changes'] = changes
                processed_runs = self._animate_runs_step(changes)

                def callback():
                    cell_steps = {}
                    for column, row_changes in enumerate(deleted_per_col):
                        for to_row, from_row in row_changes:
                            cell_steps[(to_row, column)] = from_row, (
                                to_row - from_row) * DROP_STEPS

                            if from_row >= 0:
                                self.undraw_tile_sprite((from_row, column))

                    data['cell_steps'] = cell_steps

                    fns['drop_tiles'](data, done)()

                fns['remove_runs'](data, callback)()

                yield

        def done():
            self._resolving = False

        callback = lambda: self._master.after(500, stepper)
        steps = process_run_string(callback)
        stepper = self._create_animation_stepper(steps, None,
                                                 done)

        stepper()

        ###########################################################################
        ######################### END COMPLICATED METHODS #########################
        ################### (Students needn't understand these) ###################
        ###########################################################################


class SimpleGame(EventEmitter):
    """"
    Models a simple game.

    Emits:
        - swap (from_pos, to_pos):
            When a swap is initiated.
        - swap_resolution (from_pos, to_pos):
            When a swap has been completely resolved.
        - run (run_number, runs):
            When a group of runs has been detected and is about to be removed.
        - score (score):
            When a score has been earned.
    """
    def __init__(self):
        """
        Constructor()
        """
        super().__init__()

        self._grid = TileGrid(TILE_PROBABILITIES)
        self._grid.on('run', self._handle_runs)
        self._grid.on('swap', self._handle_swap)
        self._grid.on('swap_resolution', self._handle_swap_resolution)

        self._resolving = False

    def get_grid(self):
        """
        Returns the TileGrid for this SimpleGame.

        SimpleGame.get_grid(SimpleGame) -> TileGrid
        """
        return self._grid

    def _handle_swap(self, from_pos, to_pos):
        """
        Handles the initiation of a swap (before all runs have been resolved).

        Emits swap.

        SimpleGame._handle_swap(SimpleGame, (int, int), (int, int)) -> None
        """
        self.emit('swap', from_pos, to_pos)

    def _handle_swap_resolution(self, from_pos, to_pos):
        """
        Handles the resolution of a swap (after all runs have been resolved).

        Emits swap_resolution.

        SimpleGame._handle_swap_resolution(SimpleGame, (int, int), (int, int))
                                                                        -> None
        """
        self.emit('swap_resolution', from_pos, to_pos)

    def _handle_runs(self, runs_number, runs):
        """
        Converts runs into score.

        Emits score, runs.

        SimpleGame._handle_runs(SimpleGame, int, list(Runs)) -> None
        """
        score = 0
        for run in runs:
            score += (len(run) * run.get_max_dimension()) * 10

        score *= (runs_number + 1)

        self.emit('score', score)
        self.emit('run', runs)

    def reset(self):
        """
        Resets this SimpleGame.

        SimpleGame.reset(SimpleGame) -> None
        """
        self._grid.generate()
