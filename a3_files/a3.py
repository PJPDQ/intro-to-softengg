#!/usr/bin/env python3
################################################################################
#
#   CSSE1001/7030 - Assignment 3
#
#   Student Username: s4397674
#
#   Student Name: Dicky Sentosa Gozali
#
################################################################################

# VERSION 1.0.0

################################################################################
#
# The following is support code. DO NOT CHANGE.

from a3_support import *


# End of support code
################################################################################
# Write your code below
################################################################################

# Write your classes here (including import statements, etc.)
from tkinter import messagebox
import tkinter.ttk as ttk
import time
##import winsound

## TASK 1
class SimpleTileApp(object):
    def __init__(self, master):
        """
        Constructor(SimpleTileApp, tk.Frame)
        """
        master.title('Simple Tile Game')
        self._master = master

        self._game = SimpleGame()

        self._game.on('swap', self._handle_swap)
        self._game.on('score', self._handle_score)


        self._player = SimplePlayer()
        self.setup_ui()

        self._reset_button = tk.Button(master, text='Reset', command=self.reset)
        
        self._reset_button.pack(side=tk.BOTTOM, expand=True)
        self.menu()
        
    def menu(self):
        menubar =tk.Menu(self._master)
        self._master.config(menu=menubar)

        filemenu = tk.Menu(menubar)
        menubar.add_cascade(label='File', menu=filemenu)

        filemenu.add_command(label='New Game', command=self.new_game)
        filemenu.add_command(label='Exit', command=self.exit)
        self._filename = None

    def setup_ui(self):
        self._grid_view = TileGridView(self._master, self._game.get_grid(),\
                                       width=GRID_WIDTH, height=GRID_HEIGHT, bg='black')
        self._grid_view.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self._status_bar = SimpleStatusBar(self._master, self._player)
        self._status_bar.pack(expand = True)

    def new_game(self):
        if self._grid_view.is_resolving() == False:
            self._game.reset()
            self._grid_view.draw()
        else:
            messagebox.showerror('Error', 'Resolving is in progress!')
            # show message
    def exit(self):
        self._master.destroy()

    def reset(self): ## reset function??
        if self._grid_view.is_resolving() == False:
            self._player.reset_score()
            self._player.reset_swaps()
            self._status_bar.update_swaps()
            self._status_bar.update_score()
        else:
            messagebox.showerror('Error', 'Resolving is in progress!')
            # show message

    def _handle_swap(self, from_pos, to_pos):
        """
        Run when a swap on the grid happens.
        """
        self._player.record_swap()
        self._status_bar.update_swaps()
        print(
            "SimplePlayer made a swap from {} to {}!".format(from_pos, to_pos))

    def _handle_score(self, score):
        """
        Run when a score update happens.
        """
        self._player.add_score(score)
        self._status_bar.update_score()
        print("SimplePlayer scored {}!".format(score))

class SimplePlayer(object):
    def __init__(self):
        """"
        Constructs the player
        """
        self._score = 0
        self._swaps = 0
        

    def add_score(self, score):
        """
        Adds a score to the player's score. Returns the player's new score.
        add_score(int) -> int
        """
        self._score = self._score + score
        return self._score

    def get_score(self):
        """
        Returns the player's score
        get_score() -> int
        """
        return self._score

    def reset_score(self):
        """
        Resets the player's score
        reset_score() -> None
        """
        score = 0
        self._score = score

    def record_swap(self):
        """
        Records a swap for the player. Returns the player's new swap count.
        record_swap() -> None
        """
        self._swaps += 1

    def get_swaps(self):
        """
        Returns the player's swap count.
        get_swaps() -> int
        """
        return self._swaps
        

    def reset_swaps(self):
        """
        Resets the player's swap count.
        reset_swaps() -> None
        """
        self._swaps = 0

