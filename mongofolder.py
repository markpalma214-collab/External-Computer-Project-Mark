from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["school"] # make a database named school
students = db["students"] # add a collection as students
print("=====Insert students====")
name = input("Enter name: ")
age = int(input("Enter age: "))
course = input("Enter your course: ")
student = {
    "name":name,
    "age":age,
    "course":course,
}
result = students.insert_one(student)
print("Student inserted successfully")
print("id", result.inserted_id)
print("\==Student Records")
records = students.find()
print("--------------")
for student in records:
    print("ID:", student["_id"])
    print("name:", student["name"])
    print("age:", student["age"])
    print("course:", student["course"])
client.close()