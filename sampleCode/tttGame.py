import random

def displayInitialMenu():
    print('1. play tic tac toe')
    print('2. quit')
    users_choice = int(input('choice: '))
    print()
    return users_choice

def print_board(b):
    for row in b:
        print(row)
    print()

def computer_pick_move(b, chosen, letter):
    computers_position = random.randint(1,9)
    while computers_position in chosen:
         computers_position = random.randint(1,9)
         
    assign_position(b, letter, computers_position, chosen)
    return computers_position

def user_pick_move(b, chosen, letter):
    users_position = int(input('choose position: '))
    while users_position < 1 or users_position > 9 or users_position in chosen:
        users_position = int(input('invalid, choose again: '))
    assign_position(b, letter, users_position, chosen)

def assign_position(b, letter, position, chosen):
        row_number = (position-1) // 3
        col_number = (position-1) % 3
        b[row_number][col_number] = letter
        chosen.append(position)

def winner(b, chosen):
    for letter in ['x','o']:
        # check rows
        for row in b:
            if row == [letter,letter,letter]:
                return letter
        
        # check columns
        for column in range(0,3):
            for row in range(len(b)):
                if b[row][column] != letter:
                    break
                if row == len(b) - 1:
                    return letter
        
        # check upper left to lower right diagonal
        for column in range(len(b[0])):
            if b[column][column] != letter:
                break
            if column == len(b[0]) - 1:
                return letter

        # check upper right to lower left diagonal
        for row in range(len(b)):
            if b[row][len(b) - 1 - row] != letter:
                break
            if row == len(b) - 1:
                return letter
            
    if len(chosen) == len(b) * len(b[0]):
        return 'tie'
    
    return 'no winner yet'

def ttt():
    board = [ ['1','2','3'],
              ['4','5','6'],
              ['7','8','9']  ]
    
    chosen_positions = []

    # ask user to choose letter
    user_letter = input('Would you like to be "x" or "o" ? ')
    while user_letter not in ['x','o']:
        user_letter = input('I said "x" or "o", choose: ')
        
    # computer is assigned the other letter
    if user_letter == 'x' : 
        computer_letter = 'o'
    else:
        computer_letter = 'x'
        
    # If the computer is 'x' then the computer picks the first move
    if computer_letter == 'x':
        computer_pick_move(board, chosen_positions, computer_letter)
    
    print_board(board)

    while winner(board, chosen_positions) == 'no winner yet':
        # get the user's move
        user_pick_move(board, chosen_positions, user_letter)
        
        print()
        
        if winner(board, chosen_positions) == 'no winner yet':
            # computer picks a move
            computer_pick_move(board, chosen_positions, computer_letter)
                                                            
        print_board(board)        
    
    who_won = winner(board, chosen_positions)
    if who_won == 'tie':
        print('tie game')
    else:
        print(who_won, "won.")
    print()

def main():
    choice = displayInitialMenu()
   
    # main loop to choose if the user wants to play or quit
    while(choice != 2):
        ttt()
        choice = displayInitialMenu()
        
        
        
        