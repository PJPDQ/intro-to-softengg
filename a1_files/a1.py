#!/usr/bin/env python3
###################################################################
#
#   CSSE1001/7030 - Assignment 1
#
#   Student Username: s4397674
#
#   Student Name: Dicky Sentosa Gozali
#
###################################################################

###################################################################
#
# The following is support code. DO NOT CHANGE.

from a1_support import *
def get_position_in_direction(position, direction):
    """
    takes a row, column pair representing a position and a direction character
    'n' = 'north'
    's' = 'south'
    'e' = 'east'
    'w' = 'west'
    returns the position of the adjacent square in the given direction.
    get_position_in_direction(tuple(int, int), str) -> (int, int)
    """
    position = list(position)
    
    if direction =='n':
        position[0]=position[0]-1
    elif direction =='s':
        position[0]+=1
    elif direction =='w':
        position[1]=position[1]-1
    elif direction =='e':
        position[1]+=1
    return tuple(position)

def print_maze(maze, position):
    """
    takes a maze string and the position of the player
    print the maze with the player shown as an 'A'.
    print_maze(str, (int, int)) -> maze
    """ 
    user_in_maze = position_to_index(position, maze_columns(maze))

    print (maze[:user_in_maze] + 'A' + maze[user_in_maze+1:])
            
def move(maze, position, direction):
    """
    takes a maze string, a position of a square and a direction.
    returns a pair of form (position, square) where position is the position
    after the move and square is the resulting square after the move.
    Pre-condition: if move is invalid, the new position returned is the same as the old position.
    move(str, (int, int), str) -> ((int, int), str)
    """
    x, y = get_position_in_direction(position, direction)
    user_in_maze = position_to_index((x,y), maze_columns(maze))
    if maze[user_in_maze] != "#":
        return ((x, y), maze[user_in_maze])
    else:
        return (position, maze[user_in_maze])

def get_legal_directions (maze, position):
    """
    takes a maze string and a position
    returns a list of legal direction for that square
    get_legal_directions(str, (int, int)) -> [str, str]
    """
    directions = ()
    legal_directions = []
    for directions in ['n', 's', 'e', 'w']:
        x, y = get_position_in_direction(position, directions)
        user_in_maze = position_to_index((x,y), maze_columns(maze))
        if maze[user_in_maze] != '#':
            legal_directions.append(directions)
    return legal_directions

def interact():
    # Add your code for interact here
    """
    handles user input
    interact() -> None
    """
    maze = load_maze(input("Maze File: "))
    history = [START_POSITION]
    
    while maze != None:
        print()
        print_maze(maze,history[-1])
        print()
        command = input("Command: ").strip().lower()
        if command in DIRECTIONS:
            position, direction = move(maze, history[-1], command)
            if direction == '#':
                print ("You can't go in that direction.")
            elif direction in BAD_POKEMON:
                print(LOSE_TEXT.format(POKEMON[direction]))
                break
            elif direction == GOOD_POKEMON:
                print(WIN_TEXT.format(POKEMON[direction]))
                break
            elif direction == ' ':
                history.append(position)
        elif command == 'r':
            history = [START_POSITION]
        elif command =='b':
            if len(history) > 1:
                history.pop()
            else:
                print("You cannot go back from the beginning.")
        elif command == '?':
            print(HELP_TEXT)
        elif command == 'p':
            legal = get_legal_directions(maze, history[-1])
            i = ", ".join(legal)
            print("Possible directions: "+ i)
        elif command == 'q':
            var = input("Are you sure you want to quit? [y] or n: ")
            if var == 'n':
                continue
            else:
                break
        else:
            print("Invalid command: " + command)
           

# End of support code
################################################################


##################################################
# !!!!!! Do not change (or add to) the code below !!!!!
# 
# This code will run the interact function if
# you use Run -> Run Module  (F5)
# Because of this we have supplied a "stub" definition
# for interact above so that you won't get an undefined
# error when you are writing and testing your other functions.
# When you are ready please change the definition of interact above.
###################################################

if __name__ == '__main__':
    interact()