class SimpleStatusBar(tk.Frame):
    def __init__(self, master, player):
        """
        Construct the Player's status
        """
        super().__init__(master)
        
        self._player = player

        self._score = tk.Label(self, text = SCORE_FORMAT.format(0))
        self._score.pack(side = tk.LEFT, padx = 10)
        
        self._swaps = tk.Label(self, text = SWAPS_FORMAT.format(self._player.get_swaps(), ''))
        self._swaps.pack(side=tk.RIGHT, padx = 10)
    
    def update_swaps(self):
        if self._player.get_swaps() == 1:
            self._swaps.config(text = SWAPS_FORMAT.format(self._player.get_swaps(), ''))
        else:
            self._swaps.config(text = SWAPS_FORMAT.format(self._player.get_swaps(), 's'))
    
    def update_score(self):
        tot_score = 0                            
        if self._player.get_score() == tot_score:
            self._score.config(text = SCORE_FORMAT.format(tot_score))
        else:
            tot_score += self._player.get_score()
            self._score.config(text = SCORE_FORMAT.format(tot_score))

## TASK 2
class Character:
    def __init__(self, max_health):
        """
        Constructs the character, where max_health is an integer
        representing the maximum amount of the player can have, and
        the amount of health they start with.
        """
        self._max_health = max_health
        self._current_health = max_health

    def get_max_health(self):
        """
        Returns the maximum health the player can have.
        get_health() -> int
        """
        return self._max_health

    def get_health(self):
        """
        Returns the player's current health.
        get_health() -> int
        """
        return self._current_health

    def lose_health(self, amount):
        """
        Decreases the player's health by amount. Health cannot go below zero
        lose_health(int) -> None
        """
        if self._current_health - amount <= 0:
            self._current_health = 0
        else:
            self._current_health = self._current_health - amount

    def gain_health(self, amount):
        """
        Increases the player's health by amount. Health cannot go above
        maximum health
        gain_health(int) -> int
        """
        if self._current_health >= self._max_health:
            self._current_health
            return None
        else:
            self._current_health += amount

    def reset_health(self):
        """
        Resets the player's health to the maximum.
        reset_health() -> int
        """
        health = self._max_health
        self._current_health = health

class Enemy(Character):
    def __init__(self, type, max_health, attack):
        """
        Constructs the player, where type is the enemy's type, max_health is
        an integer representing the amount of health the enemy has, and
        attack is a pair of the enemy's attack range, (minimum, maximum).
        """
        super().__init__(max_health)
        self._enemy_health = ENEMY_BASE_HEALTH
        self._type = type
        self._attack = attack

    def get_type(self):
        """
        Returns the enemy's type.
        get_type() -> str
        """
        return self._type

    def attack(self):
        """
        Returns a random integer in the enemy's attack range.
        attack() -> list(int)
        """
        x, y = self._attack
        return random.randint(x, y)

class Player(Character):
    def __init__(self, max_health, swaps_per_turn, base_attack):
        """
        Constructs the player, where max_health is an integer representing
        the amount of health the player has, swaps_per_turn is an
        integer representing the number of swaps a player makes each turn,
        and base_attack is the player’s base attack.
        """
        super().__init__(max_health)
        self._player_health = PLAYER_BASE_HEALTH
        self._swaps_per_turn = swaps_per_turn
        self._base_attack = base_attack

    def record_swap(self):
        """
        Decreases the player’s swap count by 1, which cannot go below zero.
        Returns the player’s new swap count.
        record_swap(self) -> int
        """
        if self._swaps_per_turn <= 0:
            return 0
        x = self._swaps_per_turn-1
        self._swaps_per_turn = x
        return self._swaps_per_turn

    def get_swaps(self):
        """
        Returns the player's swap count.
        get_swaps() -> int
        """
        return self._swaps_per_turn

    def reset_swaps(self):
        """
        Resets the player's swap count to the maximum swap count.
        reset_swaps() -> int
        """
        self._swaps_per_turn = SWAPS_PER_TURN

    def attack(self, runs, defender_type):
        """
        Takes a list of Run instances and a defender type. Returns a pair
        of (type, damage), where attack is a list of pairs of the form
        (tile, damage), listing damage 6 amounts for each type,
        in the order the attacks should be performed.
        attack(list<Run>, str) -> [(str, int)]
        """
        damage =[]
        types = []
        
        for run in runs:
            typeclass = run.__getitem__(run.find_dominant_cell()).get_type()
            types.append(typeclass)
            max_length = run.get_max_dimension()
            length = run.__len__()
            plattack = self._base_attack
            number = types.count(typeclass)
            bonus = 1
            if number != 1:
                bonus = plattack*number
            else:
                bonus = 1
            tot_damage = length * max_length * plattack * bonus
            damage.append((typeclass, tot_damage))
        return damage
                   
        
