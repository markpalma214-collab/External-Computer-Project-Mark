from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Access database and collection
db = client["gym_database"]
members = db["gym_members"]

# === Insert Gym Member ===
print("=== Register Gym Member ===")
name = input("Enter member name: ")
age = int(input("Enter age: "))
membership = input("Enter membership type: ")
payment = float(input("Enter monthly payment: "))

member = {
    "name": name,
    "age": age,
    "membership": membership,
    "payment": payment
}

result = members.insert_one(member)

print("Gym member registered successfully!")
print("ID:", result.inserted_id)

# === Retrieve Gym Member Records ===
print("\n=== Gym Member Records ===")
records = members.find()

for member in records:
    print("------")
    print("ID:", member["_id"])
    print("Name:", member["name"])
    print("Age:", member["age"])
    print("Membership:", member["membership"])
    print("Monthly Payment:", member["payment"])

# Close connection
client.close()