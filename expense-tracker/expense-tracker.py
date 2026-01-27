from datetime import datetime, timezone
import json
import os
import uuid

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
# these next couple of functions are for update function
def get_optional_input(prompt: str):
    value = input(prompt).strip()
    return value if value else None

def get_optional_amount(prompt: str):
    while True:
        user_input = input(prompt).strip()
        if user_input == "":
            return None
        try:
            amount = float(user_input)
            if amount <= 0:
                print('Amount must be higher than zero.\n')
                continue
            return round(amount, 2)
        except ValueError:
            print("Please enter a valid number (e.g. 12.50) or press enter to keep current.\n")
#Backfill IDs for old saved expenses
def ensure_expense_ids(expenses):
    changed = False
    for expense in expenses:
        if "id" not in expense or not expense["id"]:
            expense["id"] = str(uuid.uuid4())
            changed = True
    if changed:
        save_expenses(expenses)


# This function is to add the expenses.
def add_expense(expenses):
    amount = get_valid_amount()
    category = get_non_empty_input("Enter category: ")
    description = get_non_empty_input("Enter description: ")
    expense = {
        "id": str(uuid.uuid4()),
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
        short_id = str(expense.get("id", ""))[:8]
        print(f"{i}. [{short_id}] £{expense['amount']:.2f} - {expense['category']} - {expense['description']} - {ts}")


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
                    f"Deleted: £{removed['amount']:.2f2} - "
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

# This function is to update/append expenses.
def edit_expense(expenses):
    if not expenses:
        print("No expenses to edit.\n")
        return
    view_expenses(expenses)

    try:
        choice = int(input("Enter the number of the expense to edit: "))
    except ValueError:
        print("Please enter a valid number.\n")
        return
    if not (1 <= choice <= len(expenses)):
        return
  
    expense = expenses[choice - 1]

    print("\nPress Enter to keep the current value.\n")

    new_amount = get_optional_amount(f"Amount (current £{expense['amount']:.2}): ")
    new_category = get_optional_input(f"Category (current {expense['category']}): ")
    new_description = get_optional_input(f"Description (current {expense['description']}): ")

    if new_amount is None and new_category is None and new_description is None:
        print("No changes made.\n")
        return
    
    confirm = input("Save changes? (Y/N): ").strip().upper()
    if confirm != "Y":
        print("Edit cancelled.\n")
        return
    
    if new_amount is not None:
        expense["amount"] = new_amount
    if new_category is not None:
        expense["category"] = new_category
    if new_description is not None:
        expense["description"] = new_description

    expense["timestamp"] = datetime.now(timezone.utc).isoformat()

    save_expenses(expenses)
    print("Expense updated.\n")

# Shows the total amount of expenses
def total_expenses(expenses):
    total = sum(expense["amount"] for expense in expenses )
    print(f"Total spent: £{total:.2f}\n")

# main function loop
def main():
    expenses = load_expenses()
    ensure_expense_ids(expenses)

    while True:
        print("Expense Tracker")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. View Total")
        print("4. Delete Expense")
        print("5. Update")
        print("6. Exit")

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
            edit_expense(expenses)
        elif choice == 6:
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.\n")

if __name__ == "__main__":
    main()