try:
    import model_solution as model
except ImportError:
    try:
        import a2 as model
    except ImportError:
        print("No assignment could be found.")
        exit()

from a2_support import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
import os

# size of a grid cell
CELL_WIDTH = 60
CELL_HEIGHT = 60

VERSION = "1.0.4"
TITLE = "Gotta Catch 'Em All!"
WELCOME_MESSAGE = """
Welcome to Pokemon Finder {version} (final)
Gotta Catch 'Em All!
""".format(version=VERSION).strip()

# default url for loading file from url
DEFAULT_LOAD_URL = "http://csse1001.uqcloud.net/2016s2a2/pokemon-map.json?levels=4&rows=12&columns=12"
# DEFAULT_LOAD_URL = DEFAULT_LOAD_URL.replace("http://csse1001.uqcloud.net/", "http://localhost:3000/")

# see below
IMAGE_MAPPINGS = """
pokemon/colour/ -> images/pokemon/{}_c.gif
pokemon/black/  -> images/pokemon/{}_b.gif
pokemon/gray/   -> images/pokemon/{}_g.gif
players/        -> images/players/hgss_{}.gif
general/        -> images/{}.gif
"""

# Pokemon colours
POKEMON_COLOUR_FULL = 'colour'
POKEMON_COLOUR_GRAY = 'gray'
POKEMON_COLOUR_BLACK = 'black'

# map of image groups to file paths
IMAGE_MAPPINGS = dict(tuple(s.strip() for s in m.split('->'))
                      for m in IMAGE_MAPPINGS.strip().split('\n'))

PLAYER_IDS = range(0, 127 + 1)  # range of valid player sprite ids
PLAYER_ROWS = 8  # number of rows when choosing player sprite
PLAYER_COLUMNS = 16  # number of columns, as above
DEFAULT_PLAYER_ID = 0  # initial player sprite id

# colours for each terrain type
# (wall colour, background colour)
REGION_COLOURS = {
    "Ice": ("#0076ad", "#a8cdd5"),
    "Grass": ("#57280c", "#71b369"),
    "Mountain": ("#301700", "#6a5f4f"),
    "Beach": ("#554428", "#efedbc")
}

DEFAULT_REGION_COLOUR = ("#927c8d", "white")

# directions that each key map to
KEY_DIRECTIONS = {
    'Up': NORTH,
    'Down': SOUTH,
    'Left': WEST,
    'Right': EAST,
    'w': NORTH,
    's': SOUTH,
    'a': WEST,
    'd': EAST
}


class ImageManager(object):
    """
    Manages images, caching after first load.
    """

    def __init__(self, mappings):
        """
        Constructor

        ImageManager.__init__(ImageManager, dict)
        """
        self._mappings = mappings
        self._images = {}

    def get_image(self, prefix, *args):
        """
        Returns image by name. Loads if not already loaded.

        ImageManager.get_image(ImageManager) -> tk.PhotoImage
        """
        name = prefix + "/".join(str(a) for a in args)
        filename = self._mappings[prefix].format(*args)

        if name not in self._images:
            # load_file image
            self._images[name] = tk.PhotoImage(file=filename)

        return self._images[name]


