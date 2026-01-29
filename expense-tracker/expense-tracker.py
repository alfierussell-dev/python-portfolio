from datetime import datetime, timezone
import json
import os
import uuid

# HELPERS
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
def normalise_amounts(expenses):
    changed = False
    for e in expenses:
        try:
            e["amount"] = round(float(e["amount"]), 2)
            changed = True
        except (KeyError, ValueError, TypeError):
            pass
    if changed:
        save_expenses(expenses)

# ID helpers
def find_expense_index_by_id(expenses, expense_id: str):
    expense_id = expense_id.strip().lower()
    for i, e in enumerate(expenses):
        if str(e.get("id", "")).lower().startswith(expense_id):
            return i
    return None
def find_expense_index_by_id_prefix(expenses, user_input: str):
    prefix = user_input.strip().lower()
    if not prefix:
        return None

    matches = []
    for i, e in enumerate(expenses):
        exp_id = str(e.get("id", "")).lower()
        if exp_id.startswith(prefix):
            matches.append(i)

    if len(matches) == 1:
        return matches[0]

    return None
def ensure_expense_ids(expenses):
    changed = False
    for e in expenses:
        if isinstance(e, dict) and not e.get("id"):
            e["id"] = str(uuid.uuid4())
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

# This is a render function to not duplicate data.
def display_expenses(expense_list):
    if not expense_list:
        print("No expenses recorded.\n")
        return
    
    for i, expense in enumerate(expense_list, start=1):
        ts = format_timestamp(expense.get("timestamp", ""))
        short_id = str(expense.get("id", ""))[:8]
        amount = float(expense.get("amount", 0))
        print(f"{i}, [{short_id}] £{amount:.2f} - {expense.get('category', '')} - {expense.get('description', '')} - {ts}")
    
    print()

# This function is the default show all, newest first.
def view_expenses(expenses):
    sorted_list = sorted(expenses, key=lambda e: e.get("timestamp", ""), reverse=True)
    display_expenses(sorted_list)

def filter_by_category(expenses):
    if not expenses:
        print("No expenses recorded.\n")
        return
    
    category = get_non_empty_input("Enter cetegory to filter by: ").strip()

    filtered = [e for e in expenses if str(e.get("category", "")).strip().lower() == category.lower()]
    
    filtered = sorted(filtered, key=lambda e: e.get("timestamp", ""), reverse=True)

    print(f"\nExpenses in category: {category}")
    display_expenses(filtered)

def filter_by_month(expenses):
    if not expenses:
        print("No expenses recorded.\n")
        
    month = get_non_empty_input("Enter month (YYYY-MM), e.g. 2026-01: ").strip()

    filtered = []
    for e in expenses:
        ts = e.get("timestamp", "")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            month_key = dt.strftime("%Y-%m")
            if month_key == month:
                filtered.append(e)
        except ValueError:
            continue
    filtered = sorted(filtered, key=lambda e: e.get("timestamp", ""), reverse=True)

    print(f"\nExpenses in month: {month}")
    display_expenses(filtered)

# sub-menu function
def filter_menu(expenses):
    if not expenses:
        print("No expenses recorded.\n")
        return

    print("\nFilter Expenses")
    print("1. By Category")
    print("2. By Month (YYYY-MM)")
    print("3. Back")

    choice = input("Choose an option: ").strip()

    if choice == "1":
        filter_by_category(expenses)
    elif choice == "2":
        filter_by_month(expenses)
    elif choice == "3":
        return
    else:
        print("Invalid option.\n")


# gives totals for each category.
def category_totals(expenses):
    if not expenses:
        print("No expenses recorded.\n")
        return
    totals = {}

    for expense in expenses:
        category = expense["category"]
        amount = float(expense["amount"])

        if category not in totals:
            totals[category] = 0.0
    
        totals[category] += amount
    
    print("\nSpending by Category:")
    for category, total in totals.items():
        print(f"{category}: £{total:.2f}")

    print()

