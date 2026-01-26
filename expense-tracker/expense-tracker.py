import json
import os

def load_expenses(filename="expenses.json"):
    if not os.path.exists(filename):
        return []

    try:
        with open(filename, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_expenses(expenses, filename="expenses.json"):
    with open(filename, "w") as file:
        json.dump(expenses, file, indents=4)


"""This function is to add the expenses."""
def add_expense(expenses):
    amount = float(input("Enter amount: "))
    category = input("Enter category: ")
    description = input("Enter description: ")

    expense = {
        "amount": amount,
        "category": category,
        "description": description
    }

    expenses.append(expense)
    save_expenses(expenses)
    print("Expenses have been added.\n")

"""This function is to view added expenses."""
def view_expenses(expenses):
    if not expenses:
        print("No expenses recorded.\n")
        return
    for i, expense in enumerate(expenses, start=1):
        print(f"{i}. £{expense['amount']} - {expense['category']} - {expense['description']}")

"""Shows the total amount of expenses"""
def total_expenses(expenses):
    total = sum(expense["amount"] for expense in expenses )
    print(f"Total spent: £{total:.2f}\n")

def main():
    expenses = load_expenses()

    while True:
        print("Expense Tracker")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. View Total")
        print("4. Exit")

        try:
            choice = int(input("Choose an option: "))
        except ValueError:
            print("Please enter a number.\n")
            continue

        if choice == 1:
            add_expense(expenses)
        elif choice == 2:
            view_expenses(expenses)
        elif choice == 3:
            total_expenses(expenses)
        elif choice == 4:
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.\n")

if __name__ == "__main__":
    main()