class PokemonManager(object):
    """
    Manages bidirectional mapping of Pokemon names to ids.
    """
    _name_by_id = None
    _id_by_name = None

    @classmethod
    def init(cls, name_file="pokemon.txt", force=False):
        """
        Initializes PokemonManager

        PokemonManager.init(PokemonManager, str[, bool]) -> None
        """

        # don't reinitialize
        if cls._name_by_id is not None and not force:
            return

        # load_file names
        cls._name_by_id = {}
        cls._id_by_name = {}

        with open(name_file, 'r', encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                id, name = line.split(' ', 1)
                id = int(id)
                cls._name_by_id[id] = name
                cls._id_by_name[name] = id

    @classmethod
    def get_name_by_id(cls, id):
        """
        Returns name of pokemon with given id, else None.

        PokemonManager.get_name_by_id(PokemonManager, int) -> str
        """

        return cls._name_by_id.get(id)

    @classmethod
    def get_id_by_name(cls, name):
        """
        Returns id of pokemon with given name, else None.

        PokemonManager.get_name_by_id(PokemonManager, name) -> int
        """

        return cls._id_by_name.get(name)

    @classmethod
    def get_names(cls):
        """
        Returns a list of pokemon names, sorted by id.

        PokemonManager.get_names(PokemonManager) -> list(str)
        """

        return [x[1] for x in sorted(cls._name_by_id.items())]


class CoordinateTranslator(object):
    """
    Manages translation between (row, column) and (x, y) coordinates.
    """

    def __init__(self, cell_width=CELL_WIDTH, cell_height=CELL_HEIGHT):
        """
        Constructor

        CoordinateTranslator.__init__(CoordinateTranslator, int, int)
        """
        self._cell_width = cell_width
        self._cell_height = cell_height

    def get_cell_size(self):
        """
        Returns the cell size.

        CoordinateTranslator.get_cell_size(CoordinateTranslator) -> (int, int)
        """
        return self._cell_width, self._cell_height

    def get_row_column(self, x, y):
        return (y // self._cell_width, x // self._cell_height)

    def get_top_left_pixel(self, row, column):
        """
        Returns the pixel coordinates for the top-left position of a cell.

        CoordinateTranslator.get_top_left_pixel(
            CoordinateTranslator, int, int) -> (int, int)
        """
        return column * self._cell_width, row * self._cell_height

    def position_to_pixel_centre(self, row, column):
        """
        Converts (row, column) pair into pixel coordinates for centre of cell.

        CoordinateTranslator.position_to_pixel_centre(
            CoordinateTranslator, int, int) -> (int, int)
        """
        return (column * self._cell_width + self._cell_width // 2,
                row * self._cell_height + self._cell_height // 2)

    def position_to_pixel_boundary(self, row, column):
        """
        Converts (row, column) pair into pixel coordinates for cell boundary.
        Returns (top, left, bottom, right)

        CoordinateTranslator.position_to_pixel_boundary(
            CoordinateTranslator, int, int) -> (int, int, int, int)
        """
        top = row * self._cell_height
        bottom = top + self._cell_height
        left = column * self._cell_width
        right = left + self._cell_width

        return top, left, bottom, right


class GridView(tk.Canvas):
    """
    Handles visuals for the game grid.
    """
    CAUGHT_COLOUR = POKEMON_COLOUR_GRAY
    UNCAUGHT_COLOUR = POKEMON_COLOUR_BLACK

    def __init__(self, master, image_manager, *args, **kwargs):
        """
        Constructor

        GridView.__init__(GridView, tk.tk, ImageManager, *args, **kwargs)
        """
        super().__init__(master, *args, **kwargs)

        self._ct = CoordinateTranslator()
        self._im = image_manager
        self._player_id = DEFAULT_PLAYER_ID
        self._player = None

    def set_player_id(self, id=DEFAULT_PLAYER_ID):
        """
        Sets the player's (sprite) id.

        GridView.set_player_id(GridView, int) -> None
        """
        self._player_id = id

        if self._player is not None:
            self.itemconfig(self._player,
                            image=self._im.get_image("players/", id))

    def load_level(self, level):
        """
        Loads the level into view.

        GridView.load_level(GridView, Level) -> None
        """
        self.delete(tk.ALL)

        self._level = level

        size = level.get_size()
        width, height = self._ct.get_top_left_pixel(*size)
        self.configure(width=width, height=height)

        wall_colour, bg_colour = REGION_COLOURS.get(
            level.get_terrain(),
            DEFAULT_REGION_COLOUR)

        # init bg
        self.create_rectangle(0, 0, width, height, fill=bg_colour,
                              outline=bg_colour)

        self.draw_obstacles()
        self.draw_pokemons()

        # init player
        self._player = None
        self.draw_player_at(*level.get_starting_position())

    def draw_pokemons(self):
        """
        Adds Pokemon to view.

        GridView.draw_pokemons(GridView) -> None
        """
        self._pokemons = {}
        self._pokemon_ids = {}
        for pokemon in self._level.get_pokemons():
            position = pokemon.get_position()
            name = pokemon.get_name()
            id = PokemonManager.get_id_by_name(name)
            x, y = self._ct.position_to_pixel_centre(*position)

            colour = self.CAUGHT_COLOUR if name in self._level.get_dex() \
                else self.UNCAUGHT_COLOUR

            image = self._im.get_image("pokemon/{}/".format(colour), id)
            self._pokemon_ids[position] = id
            self._pokemons[position] = self.create_image(x, y, image=image)

    def draw_obstacles(self):
        """
        Adds obstacles to view.

        GridView.draw_obstacles(GridView) -> None
        """
        level = self._level
        wall_colour, bg_colour = REGION_COLOURS.get(
            level.get_terrain(),
            DEFAULT_REGION_COLOUR)

        for row, column in level.get_obstacles():
            r1 = r2 = row // 1 + 1
            c1 = c2 = column // 1 + 1

            if row % 1 != 0:  # horizontal wall
                c1 = column
                c2 = c1 + 1

            if column % 1 != 0:  # vertical wall
                r1 = row
                r2 = r1 + 1

            x1, y1 = self._ct.get_top_left_pixel(r1, c1)
            x2, y2 = self._ct.get_top_left_pixel(r2, c2)

            self.create_rectangle(x1, y1, x2, y2, fill=wall_colour,
                                  outline=wall_colour)

    def redraw_caught_pokemon(self, row, column, pokemon):
        """
        Redraws the caught Pokemon at (row, column) position.

        GridView.redraw_caught_pokemon(GridView, int, int, Pokemon) -> None
        """
        position = row, column

        if position not in self._pokemons:
            print("No pokemon at {}".format((row, column)))
            return

        positions = [position]

        # find other this_pokemon of the same name
        for this_pokemon in self._level.get_pokemons():
            if pokemon.get_name() == this_pokemon.get_name():
                positions.append(this_pokemon.get_position())

        for i, position in enumerate(positions):
            self.delete(self._pokemons[position])
            del self._pokemons[position]
            id = self._pokemon_ids[position]

            if i == 0:
                continue

            image = self._im.get_image(
                "pokemon/{}/".format(self.CAUGHT_COLOUR), id)
            x, y = self._ct.position_to_pixel_centre(*position)
            self._pokemons[position] = self.create_image(x, y, image=image)

    def draw_player_at(self, row, column):
        """
        Draws player at (row, column) position.

        GridView.draw_player_at(GridView, int, int) -> None
        """

        if self._player is not None:
            self.delete(self._player)

        image = self._im.get_image("players/", self._player_id)
        x, y = self._ct.position_to_pixel_centre(row, column)

        self._player = self.create_image(x, y, image=image)


class DexView(tk.Canvas):
    """
    Handles visuals for a Pokedex.
    """
    REGISTERED_COLOUR = POKEMON_COLOUR_FULL
    UNREGISTERED_COLOUR = POKEMON_COLOUR_BLACK

    def __init__(self, master, image_manager, *args, **kwargs):
        """
        Constructor

        DexView.__init__(tk.Tk, ImageManager, *args, **kwargs)
        """
        super().__init__(master, *args, **kwargs)

        self._im = image_manager

    def load_dex(self, dex, rows=1, cell_width=CELL_WIDTH,
                 cell_height=CELL_HEIGHT):
        """
        Loads a Pokedex.

        DexView.load_dex(DexView, Dex, int, int, int) -> None
        :return:
        """

        self._rows = rows
        self._dex = dex

        self._cell_width = cell_width
        self._cell_height = cell_height

        self.draw()

    def draw(self):
        """
        Draws the Dex.

        DevView.draw(DexView) -> None
        """

        self.delete(tk.ALL)

        dex = self._dex
        rows = self._rows

        columns = 1

        try:
            columns = len(dex) // rows + 1
        except:
            pass

        cell_width, cell_height = self._cell_width, self._cell_height

        self.configure(width=columns * cell_width)

        # self.create_text(self._width//2, 0, text="Pokédex", anchor=tk.N)

        for i, (pokemon, caught) in enumerate(dex.get_pokemons()):
            colour = self.REGISTERED_COLOUR if caught else self.UNREGISTERED_COLOUR
            id = PokemonManager.get_id_by_name(pokemon)
            image = self._im.get_image("pokemon/{}/".format(colour), id)
            self.create_image(cell_width * (i // rows + 0.5),
                              (i % rows) * cell_height, image=image,
                              anchor=tk.N)


class PlayerView(tk.Canvas):
    """
    Gives an overview of the player and all the pokemon they have caught.
    """

    def __init__(self, master, image_manager, player: model.Player, sprite_id,
                 columns, *args, cell_width=CELL_WIDTH, cell_height=CELL_HEIGHT,
                 **kwargs):
        """
        Constructor

        PlayerView.__init__(PlayerView, Player, int)
        """

        self._player = player
        self._sprite_id = sprite_id
        self._columns = columns
        self._im = image_manager
        self._cell_width = cell_width
        self._cell_height = cell_height

        super().__init__(master, *args, **kwargs)

    def redraw(self):
        """
        Redraws the view.

        PlayerView.redraw(PlayerView) -> None
        """

        columns = self._columns
        row, column = 0, 0
        cell_width, cell_height = self._cell_width, self._cell_height

        player = self._player
        dex = player.get_dex()

        # draw player
        image = self._im.get_image("players/", self._sprite_id)
        self.create_image(column * cell_width, row * cell_height, image=image,
                          anchor=tk.NW)

        column += 1
        self.create_text(column * cell_width, row * cell_height,
                         text="\n{} caught all of these Pokémon!".format(
                             player.get_name()), anchor=tk.NW)

        # draw pokemon
        column = 0
        row += 1

        for i, pokemon in enumerate(player.get_pokemons()):
            name = pokemon.get_name()
            id = PokemonManager.get_id_by_name(name)
            image = self._im.get_image("pokemon/colour/", id)
            column_offset = i % columns
            row_offset = i // columns

            self.create_image((column + column_offset) * cell_width,
                              (row + row_offset) * cell_height, image=image,
                              anchor=tk.NW)

        row += row_offset

        self.configure(width=columns * cell_width,
                       height=(row + 1) * cell_height)


class PokemonApp(object):
    """
    Top level controller for Pokemon finding game.
    """
    WIDTH = 1024
    HEIGHT = 768

    def __init__(self, master, welcome_message=WELCOME_MESSAGE):
        """
        Constructor

        PokemonApp.__init__(tk.Tk)
        """
        master.title(TITLE)
        self._master = master
        self._sprites = ImageManager(IMAGE_MAPPINGS)

        self._player_view = None
        self._grid = GridView(master, self._sprites, width=self.WIDTH,
                              height=self.HEIGHT)
        self._grid.pack(expand=1, side=tk.LEFT)

        self._dex = DexView(master, self._sprites)

        # Welcome message
        self._grid.create_text(self.WIDTH // 2, 100,
                               text=welcome_message, font=('Helvetica', '24'))

        image = self._sprites.get_image("general/", "pikachu")
        self._grid.create_image(self.WIDTH // 2, 0, image=image, anchor=tk.N)

        self._images = {}

        self.add_menus()

        self._filename = None
        self._playing = False

        PokemonManager.init()

        self._model = model.Game()

##        self.load_game_file("game2.json")

        # bind arrow keys
        for event, direction in KEY_DIRECTIONS.items():
            # bind direction from this iteration
            callback = (lambda d: lambda ev: self.move(d, ev))(direction)
            self._master.bind("<" + event + ">", callback)

    def add_menus(self):
        """
        Adds menus to main window.

        PokemonApp.add_menus(PokemonApp) -> None
        """
        menubar = tk.Menu(self._master)
        self._master.config(menu=menubar)

        filemenu = tk.Menu(menubar)

        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Load Game from File",
                             command=self.load_game_file)
        filemenu.add_command(label="Load Game from URL",
                             command=self.load_game_url)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit)

        playermenu = tk.Menu(menubar)

        menubar.add_cascade(label="Player", menu=playermenu)
        playermenu.add_command(label="Set Name", command=self.set_name)
        playermenu.add_command(label="Set Sprite",
                               command=self.set_player_sprite)
        playermenu.add_separator()
        playermenu.add_command(label="Reset Pokemon",
                               command=self.reset_pokemon)
        playermenu.add_command(label="Skip Level",
                               command=self.advance_level)

    def advance_level(self):
        """
        Advances to the next level.
        """

        if self._model.get_level().is_complete():
            if self._model.start_next_level():  # game completed
                numLevels = len(self._model)
                messagebox.showinfo("Game Complete",
                                    "Congratulations, you've completed all {} level{}!".format(
                                        numLevels,
                                        '' if numLevels == 1 else 's'))

                self.show_player_summary()
            else:
                self.load_level()
        else:
            messagebox.showerror("Error",
                                 "You cannot skip to the next level until the current one is complete.")

    def show_player_summary(self):
        """
        Shows a summary of the player and what they've caught.

        PokemonApp.show_player_summary(PokemonApp) -> None
        """

        self._grid.pack_forget()
        self._dex.pack_forget()

        self._player_view = PlayerView(self._master, self._sprites,
                                       self._model.get_player(),
                                       self._grid._player_id,
                                       PLAYER_COLUMNS)
        self._player_view.redraw()
        self._player_view.pack()

        self._playing = False

    def check_complete(self):
        """
        Checks if the level/game is complete.

        PokemonApp.check_complete(PokemonApp) -> None
        """
        level = self._model.get_level()

        if self._model.get_level().is_complete():
            if not level.get_pokemons():
                if not self._complete_msg_shown:
                    self._complete_msg_shown = True
                    messagebox.showinfo("Level Complete",
                                        "You've completed the Pokedex for this {} level.".format(
                                            level.get_terrain()
                                        ))
                return self.advance_level()

            if not self._complete_msg_shown:
                self._complete_msg_shown = True
                answer = messagebox.askquestion("Level Complete",
                                                "You've completed the Pokedex for this {} level.\n"
                                                "Would you like to skip to the next level?".format(
                                                    level.get_terrain()
                                                ))
                if answer == messagebox.YES:
                    self.advance_level()

    def move(self, direction, ev=None):
        """
        Attempts to move player in direction.

        PokemonApp.move(PokemonApp, str, tk.Event) -> None
        """
        if not self._playing:
            return

        player = self._model.get_player()
        old_position = player.get_position()
        hit = self._model.move_player(direction)
        new_position = player.get_position()

        if old_position == new_position:
            return

        if isinstance(hit, model.Pokemon):
            self._grid.redraw_caught_pokemon(*new_position, hit)

            # update dex view
            self._dex.draw()

        # update in gui
        self._grid.draw_player_at(*new_position)

        self.check_complete()

    def load_level(self, level=None):
        """
        Loads current level into view components.

        PokemonApp.load_level(PokemonApp, Level) -> None
        """
        if not level:
            level = self._model.get_level()

        self._grid.load_level(level)
        self._dex.load_dex(level.get_dex(), level.get_size()[0],
                           CELL_WIDTH + 10)

        self._complete_msg_shown = False

        if level.is_complete():
            self._complete_msg_shown = True

            def show_message():
                answer = messagebox.askquestion("Level Complete",
                                                "You've already completed the Pokedex for this {} level.\n"
                                                "Would you like to skip to the next level?".format(
                                                    level.get_terrain()
                                                ))
                if answer == messagebox.YES or not level.get_pokemons():
                    self.advance_level()

            self._master.after(50, show_message)

    def load_game_url(self, url=None):
        """
        Loads a game from a url and begins play.

        PokemonApp.load_game_url(PokemonApp, str) -> None
        """

        # prompt user for file
        if not url:
            url = simpledialog.askstring("Game URL",
                                         "Please enter the URL for the game to load.",
                                         initialvalue=DEFAULT_LOAD_URL)

            if not url:
                return

        # attempt to init
        try:
            self._model.load_url(url)
        except InvalidGameFileError:
            messagebox.showerror("Invalid Game File",
                                 "The url {} could not be loaded.".format(url))
        except InvalidGameDataError:
            messagebox.showerror("Invalid Game Data",
                                 "The url {} does not contain valid game data.".format(
                                     url))
        else:
            self._filename = url
            self._start_game()

    def load_game_file(self, filename=None):
        """
        Loads a game from file and begins play.

        PokemonApp.load_game_file(PokemonApp, str) -> None
        """

        # prompt user for file
        if not filename:
            filename = filedialog. \
                askopenfilename(initialdir=os.getcwd(),
                                title="Game File",
                                filetypes=(("json files", "*.json"),))

            if not filename:
                return

        # attempt to init
        try:
            self._model.load_file(filename)
        except InvalidGameFileError:
            messagebox.showerror("Invalid Game File",
                                 "The file {} could not be loaded.".format(
                                     filename))
        except InvalidGameDataError:
            messagebox.showerror("Invalid Game Data",
                                 "The file {} does not contain valid game data.".format(
                                     filename))
        else:
            self._filename = filename
            self._start_game()

    def _start_game(self):
        """
        Starts the loaded game.

        PokemonApp._start_game(PokemonApp) -> None
        """

        self._master.title("{} - {}".format(self._filename, TITLE))
        if self._player_view is not None:
            self._player_view.pack_forget()
        self._grid.pack(expand=1, side=tk.LEFT)
        self._dex.pack(expand=1, fill=tk.Y, side=tk.LEFT)

        self._playing = True

        self._model.start_next_level()
        self.load_level()

        self.check_complete()

    def set_player_sprite(self):
        """
        Prompts the player to choose a sprite for their character.

        PokemonApp.set_player_sprite(PokemonApp) -> None
        """
        window = tk.Toplevel(self._master)
        players = tk.Canvas(window, width=PLAYER_COLUMNS * CELL_WIDTH,
                            height=PLAYER_ROWS * CELL_HEIGHT)
        players.pack()

        window.title("Choose Player")

        ct = CoordinateTranslator()

        im = self._sprites

        for id in PLAYER_IDS:
            row = id // PLAYER_COLUMNS
            column = id % PLAYER_COLUMNS
            x, y = ct.position_to_pixel_centre(row, column)
            image = im.get_image("players/", id)
            players.create_image(x, y, image=image)

        def setPlayer(ev=None):
            row, column = ct.get_row_column(ev.x, ev.y)
            id = row * PLAYER_COLUMNS + column

            if id in PLAYER_IDS:
                self._grid.set_player_id(id)

        window.bind("<Button-1>", setPlayer)

    def set_name(self, name=None):
        """
        Sets the name of the player, prompting if not given.

        PokemonApp.set_name(PokemonApp, str) -> None
        """

        if not name:
            name = simpledialog.askstring("Player Name",
                                          "Please enter your name.",
                                          initialvalue=self._model.get_player().get_name())

        if name:
            self._model.get_player().set_name(name)

    def reset_pokemon(self, name=None):
        """
        Resets the pokemon caught by the player.

        PokemonApp.reset_pokemon(PokemonApp, str) -> None
        """

        if self._playing:
            messagebox.showerror("Currently Playing",
                                 "Cannot reset Pokémon whilst playing a game!")
        else:
            self._model.get_player().reset_pokemons()

    def exit(self):
        """
        Exits the GUI.

        PokemonApp.exit(PokemonApp) -> None
        """

        self._master.destroy()


def main():
    root = tk.Tk()
    app = PokemonApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
