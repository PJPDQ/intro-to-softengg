#!/usr/bin/env python3
###################################################################
#
#   CSSE1001/7030 - Assignment 2
#
#   Student Username: s4397674
#
#   Student Name: Dicky Sentosa Gozali
#
###################################################################

###################################################################
#
# The following is support code. DO NOT CHANGE.

from a2_support import *

# End of support code
################################################################

# Write your code here

class GameObject(object):
    def __init__(self, name, position):
        """Constructor
        __init__(self, name, position)
        """
        self._name = name
        self._position = position

    def set_position(self, position):
        """Sets the position to position, which either is a cell position
        or None
        set_position(self, (int, int)) -> (int, int)
        """
        self._position = position

    def get_position(self):
        """returns the current position of the instance
        get_position(self) -> (int, int)
        """
        return self._position

    def set_name(self, name):
        """
        sets the name to name
        set_name(self, str) -> str
        """
        self._name = name

    def get_name(self):
        """
        returns the name of the instance
        get_name(self) -> str
        """
        return self._name

    def __str__(self):
        """
        Returns a human readable representation of this instance
        __str___(self) -> str{int, int}
        """
        return GAME_OBJECT_FORMAT.format(self._name, self._position)

class Pokemon(GameObject):
    def __init__(self, name, position, terrain):
        """Constructor
        __init__(self, name, position, terrain)
        """
        super().__init__(name, position)
        self._terrain = terrain

    def set_terrain(self, terrain):
        """
        Sets the terrain to terrain.
        set_terrain(self, str) -> str
        """
        self._terrain = terrain

    def get_terrain(self):
        """
        Returns the terrain of the instance.
        get_terrain(self) -> str
        """
        return self._terrain

    def __str__(self):
        """
        Returns a human readable representation of this instance.
        __str__(self) -> str{(int, int), str}
        """
        return POKEMON_FORMAT.format(self._name, self._position, self._terrain)

    def __repr__(self):
        return POKEMON_REPR_FORMAT.format(self._name, self._position, self._terrain)
   
class Player(GameObject):
    def __init__(self, name):
        """Constructor
        __init__(self, name)
        """
        super().__init__(name, None)
        self._pokencounter = Dex([])
        self._pokecaught = []

    def get_pokemons(self):
        """
        Returns a list of all Pokemon that this Player has caught, in
        the order they were caught
        get_pokemons(self) -> list
        """
        return self._pokecaught

    def get_dex(self):
        """
        Returns the Player's Dex
        get_dex(self) -> list
        """
        return self._pokencounter

    def reset_pokemons(self):
        """
        Resets all the Pokemon caught by this Player, including their Dex.
        reset_pokemons(self) -> str
        """
        self._pokencounter = Dex([])
        self._pokecaught = []

    def register_pokemon(self, pokemon):
        """
        Catches the pokemon and adds to the Player's Dex, where
        pokemon is a Pokemon, provided it is expected by the Player's
        Dex. Otherwise, this method should raise an UnexpectedPokemonError.
        register_pokemon(self, pokemon) -> None
        """
        self._pokencounter.register(pokemon.get_name())
        self._pokecaught.append(pokemon)

    def __str__(self):
        """
        Returns a human readable representation of this instance.
        __str__(self) -> str{(int, int), int}
        """
        return PLAYER_FORMAT.format(self.get_name(), super().get_position(),
                                    len(self._pokecaught))


class Wall(GameObject):
    pass

    def __repr__(self):
        return WALL_REPR_FORMAT.format('#')


