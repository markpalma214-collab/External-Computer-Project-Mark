
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["mycollection"] # not table, dictionary data


def create():E
    name = input("Enter name: ")
    city = input("Enter city: ")
    interest = input("Enter interest: ")

    document = {
        "name": name,
        "city": city,
        "interest": interest
    }

    result = collection.insert_one(document)
    print("☑ Data inserted with ID:", result.inserted_id)


def read():
    print("\n📁 All documents:")
    for doc in collection.find():
        print(doc)

    city = input("\nEnter city to filter (or press Enter to skip): ")
    if city:
        print(f"\n📍 Documents from {city}:")
        for doc in collection.find({"city": city}):
            print(doc)


def update():
    name = input("Enter name of person to update: ")
    new_interest = input("Enter new interest: ")

    result = collection.update_one(
        {"name": name},
        {"$set": {"interest": new_interest}}
    )

    if result.modified_count > 0:
        print("☑ Document updated successfully.")
    else:
        print("⚠️ No matching document found.")


def delete():
    name = input("Enter name of person to delete: ")
    result = collection.delete_one({"name": name})
    if result.deleted_count > 0:
        print("🗑️ Document deleted successfully.")
    else:
        print("⚠️ No matching document found.")


while True:
    print("\n--- MongoDB CRUD Menu ---")
    print("1. Create (Insert)")
    print("2. Read (Retrieve)")
    print("3. Update (Modify)")
    print("4. Delete (Remove)")
    print("5. Exit")

    choice = input("Enter choice (1-5): ")

    if choice == "1":
        create()
    elif choice == "2":
        read()
    elif choice == "3":
        update()
    elif choice == "4":
        delete()
    elif choice == "5":
        print("👋 Exiting program.")
        break
    else:
        print("⚠️ Invalid choice, try again.")