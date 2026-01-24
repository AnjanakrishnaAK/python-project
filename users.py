users = {}

def create_user():
    user_id = input("Enter User ID: ")
    name = input("Enter Name: ")
    users[user_id] = name
    print("User created successfully!\n")

def read_users():
    if not users:
        print("No users found.\n")
    else:
        print("User List:")
        for uid, name in users.items():
            print(f"{uid} : {name}")
        print()

def update_user():
    user_id = input("Enter User ID to update: ")
    if user_id in users:
        name = input("Enter new name: ")
        users[user_id] = name
        print("User updated successfully!\n")
    else:
        print("User not found.\n")

def delete_user():
    user_id = input("Enter User ID to delete: ")
    if user_id in users:
        del users[user_id]
        print("User deleted successfully!\n")
    else:
        print("User not found.\n")

while True:
    print("CRUD MENU")
    print("1. Create User")
    print("2. Read Users")
    print("3. Update User")
    print("4. Delete User")
    print("5. Exit")

    choice = input("Enter choice (1-5): ")

    if choice == '1':
        create_user()
    elif choice == '2':
        read_users()
    elif choice == '3':
        update_user()
    elif choice == '4':
        delete_user()
    elif choice == '5':
        print("Exiting program...")
        break
    else:
        print("Invalid choice!\n")