class Dex(object):
    def __init__(self, pokemon_names):
        """Constructor
        __init__(self, pokemon_names)"""
        self._dex = {}
        self.expect_pokemons(pokemon_names)

    def expect_pokemons(self, pokemon_names):
        """
        Instructs the Dex to also expect all pokemon in the list of
        pokemon_names (that are not already expected).
        expect_pokemons(self, dictionary) -> None
        """
        for x in pokemon_names:
            if x in self._dex:
                continue
            else:
                self._dex[x] = False

    def expect_pokemons_from_dex(self, other_dex):
        """
        Instruct the Dex to also expect all pokemon that other_dex expects
        (that are not already expected)
        expect_pokemons_from_dex(self, dictionary) -> None
        """
        pokemon_names = []
        self._pkmlist = other_dex.get_pokemon()
        for poke in self._pkmlist:
            pokemon_names.append(poke[0])
        self.expect_pokemons(pokemon_names)
        
    def register(self, pokemon_name):
        """
        Registers the pokemon(name) in the Dex. Returns True if the pokemon was
        already registered, else False. This method raises an
        UnexpectedPokemonError if the pokemon is not expected by this Dex.
        register(self, list) -> str
        """
        if pokemon_name not in self._dex:
            raise UnexpectedPokemonError(pokemon_name +
                                         ' is not expected by this Dex')
        elif self._dex[pokemon_name] == False:
            self._dex[pokemon_name] = True
            return False
        else:
            self._dex[pokemon_name] = True
            return True
        

    def register_from_dex(self, other_dex):
        """
        Registers each pokemon from the another Dex, other_dex, provided it is
        expected by this Dex and registered in the other Dex. This method must
        never raise an UnexpectedPokemonError.
        register_from_dex(self, list) -> str
        """
        for pokemon in other_dex._dex:
            if pokemon in self._dex:
                if other_dex._dex[pokemon] == True:
                    self._dex[pokemon] = True

    def get_pokemons(self):
        """
        Returns a list of (name, registered) pairs for each pokemon expected
        by this Dex, where name is the name of the pokemon, and registered is
        True if the pokemon is registered, else False. This list must be sorted
        alphabetically by name.
        get_pokemon(self) -> list
        """
        pokecaught = []
        for pokemon in self._dex:
            poke = self._dex[pokemon]
            pokecaught.append((pokemon, poke))
        return sorted(pokecaught)
       
    def get_registered_pokemons(self):
        """
        Returns an alphabetically sorted list of names of pokemon registered in
        this Dex.
        get_registered_pokemons(self) -> list
        """
        pokeregistered = []
        for pokemon in self._dex:
            if self._dex[pokemon] == True:
                pokeregistered.append(pokemon)
        sorted(pokeregistered)
        return pokeregistered

    def get_unregistered_pokemons(self):
        """
        Returns an alphabetically sorted list of names of pokemon
        unregistered in, but expected by, this Dex.
        get_unregistered_pokemons(self) -> list
        """
        pokeunregistered = []
        for pokemon in self._dex:
            if self._dex[pokemon] == False:
                pokeunregistered.append(pokemon)
        sorted(pokeunregistered)
        return pokeunregistered
                              
    def __len__(self):
        """
        Returns the total number of pokemon expected by this Dex.
        __len__(self) -> int
        """
        return len(self._dex)

    def __contains__(self, name):
        """
        Returns True iff pokemon with name is registered in this Dex, else
        False.
        __contains__(self, name) -> str
        """
        return self._dex.get(name, False)

    def __str__(self):
        """
        Returns a human readable string representation of this Dex.
        __str__(self) -> str{int}
        """
        return DEX_FORMAT.format(len(self.get_registered_pokemons()),
                                 ", ".join(self.get_registered_pokemons()),
                                 len(self.get_unregistered_pokemons()),
                                 ", ".join(self.get_unregistered_pokemons()))

class Level(object):
    def __init__(self, player, data):
        """Constructor
        __init__(self, Player, data)"""
        self._player = player
        self._data = data
        self._wall = {}
        self._poke = {}
        poke = []
        self._lvldex=Dex([])
        for var in self._data.get('pokemons'):
            position = var.get('position')
            pokemon = var.get('name')
            self._poke[position] = Pokemon(pokemon, position,
                                           self._data.get('terrain'))
            poke.append(pokemon)
        self._player.get_dex().expect_pokemons(poke)
        self._lvldex.expect_pokemons(poke)
        for var in self._data.get('walls'):
            position = var
            self._wall[position] = None
        rows = self._data.get('rows')
        columns = self._data.get('columns')
        for row in range(0, rows):
            self._wall[(row, -0.5)] = None 
            self._wall[(row, columns - 0.5)] = None 
        for column in range(0, columns):
            self._wall[(-0.5, column)] = None 
            self._wall[(rows-0.5, column)] = None 
            
        
    def get_size(self):
        """
        Returns the size of the level grid.
        get_size(self) -> int
        """
        row = self._data.get('rows')
        column = self._data.get('columns')
        return (row, column)
    
    def get_terrain(self):
        """
        Returns the terrain type of this level.
        get_terrain(self) -> str
        """
        terrain = self._data.get('terrain')
        return terrain

    def get_dex(self):
        """
        Returns the Dex for this level.
        get_dex(self) -> dictionary
        """
        return self._lvldex
    
    def get_starting_position(self):
        """
        Returns the player's starting position for this level.
        get_starting_position(self) -> (int, int)
        """
        position = self._data.get('player')
        return position

    def is_obstacle_at(self, position):
        """
        Returns True iff an obstacle exists at given position, else False.
        is_obstacle_at(self, position) -> (int, int)
        """
        if position in list(self._wall.keys()):
            return True
        else:
            return False

    def get_obstacles(self):
        """
        Returns a list of positions of all obstacles (walls) that exist in
        this level, including boundary walls.
        get_obstacles(self) -> list
        """
        return list(self._wall.keys())
    
    def get_pokemons(self):
        """
        Returns a list of all Pokemon that exist in this level.
        get_pokemons(self) -> list
        """
        pokemon = []
        for poke in self._poke.values():
            pokemon.append(poke)
        return pokemon

    def get_pokemon_at(self, position):
        """
        Returns the Pokemon that exists at the given position, else None.
        get_pokemon_at(self, (int, int)) -> Pokemon
        """
        if position in list(self._poke.keys()):
            return self._poke.get(position)
        else:
            return None


    def catch_pokemon_at(self, position):
        """
        Catches and returns the Pokemon that exists at the given position.
        If no pokemon exists at the given position, this method raises an
        InvalidPositionError.
        catch_pokemon_at(self, position) -> Pokemon
        """
        if position not in self._poke:
            raise InvalidPositionError()
        else:
            self._player.register_pokemon(self._poke.get(position))
            self._lvldex.register_from_dex(self._player.get_dex())
            x = self._poke.pop(position)
            return x
            
    def is_complete(self):
        """
        Returns True iff this Level is complete, else False.
        is_complete(self) -> str
        """
        if len(self._poke) == 0:
            return True
        else:
            return False


