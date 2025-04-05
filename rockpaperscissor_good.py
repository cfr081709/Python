import time
import random

player_name = input("Hello, pleaese enter your name: ")
print(f"Welcome, {player_name}!")
x = 1

if 1 == x:
    print("Let's play Rock, Paper, Scissors!")
    time.sleep(1)

# Get player's choice
    player_choice = input("Please choose rock, paper, or scissors: ").lower()

# Validation of player's choice
    if player_choice not in ["rock", "paper", "scissors"]:
        print("Invalid choice. Please try again.")
    else:
        print("Good Choice!")
        time.sleep(1)

# Get computer's choice
    computer_choice = random.choice(["rock", "paper", "scissors"])

# Winner determination
    if player_choice == computer_choice:
        print(f"Both chose {player_choice}. It's a tie!")
    elif (player_choice == "rock" and computer_choice == "scissors") or \
         (player_choice == "paper" and computer_choice == "rock") or \
         (player_choice == "scissors" and computer_choice == "paper"):
        print(f"You chose {player_choice} and the computer chose {computer_choice}. You win!")
    else:
        print(f"You chose {player_choice} and the computer chose {computer_choice}. You lose!")

continue_game = input("Do you want to play again? (yes/no): ").lower()
if continue_game == "yes":
    print("Great! Let's play again.")
if continue_game == "no":
    print("Thanks for playing! Goodbye!")
    x = 0