# Totals for each month using timestamps.
def monthly_totals(expenses):
    if not expenses:
        print("No expenses recorded.\n")
        return
    
    totals = {}

    for expense in expenses:
        ts = expense.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue

        month_key = dt.strftime("%Y-%m")

        amount = float(expense["amount"])

        if month_key not in totals:
            totals[month_key] = 0.0
        
        totals[month_key] += amount
    
    print("\nSpending by Month:")
    for month, total in sorted(totals.items()):
        print(f"{month}: £{total:.2f}")

    print()

# This function is to delete expenses using their IDs.
def delete_expense_by_id(expenses):
    if not expenses:
        print("No expenses to delete.\n")
        return

    view_expenses(expenses)
    user_id = input("Enter expense ID (or first 8 chars) to delete: ").strip()

    idx = find_expense_index_by_id_prefix(expenses, user_id)

    if idx is None:
        print("No matching ID found (or ID was ambiguous). Copy the 8-char ID shown in [].\n")
        return

    e = expenses[idx]
    confirm = input(
        f"Delete [{str(e.get('id',''))[:8]}] £{float(e['amount']):.2f} - {e['category']} - {e['description']}? (Y/N): "
    ).strip().upper()

    if confirm != "Y":
        print("Deletion cancelled.\n")
        return

    removed = expenses.pop(idx)
    save_expenses(expenses)
    print(f"Deleted [{str(removed.get('id',''))[:8]}].\n")

    


# This function is to update/append expenses by using their IDs.
def edit_expense_by_id(expenses):
    if not expenses:
        print("No expenses to edit.\n")
        return
    
    view_expenses(expenses)
    user_id = input("Enter expense ID (or first 8 chars) to delete: ").strip()

    idx = find_expense_index_by_id_prefix(expenses, user_id)

    if idx is None:
        print("No matching ID found (or ID was ambiguous). Copy the 8-char ID shown in [].\n")
        return
    
    expense = expenses[idx]

    print("\nPress Enter to keep the current value.\n")

    current_amount = float(expense.get("amount", 0))
    new_amount = get_optional_amount(f"Amount (current £{current_amount:.2f}): ")
    new_category = get_optional_input(f"Category (current {expense.get('category','')}): ")
    new_description = get_optional_input(f"Description (current {expense.get('description','')}): ")

    if new_amount is None and new_category is None and new_description is None:
        print('No changes made.\n')
        return
    confirm = input("Do you wish to save changes? (Y/N): ").strip().upper()
    if confirm != "Y":
        print("Edit cancelled.\n")

    if new_amount is not None:
        expense["amount"] = new_amount
    if new_category is not None:
        expense["category"] = new_category
    if new_description is not None:
        expense["description"] = new_description

    expense["timestampt"] = datetime.now(timezone.utc).isoformat()

    save_expenses(expenses)
    print(f"Expense updated [{str(expense.get('id', ''))[:8]}].\n")
# Shows the total amount of expenses
def total_expenses(expenses):
    total = sum(expense["amount"] for expense in expenses )
    print(f"Total spent: £{total:.2f}\n")

# main function loop
def main():
    expenses = load_expenses()
    ensure_expense_ids(expenses)
    normalise_amounts(expenses)

    while True:
        print("Expense Tracker")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. View Total")
        print("4. Delete Expense")
        print("5. Update Expense (by ID)")
        print("6. Category totals")
        print("7. Monthly totals")
        print("8. Filter")
        print("9. Exit")

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
            delete_expense_by_id(expenses)
        elif choice == 5:
            edit_expense_by_id(expenses)
        elif choice == 6:
            category_totals(expenses)
        elif choice == 7:
            monthly_totals(expenses)
        elif choice == 8:
            filter_menu(expenses)
        elif choice == 9:
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.\n")

if __name__ == "__main__":
    main()