class VersusStatusBar(tk.Frame):
    def __init__(self, master, player, enemy):
        """
        Construct the Player's status and Enemy's status
        """
        super().__init__(master)
        self._player = player
        self._enemy = enemy
     
        
        self._level = 1
        self._currentlvl = tk.Label(master, text = LEVEL_FORMAT.format(self._level))
        self._currentlvl.pack(side=tk.TOP, expand=True, fill = tk.BOTH)

        self._swaps = tk.Label(self, text = SWAPS_LEFT_FORMAT.format(
            self._player.get_swaps(), 's'))
        self._swaps.pack(anchor=tk.N, expand=True)
        
        self._player_health=tk.Label(master, text=HEALTH_FORMAT.format(PLAYER_BASE_HEALTH))
        self._player_health.pack(side=tk.LEFT)

        self._enemy_health=tk.Label(master, text=HEALTH_FORMAT.format(ENEMY_BASE_HEALTH))
        self._enemy_health.pack(side=tk.RIGHT)

    def change_enemy(self, new_enemy):
        self._enemy = new_enemy
        self.update_ehealth(0)

    def update_swaps(self):
        if self._player.get_swaps() <= 1:
            self._swaps.config(text = SWAPS_LEFT_FORMAT.format(
                self._player.get_swaps(), ''))
        else:
            self._swaps.config(text = SWAPS_LEFT_FORMAT.format(
                self._player.get_swaps(), 's'))

    def update_ehealth(self, amount):
        tot_health = self._enemy.get_max_health()
        if self._enemy.get_health() <= 0:
            self._enemy_health.config(text = HEALTH_FORMAT.format(tot_health))
        else:
            self._enemy.lose_health(amount)
            self._enemy_health.config(text = HEALTH_FORMAT.format(self._enemy._current_health))

    def update_phealth(self, amount):
        tot_health = self._player.get_max_health()
        if self._player.get_health() <= 0:
            self._player_health.config(text = HEALTH_FORMAT.format(tot_health))
        else:
            self._player.lose_health(amount)
            self._player_health.config(text = HEALTH_FORMAT.format(self._player._current_health))
    
    def update_level(self):
        self._level+=1
        self._currentlvl.config(text=LEVEL_FORMAT.format(self._level))
        self.reset()

    def reset(self):
        self._enemy.reset_health()
        self._player.reset_health()
        self._player.reset_swaps()

class ImageTileGridView(TileGridView):
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
        self.joey = tk.PhotoImage(file='150_c.gif')
        self.chandler = tk.PhotoImage(file='249_c.gif')
        self.ross = tk.PhotoImage(file='250_c.gif')
        self.rachel = tk.PhotoImage(file='380_c.gif')
        self.monica = tk.PhotoImage(file='381_c.gif')
        self.phoebe = tk.PhotoImage(file='487_c.gif')

        self._image = {'fire': self.joey, 'poison': self.chandler,
                       'water': self.ross, 'coin': self.rachel,
                       'psychic': self.monica, 'ice': self.phoebe}
        super().__init__(master, grid, width = GRID_WIDTH, height = GRID_HEIGHT, cell_width=GRID_CELL_WIDTH, cell_height = GRID_CELL_HEIGHT, bg='black')
        
        
    def draw_tile_sprite(self, xy_pos, tile, selected):
        """Draws the sprite for the given tile at given (x, y) position.

        TileGridView.undraw_tile_sprite(TileGridView, (int, int), Tile, bool)
                                                                    -> None"""

        width, height = self._calculate_tile_size(xy_pos, selected)
        x, y = xy_pos
        return self.create_image(x, y, image=self._image[tile.get_type()])

