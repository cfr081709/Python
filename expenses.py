import time
import matplotlib.pyplot as plt
import sys

def get_float_input(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("Invalid input. Please enter a non-negative number.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def print_with_delay(message, delay=3):
    print(message)
    time.sleep(delay)

moneymade = get_float_input("How much money did you make this year: ")
if moneymade == 0:
    print("Error: Income cannot be zero. Exiting program. Reinitialize the program.")
    time.sleep(5)
    sys.exit()

onlineshmoney = get_float_input("How much money did you spend online shopping this year: ")
inpersonmoney = get_float_input("How much money did you spend in person shopping this year: ")
restraunt = get_float_input("How much money did you spend on restaurants this year: ")
need = get_float_input("How much money did you spend on needs this year: ")
saving = get_float_input("How much money did you save this year: ")

while True:
    kids = input("Do you have kids (y/n): ").strip().lower()
    kidmoney = 0
    if kids == "y":
        kidmoney = get_float_input("How much money did you spend on your kids this year: ")
        break
    elif kids == "n":
        break
    else:
        print("Invalid input. Please enter 'y' or 'n'.")
        time.sleep(2)

totalspent = onlineshmoney + inpersonmoney + restraunt + need + kidmoney
percentspentonline = onlineshmoney / moneymade * 100
percentspentinperson = inpersonmoney / moneymade * 100
percentrestraunt = restraunt / moneymade * 100
percentneed = need / moneymade * 100
percentkidmoney = (kidmoney / moneymade * 100) if kids == "y" else 0
percentsaved = saving / moneymade * 100

if totalspent > moneymade:
    print_with_delay("Warning: You spent more than you made this year by -$" + str(totalspent - moneymade))
else:
    print_with_delay("You spent within your means this year, and saved " + str(percentsaved) + "% of your income.")

print_with_delay("You made: $" + str(moneymade))
print_with_delay("You spent: $" + str(totalspent))
print_with_delay("Net Income: $" + str(moneymade - totalspent))
print_with_delay("You saved: " + str(percentsaved) + "% of your income.")
print_with_delay("You spent " + str(percentspentonline) + "% of your income on online shopping.")
print_with_delay("You spent " + str(percentspentinperson) + "% of your income on in person shopping.")
print_with_delay("You spent " + str(percentrestraunt) + "% of your income on restaurants.")
print_with_delay("You spent " + str(percentneed) + "% of your income on needs.")
if kids == "y":
    print_with_delay("You spent " + str(percentkidmoney) + "% of your income on your kids.")
else:
    print_with_delay("N/A")

graphyn = input("Do you want to see a graph of your spending? (y/n): ")

if graphyn == "y":
    categories = ['Online Shopping', 'In Person Shopping', 'Restaurants', 'Needs']
    values = [percentspentonline, percentspentinperson, percentrestraunt, percentneed]
    colors = ['blue', 'orange', 'green', 'red']

    if kids == "y":
        categories.append('Kids')
        values.append(percentkidmoney)
        colors.append('purple')

    plt.figure(figsize=(10, 5))
    graph_type = input("Choose graph type - bar or pie (default is bar): ").strip().lower()

    if graph_type == "pie":
        plt.pie(
            values, 
            labels=categories, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=colors, 
            textprops={'color': 'white'}
        )
        plt.title('Breakdown of Spending this Year')
    elif graph_type == "bar":
        plt.bar(categories, values, color=colors)
        plt.ylabel('Percentage of Income (%)')
        plt.title('Breakdown of Spending this Year')
        plt.ylim(0, max(values) + 10)
        plt.xticks(rotation=45)
        plt.tight_layout()
    else:
        print_with_delay("Invalid graph type. Defaulting to bar chart.")
        plt.bar(categories, values, color=colors)
        plt.ylabel('Percentage of Income (%)')
        plt.title('Breakdown of Spending this Year')
        plt.ylim(0, max(values) + 10)
        plt.xticks(rotation=45)
        plt.tight_layout()

    plt.show()
else:
    print_with_delay("N/a")

exit = input("Thank you for using the expenses tracker! Would you like to quit the program? (y/n): ").strip().lower()
if exit == "y":
    print("Exiting program. Goodbye!")
    sys.exit()
else:
    print("Program will now terminate.")
    sys.exit()