class Game(object):
    def __init__(self):
        """Constructor
        __init__()"""

        self._player = Player(DEFAULT_PLAYER_NAME)
        self._levels = []
        self._game_data = {}
        self._currentlvl ={}
##        self._lvldex = Level(self._player, self._currentlvl).get_dex()
        
    def load_file(self, game_file):
        """
        Loads a game from a file, given by game_file, using load_game_file
        from the support file.
        load_file(self, str) -> file
        """
        self._game_data = load_game_file(game_file)
        self._currentlvl = None
        for level_data in self._game_data['levels']:
                level = Level(self._player, level_data)
                self._levels.append(level)

    def load_url(self, game_url):
        """
        Loads a game from url, given by game_url, using load_game_url from
        the support file.
        load_game_url(str) -> file
        """
        self._game_data = load_game_url(game_url)
        self._currentlvl = None
        for level_data in self._game_data['levels']:
                level = Level(self._player, level_data)
                self._levels.append(level)
        
    def start_next_level(self): 
        """
        Attempts to start the next level of the game. Return True iff
        the game is completed, else False. This method should raise an
        InvalidPositionError if the level contains any invalid positions.
        start_next_level(self) -> str
        """
        if len(self._levels) == 0 and self.get_level().is_complete():
            return True
        else:
            self._currentlvl = self._levels.pop(0)
##            self._currentlvl.register_from_dex(self._player.get_dex())
##            self._player.get_dex().expect_pokemons(self._lvldex)
##            self._player.register_pokemon(self._lvldex)

            self._player.set_position(self.get_level().get_starting_position())
            return False

    def get_player(self):
        """
        Returns the player of the game.
        get_player(self) -> str
        """
        return self._player

    def get_level(self):
        """
        Returns the current level, an instance of Level, else None
        if the game hasn't started.
        get_level(self) -> int
        """
        return self._currentlvl
                    
    def __len__(self):
        """
        Returns the total number of levels in the game.
        __len__(self) -> int
        """
        return len(self._game_data['levels'])

    def is_complete(self):
        """
        Returns True iff no level remain incomplete, else False.
        is_complete(self) -> str
        """
        if len(self._levels) == 0:
            return True
        else:
            return False
        
    def move_player(self, direction):
        """
        Attempts to move the player in the given direction. Returns whatever
        the player would hit (an instance of GameObject) in attempting to move,
        else None. If direction is not one of NORTH, EAST, SOUTH, WEST,
        this method raises a DirectionError.
        move_player(self, direction) -> None
        """
        pastpos = self._player.get_position()
        if pastpos == None:
            pastpos = self._currentlvl.get_starting_position()
        else:
            pastpos = self._player.get_position()

        if direction in DIRECTIONS:
            x, y = pastpos
            directionx, directiony = DIRECTION_WALL_DELTAS.get(direction)
            newpos = (x+directionx, y+directiony)
               ## check for the wall:
            if newpos in self._currentlvl.get_obstacles():
                return Wall(self._player, newpos)
            elif newpos not in self._currentlvl.get_obstacles():
                ## move
                x1, y1 = newpos
                newpos1 = (x1+directionx, y1+directiony)
                self._player.set_position(newpos1)
                ## check for pokemon
                if self._currentlvl.get_pokemon_at(newpos1) != None:
                    return self._currentlvl.catch_pokemon_at(newpos1)
                else:
                    return None
        ##handle invalid directions
        else:
            raise DirectionError()
                    
                        


if __name__ == "__main__":
     import gui
     gui.main()