class SinglePlayerTileApp(SimpleTileApp):
    def __init__(self, master):
        """
        Constructor(SimpleTileApp, tk.Frame)
        """
        self._master = master
        self._level = 1
        
        self._master.title('Tile Game - ' + LEVEL_FORMAT.format(self._level))
        self._game = SimpleGame()
        self._plyr = SimplePlayer()
        self._player = Player(PLAYER_BASE_HEALTH, SWAPS_PER_TURN, PLAYER_BASE_ATTACK)
        self._enemy = self.create_enemy(self._level)
        

        self._player1 = tk.PhotoImage(file='hgss_127.gif')
        self._enemy1 = tk.PhotoImage(file='hgss_68.gif')
        
        self._player1Canvas = tk.Canvas(self._master, width=CHARACTER_WIDTH, height=CHARACTER_HEIGHT, bg = 'red')
        self._player1Canvas.create_image(100, 300, image=self._player1)
        self._player1Canvas.pack(side=tk.LEFT, pady=0, fill = tk.Y)

        self._enemy1Canvas= tk.Canvas(self._master, width=CHARACTER_WIDTH, height=CHARACTER_HEIGHT, bg = 'SpringGreen2')
        self._enemy1Canvas.create_image(100, 300, image = self._enemy1)
        self._enemy1Canvas.pack(side=tk.RIGHT, pady=0, fill = tk.Y)

        self.setup_ui()

        self._game.on("swap", self._handle_swap)
        self._game.on("run", self._handle_runs)
        self._game.on("swap_resolution", self._handle_swap_resolution)

        self.menu()

        
    def create_enemy(self, level):
        enemytype = WeightedTable(ENEMY_PROBABILITIES.items())
        enemy_health, enemy_attack = generate_enemy_stats(level)
        return Enemy(enemytype, enemy_health, enemy_attack)

    def next_level(self):
        self._level+=1
        self._enemy = self.create_enemy(self._level)
        self._versus_status.update_level()
        self._versus_status.change_enemy(self._enemy)
        self._master.title('Tile Game - ' + LEVEL_FORMAT.format(self._level))
        self._enemy_statusbar.config(value=self._enemy.get_max_health())
        
    def setup_ui(self):
        self._grid_view = ImageTileGridView(self._master, self._game.get_grid(), width=GRID_WIDTH, height=GRID_HEIGHT, bg ='PeachPuff2')
        self._grid_view.pack(side=tk.TOP, expand=True, fill=tk.Y)

        
        self._versus_status = VersusStatusBar(self._master, self._player, self._enemy)
        self._versus_status.pack(side=tk.BOTTOM, expand=True)
        
        self._player_statusbar = ttk.Progressbar(self._master, length=200, maximum = self._player.get_max_health(), orient=tk.HORIZONTAL, value=self._player.get_max_health())
        self._player_statusbar.pack(side=tk.LEFT, anchor=tk.SE)

        self._enemy_statusbar = ttk.Progressbar(self._master, length=200, maximum=self._enemy.get_max_health(), orient=tk.HORIZONTAL, value = self._enemy.get_max_health())
        self._enemy_statusbar.pack(side=tk.RIGHT, anchor=tk.SW)

    def statusbar(self):
        self._player_statusbar.config(value=self._player.get_health())
        self._enemy_statusbar.config(value=self._enemy.get_health())
        
    def new_game(self):
        """
        Initialize new game with reset tiles, level with no resolving
        """
        if self._grid_view.is_resolving() == False:
            self._game.reset()
            self._grid_view.draw()
            self.level = 1
            self.level = LEVEL_FORMAT.format(self.level)
        else:
            messagebox.showerror('Error', 'PIVOT!')

    def _handle_swap(self, from_cell, to_cell):
        """
        Run when a swap on the grid happens.
        """
        self._player.record_swap()
        self._versus_status.update_swaps()
        

    def _handle_swap_resolution(self, from_pos, to_pos):
        """
        Handles the resolution of a swap (after all runs have been resolved).

        Emits swap_resolution.

        SimpleGame._handle_swap_resolution(SimpleGame, (int, int), (int, int))
                                                                        -> None
        """
        if self._enemy.get_health() <= 0:
            self.next_level()
            messagebox.showinfo('You Defeated the Enemy!', 'THEY DO NOT KNOW THAT WE KNOW THEY KNOW WE KNOW')
        elif self._player.get_swaps() == 0:
            self._versus_status.update_phealth(self._enemy.attack())
            self._player.reset_swaps()
            self._versus_status.update_swaps()
            self.statusbar()
        else:
            return None
        
        
    def _handle_runs(self, runs):
        """
        Converts runs into score.

        Emits score, runs.

        SimpleGame._handle_runs(SimpleGame, int, list(Runs)) -> None
        """
        defender_type = self._enemy.get_type()
        damage = self._player.attack(runs, defender_type)
    
        for i in damage:
            self._versus_status.update_ehealth(i[1])
            self.statusbar()
 
    def exit(self):
        self._master.destroy()


