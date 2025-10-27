import pandas as pd
from pymongo import MongoClient

# Read CSV
df = pd.read_csv("laws_and_crimes_dataset.csv")

# Connect to MongoDB Atlas
MONGO_URI = "mongodb+srv://harishv2021ai:DK12xpguurVBUKUE@database.lnoatsu.mongodb.net/"
client = MongoClient(MONGO_URI)

# Choose DB and Collection
db = client["data_about_crime"]
collection = db["section_based"]

# Insert into MongoDB
data_dict = df.to_dict("records")
collection.insert_many(data_dict)

print("Data uploaded successfully!")
