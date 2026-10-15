from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["movies"]
# insert a collection
movie_obj = db["movie_name"]

movie_name = input("Enter a movie: ")
description = input("Enter description:")
status = input("enter status: ")
rating = int(input("Enter your rating"))
context = {
    "movie_name":movie_name,
    "description":description,
    "status":status,
    "rating":rating,
}

result = movie_obj.insert_one(context)
print("id inserted successfully!")
print("id:", result.inserted_id)
print("Database")
print("\n=======================")
for movie in movie_obj.find():
    print("movie:", movie["movie_name"])
    print("description:",movie["description"])
    print("status:",movie["status"])
    print("rating:", movie["rating"])
    print("\n")
    print("==========================")
    print("\n")

client.close()