##TASK 3
        

class StatusBar(tk.Frame):
    def __init__(self, master, player, enemy):
        """
        Construct the Player's status and Enemy's status
        """
        super().__init__(master)
        self._player = player
        self._enemy = enemy
     
        
        self._level = 1
        self._currentlvl = tk.Label(master, text = LEVEL_FORMAT.format(self._level))
        self._currentlvl.pack(side=tk.TOP, expand=True, fill = tk.BOTH)

        self._swaps = tk.Label(self, text = SWAPS_LEFT_FORMAT.format(
            self._player.get_swaps(), 's'))
        self._swaps.pack(anchor=tk.N, expand=True)
        
        self._player_health=tk.Label(master, text=HEALTH_FORMAT.format(PLAYER_BASE_HEALTH))
        self._player_health.pack(side=tk.LEFT)

        self._enemy_health=tk.Label(master, text=HEALTH_FORMAT.format(ENEMY_BASE_HEALTH))
        self._enemy_health.pack(side=tk.RIGHT)
        
    def change_enemy(self, new_enemy):
        self._enemy = new_enemy
        self.update_ehealth(0)

    def update_swaps(self):
        if self._player.get_swaps() <= 1:
            self._swaps.config(text = SWAPS_LEFT_FORMAT.format(
                self._player.get_swaps(), ''))
        else:
            self._swaps.config(text = SWAPS_LEFT_FORMAT.format(
                self._player.get_swaps(), 's'))

    def update_ehealth(self, amount):
        tot_health = self._enemy.get_max_health()
        if self._enemy.get_health() <= 0:
            self._enemy_health.config(text = HEALTH_FORMAT.format(tot_health))
        else:
            self._enemy.lose_health(amount)
            self._enemy_health.config(text = HEALTH_FORMAT.format(self._enemy._current_health))

    def update_phealth(self, amount):
        tot_health = self._player.get_max_health()
        if self._player.get_health() <= 0:
            self._player_health.config(text = HEALTH_FORMAT.format(tot_health))
            messagebox.showinfo('Over the line? You are so far past the line that you can not even see the line!',
                                'The line is a dot to you! - Friends Quote')
        else:
            self._player.lose_health(amount)
            self._player_health.config(text = HEALTH_FORMAT.format(self._player._current_health))

    def gain_phealth(self, amount):
        if self._player.get_health() < self._player.get_max_health():
            self._player_health.config(text = HEALTH_FORMAT.format(self._player.get_health()))
        else:
            self._player.gain_health(amount)
            self._player_health.config(text = HEALTH_FORMAT.format(self._player._current_health))


    def update_level(self):
        self._level+=1
        self._currentlvl.config(text=LEVEL_FORMAT.format(self._level))
        self.reset()

    def reset(self):
        self._enemy.reset_health()
        self._player.reset_health()
        self._player.reset_swaps()


class ImageTiles(TileGridView):
    def __init__(self, master, grid, *args, width=GRID_WIDTH,
                 height=GRID_HEIGHT,
                 cell_width=GRID_CELL_WIDTH, cell_height=GRID_CELL_HEIGHT,
                 background = 'black', **kwargs):
        """
        Constructor(tk.Frame, TileGrid, *, int, int, int, int, *)

        :param master: The tkinter master widget/window.
        :param width: Total width of the grid.
        :param height: Total height of the grid.
        :param cell_width: Width of each cell.
        :param cell_height: Height of each cell.
        """
        self.joey = tk.PhotoImage(file='Joey1.gif')
        self.chandler = tk.PhotoImage(file='Chandler1.gif')
        self.ross = tk.PhotoImage(file='Ross1.gif')
        self.rachel = tk.PhotoImage(file='Rachel1.gif')
        self.monica = tk.PhotoImage(file='Monica1.gif')
        self.phoebe = tk.PhotoImage(file='Phoebe1.gif')
        self._image = {'fire': self.joey, 'poison': self.chandler,
                       'water': self.ross, 'coin': self.rachel,
                       'psychic': self.monica, 'ice': self.phoebe}
        super().__init__(master, grid, width = GRID_WIDTH, height = GRID_HEIGHT, cell_width=GRID_CELL_WIDTH, cell_height = GRID_CELL_HEIGHT, bg='black')

    def draw_tile_sprite(self, xy_pos, tile, selected):
        """Draws the sprite for the given tile at given (x, y) position.
        TileGridView.undraw_tile_sprite(TileGridView, (int, int), Tile, bool)
                                                                    -> None"""
        width, height = self._calculate_tile_size(xy_pos, selected)
        x, y = xy_pos
        return self.create_image(x, y, image=self._image[tile.get_type()])
            
