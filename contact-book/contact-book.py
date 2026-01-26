

contacts = {}

def show_menu():
	print("\nContact Book")
	print("1. Add Contact")
	print("2. View Contacts")
	print("3. Search Contacts")
	print("4. Delete contact")
	print("5. Exit")



def add_contact():
	name = input("Enter Name: ")
	phone = input("Enter Phone Number: ")
	contacts[name] = phone
	print("Contact added!")

def view_contact():
	if not contacts:
		print("No contacts found.")
	else:
		for name, phone in contacts.items():
			print(f"{name}: {phone}")

def search_contacts():
	name = input("Enter name: ")
	if name in contacts:
		print(f"{name}: {contacts[name]}")
	else:
		print("Contact not found.")

def delete_contact():
	name = input("Enter name: ")
	if name in contacts:
		print("Confirm delete?")
		choice_2 = input("Yes/No: ")
		if choice_2 == "yes":
			contacts.pop(name, None)
			print("Contact deleted")
		elif choice_2 == "no":
			print("Delete cancelled") 
	else:
		print("Contact not found.")	

while True:
	show_menu()
	choice = input("Choose an option: ")
	if choice == "1":
		add_contact()
	elif choice == "2":
		view_contact()

	elif choice == "3":
		search_contacts()

	elif choice == "4":
		delete_contact()

	elif choice == "5":
		print("Goodbye. ")
		break
	else:
		print("Invalid option. ")	



	
show_menu()
add_contact()
view_contact()
search_contacts()