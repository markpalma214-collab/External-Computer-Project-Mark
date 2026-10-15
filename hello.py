from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)

try:
    print("MongoDB connected!")

    db = client["my_database"]
    collection = db["myCollection"]

    collection.insert_one({
        "name": "Cherry",
        "city": "Dasmarinas"
    })

    for doc in collection.find():
        print(doc)

except Exception as e:
    print("ERROR:", e)