class MultiPlayerTileApp(SimpleTileApp):
    def __init__(self, master):
        """
        Constructor(SimpleTileApp, tk.Frame)
        """
        self._master = master
        self._level = 1
        self._max_level = 5
        self._master.title('Tile Game - ' + LEVEL_FORMAT.format(self._level))
        self._game = SimpleGame()
        self._plyr = SimplePlayer()
        self._player = Player(PLAYER_BASE_HEALTH, SWAPS_PER_TURN, PLAYER_BASE_ATTACK)
        self._enemy = self.create_enemy(self._level)

        self._player1 = tk.PhotoImage(file='Gunther.gif')
        self._enemy1 = tk.PhotoImage(file='Enemy1.gif')

        self._player1Canvas = tk.Canvas(self._master, width=CHARACTER_WIDTH, height=CHARACTER_HEIGHT, bg = 'orange2')
        self._player1Canvas.create_image(100, 300, image=self._player1)
        self._player1Canvas.pack(side=tk.LEFT, pady=0, fill = tk.Y)

        self._enemy1Canvas= tk.Canvas(self._master, width=CHARACTER_WIDTH, height=CHARACTER_HEIGHT, bg = 'navajo white')
        self._enemy1Canvas.create_image(100, 300, image = self._enemy1)
        self._enemy1Canvas.pack(side=tk.RIGHT, pady=0, fill = tk.Y)

        self._tile_collected = []

        self.setup_ui()
        self._background_music = tk.Button(self._master, text='Music off',
                                           bg = 'yellow', command=self.press_me)
        self._background_music.pack(side=tk.BOTTOM)
        self._Music = False
        
        self._game.on("swap", self._handle_swap)
        self._game.on("run", self._handle_runs)
        self._game.on("swap_resolution", self._handle_swap_resolution)
        self._game.on("score", self._handle_score)

        self.menu()
        
    def press_me(self):
        if self._Music == False:
            self._Music = True
            self._background_music.config(text='Music on')
            message.showinfo('I\'ll be there for you!', '\'Cos You\'will be there for me too')
            winsound.PlaySound('background sound.wav', winsound.SND_FILENAME)
        else:
            self._Music = False
            self._background_music.config(text='Music off')

    def create_enemy(self, level):
        enemytype = WeightedTable(ENEMY_PROBABILITIES.items())
        enemy_health, enemy_attack = generate_enemy_stats(level)
        return Enemy(enemytype, enemy_health, enemy_attack)

    def new_enemypic(self, level):
        enemy2 = tk.PhotoImage(file='Enemy2.gif')
        enemy3 = tk.PhotoImage(file='Enemy3.gif')
        enemy4 = tk.PhotoImage(file='Enemy4.gif')
        enemy5 = tk.PhotoImage(file='Enemy5.gif')
        enemy6 = tk.PhotoImage(file='Enemy6.gif')
        enemy7 = tk.PhotoImage(file='Enemy7.gif')

        self._image = {2: enemy2, 3: enemy3, 4: enemy4, 5: enemy5, 6: enemy6, 7: enemy7}
        self._enemy1Canvas.delete(tk.ALL)
        self._enemy1Canvas.create_image(100, 300, image= self._image.get(level))
        self._enemy1Canvas.update()
        
        
    def next_level(self):
        """
        Initialize the next following level with upgraded and new enemy.
        """
        self._level+=1
        self._enemy = self.create_enemy(self._level)
        self.new_enemypic(self._level)
        self._versus_status.update_level()
        self._versus_status.change_enemy(self._enemy)
        self._master.title('Tile Game - ' + LEVEL_FORMAT.format(self._level))
        self._enemy_statusbar.config(value=self._enemy.get_max_health())
        
    def setup_ui(self):
        self._grid_view = ImageTiles(self._master, self._game.get_grid(), width=GRID_WIDTH, height=GRID_HEIGHT, bg ='PeachPuff2')
        self._grid_view.pack(side=tk.TOP, expand=True, fill=tk.Y)

        
        self._versus_status = StatusBar(self._master, self._player, self._enemy)
        self._versus_status.pack(side=tk.BOTTOM, expand=True)
        
        self._player_statusbar = ttk.Progressbar(self._master, length=200, maximum = self._player.get_max_health(), orient=tk.HORIZONTAL, value=self._player.get_max_health())
        self._player_statusbar.pack(side=tk.LEFT, anchor=tk.SE)

        self._enemy_statusbar = ttk.Progressbar(self._master, length=200, maximum=self._enemy.get_max_health(), orient=tk.HORIZONTAL, value = self._enemy.get_max_health())
        self._enemy_statusbar.pack(side=tk.RIGHT, anchor=tk.SW)

    def statusbar(self):
        """
        Changes the status bar depending on the Player and Enemy health.
        """
        self._player_statusbar.config(value=self._player.get_health())
        self._enemy_statusbar.config(value=self._enemy.get_health())
        
    def new_game(self):
        """
        Initialize new game with reset tiles, level with no resolving
        """
        if self._grid_view.is_resolving() == False:
            self._game.reset()
            self._grid_view.draw()
            self.level = 1
            self.level = LEVEL_FORMAT.format(self.level)
        else:
            messagebox.showerror('Error', 'PIVOT!')
            
    def create_window(self):
        """
        Return a new window showing the end of the game.
        """
        t = tk.Toplevel(self._master)
        t.wm_title('Game Over')
        label = tk.Label(t, text='You just received Monica Apartment and Central Perk')
        label.pack(side=tk.TOP, fill=tk.X, ipadx=100)

        game_over = tk.PhotoImage(file='game over.gif')

        self._newcanvas = tk.Label(t, width= 100, height = 300, image=game_over, bg='DarkGoldenrod1')
        self._newcanvas.image = game_over
        self._newcanvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        
    def _handle_score(self, score):
        """
        Run when a score update happens.
        """
        if self._player.get_health() < self._player.get_max_health():
            int(self._player.gain_health(score/100))
            self.statusbar()
            int(self._versus_status.gain_phealth(score/100))

    def _handle_swap(self, from_cell, to_cell):
        """
        Run when a swap on the grid happens.
        """
        self._player.record_swap()
        self._versus_status.update_swaps()
        

    def _handle_swap_resolution(self, from_pos, to_pos):
        """
        Handles the resolution of a swap (after all runs have been resolved).

        Emits swap_resolution.

        SimpleGame._handle_swap_resolution(SimpleGame, (int, int), (int, int))
                                                                        -> None
        """
        if self._enemy.get_health() <= 0:
            messagebox.showerror('You WON!', 'How you Doin\'?')
            self.next_level()
            if self._level > 5:
                messagebox.showinfo('You are a natural!', 'Well-Played Phoebe Buffay Well-Played')
            elif self._level == self._max_level:
                self.create_window()
        elif self._player.get_swaps() == 0:
            self._versus_status.update_phealth(self._enemy.attack())
            self._player.reset_swaps()
            self.statusbar()
            self._versus_status.update_swaps()
        else:
            return None
    
        
    def _handle_runs(self, runs):
        """
        Converts runs into score.

        Emits score, runs.

        SimpleGame._handle_runs(SimpleGame, int, list(Runs)) -> None
        """
        defender_type = self._enemy.get_type()
        damage = self._player.attack(runs, defender_type)
        for run in runs:
            typeclass = run.__getitem__(run.find_dominant_cell()).get_type()
            self._tile_collected.append(typeclass)
            if self._tile_collected.count(typeclass) >= 5:
                self.Animation_Windows(typeclass)
        for i in damage:
            self._versus_status.update_ehealth(i[1])
            self.statusbar()

    def Animation_Windows(self, tile):
        """
        Return an animation GIF on another Canvas for each Tile Run collected.
        """
        animation = tk.Toplevel(self._master)
        animation.wm_title('AnimationGIF')
        label = tk.Label(animation, text='CONGRATULATIONS!', bg='red')
        label.pack(side=tk.TOP, fill=tk.X, ipadx=100)
        
        waterlist = ["water1.gif", "water2.gif", "water3.gif", "water4.gif",
                     "water5.gif", "water6.gif", "water7.gif", "water8.gif",
                     "water9.gif", "water10.gif", "water11.gif", "water12.gif",
                     "water13.gif", "water14.gif", "water15.gif", "water16.gif",
                     "water17.gif", "water18.gif", "water19.gif", "water20.gif",
                     "water21.gif", "water22.gif"]
        poisonlist = ["love1.gif", "love2.gif", "love3.gif", "love4.gif",
                        "love5.gif","love6.gif","love7.gif","love8.gif", "love9.gif"]
        firelist = ['pizza1.gif', 'pizza2.gif', 'pizza3.gif', 'pizza4.gif',
                    'pizza5.gif', 'pizza6.gif', 'pizza7.gif', 'pizza8.gif',
                    'pizza9.gif', 'pizza10.gif', 'pizza11.gif', 'pizza12.gif',
                    'pizza13.gif', 'pizza14.gif']
        psychiclist = ['unagi1.gif', 'unagi2.gif', 'unagi3.gif', 'unagi4.gif',
                       'unagi5.gif', 'unagi6.gif', 'unagi7.gif', 'unagi8.gif',
                       'unagi9.gif', 'unagi10.gif', 'unagi11.gif', 'unagi12.gif']
        coinlist = ['coin1.gif', 'coin2.gif', 'coin3.gif', 'coin4.gif', 'coin5.gif',
                    'coin6.gif', 'coin7.gif', 'coin8.gif', 'coin9.gif', 'coin10.gif',
                    'coin11.gif', 'coin12.gif', 'coin13.gif', 'coin14.gif', 'coin15.gif',
                    'coin16.gif', 'coin17.gif', 'coin18.gif', 'coin19.gif', 'coin20.gif',
                    'coin21.gif', 'coin22.gif', 'coin23.gif', 'coin24.gif', 'coin25.gif',
                    'coin26.gif', 'coin27.gif', 'coin28.gif', 'coin29.gif', 'coin30.gif',
                    'coin31.gif', 'coin32.gif', 'coin33.gif', 'coin34.gif', 'coin35.gif',
                    'coin36.gif', 'coin37.gif', 'coin38.gif', 'coin39.gif', 'coin40.gif',
                    'coin41.gif', 'coin42.gif', 'coin43.gif', 'coin44.gif', 'coin45.gif',
                    'coin46.gif', 'coin47.gif', 'coin48.gif', 'coin49.gif', 'coin50.gif']
        icelist = ['ice1.gif', 'ice2.gif', 'ice3.gif', 'ice4.gif', 'ice5.gif',
                   'ice6.gif', 'ice7.gif', 'ice8.gif', 'ice9.gif', 'ice10.gif']
        imagelist = {'fire': firelist, 'poison': poisonlist,
                       'water': waterlist, 'coin': coinlist,
                       'psychic': psychiclist, 'ice': icelist}
               
        tiles = tk.PhotoImage(file=imagelist.get(tile)[0])
        width = tiles.width()
        height = tiles.height()
        AnimationCanvas = tk.Canvas(animation, width=width, height=height)
        AnimationCanvas.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
 
        giflist=[]
        for imagefile in imagelist[tile]:
            photo=tk.PhotoImage(file=imagefile)
            giflist.append(photo)

        for i in range(0, 1000):
            for gif in giflist:
                AnimationCanvas.delete(tk.ALL)
                AnimationCanvas.create_image(width/2.0, height/2.0, image=gif)
                AnimationCanvas.update()
                time.sleep(0.1)

    def exit(self):
        """
        Exits the game from continuing
        """
        self._master.destroy()


def task1():
    # Add task 1 GUI instantiation code here
    root = tk.Tk()
    app = SimpleTileApp(root)
    root.mainloop()
def task2():
    # Add task 2 GUI instantiation code here
    root = tk.Tk()
    app = SinglePlayerTileApp(root)
    root.mainloop()
def task3():
    # Add task 3 GUI instantiation code here
    root = tk.Tk()
    app = MultiPlayerTileApp(root)
    root.mainloop()


def main():
    # Choose relevant task to run
    task1()
##    task2()
##    task3()
if __name__ == '__main__':
   main()


