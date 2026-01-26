from datetime import datetime, timezone
import json
import os

# Function to load from a .json file.
def load_expenses(filename="expenses.json"):
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            json.dump([], file)
        return []

    with open(filename, "r") as file:
        content = file.read().strip()
        if not content:
            return []

        try:
            data = json.loads(content)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return []
# Save to said .json file.
def save_expenses(expenses, filename="expenses.json"):
    with open(filename, "w") as file:
        json.dump(expenses, file, indent=4)

# Formating the time stamp to look more user friendly.
def format_timestamp(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        local_dt = dt.astimezone()
        return local_dt.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return ts

# Safer code for validating inputs.
def get_valid_amount():
    while True:
        user_input = input("Enter amount: ").strip()

        try:
            amount = float(user_input)

            if amount <=0:
                print("Amount must be greater than zero.\n")
                continue
            
            return round(amount, 2)
       
        except ValueError:
            print("Please enter a valid number (e.g. 12.50).\n")


def get_non_empty_input(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty.\n")

# This function is to add the expenses.
def add_expense(expenses):
    amount = get_valid_amount()
    category = get_non_empty_input("Enter category: ")
    description = get_non_empty_input("Enter description: ")
    expense = {
        "amount": amount,
        "category": category,
        "description": description,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    expenses.append(expense)
    save_expenses(expenses)
    print("Expenses have been added.\n")

# This function is to view added expenses.
def view_expenses(expenses):
    if not expenses:
        print("No expenses recorded.\n")
        return
    
    for i, expense in enumerate(expenses, start=1):
        ts = format_timestamp(expense.get("timestamp", ""))
        print(f"{i}. £{expense['amount']:.2f} - {expense['category']} - {expense['description']} - {ts}")

    print()
# This function is to delete expenses
def delete_expense(expenses):
    if not expenses:
        print("No expenses to delete.\n")
        return

    view_expenses(expenses)

    try:
        choice = int(input("Enter the number of the expense to delete: "))

        if 1 <= choice <= len(expenses):
            confirm = input("Are you sure you want to delete this expense? (Y/N): ").strip().upper()

            if confirm == "Y":
                removed = expenses.pop(choice - 1)
                save_expenses(expenses)
                print(
                    f"Deleted: £{removed['amount']} - "
                    f"{removed['category']} - {removed['description']}\n"
                )
            elif confirm == "N":
                print("Deletion cancelled.\n")
            else:
                print("Invalid choice. Please enter Y or N.\n")

        else:
            print("Invalid number.\n")

    except ValueError:
        print("Please enter a valid number.\n")


# Shows the total amount of expenses
def total_expenses(expenses):
    total = sum(expense["amount"] for expense in expenses )
    print(f"Total spent: £{total:.2f}\n")

# main function loop
def main():
    expenses = load_expenses()

    while True:
        print("Expense Tracker")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. View Total")
        print("4. Delete Expense")
        print("5. Exit")

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
            delete_expense(expenses)
        elif choice == 5:
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.\n")

if __name__ == "__main__":
    main()