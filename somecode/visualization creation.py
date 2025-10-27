from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Static image folder
IMAGE_FOLDER = os.path.join('static')
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# MongoDB Setup
MONGO_URI = "mongodb+srv://harishv2021ai:DK12xpguurVBUKUE@database.lnoatsu.mongodb.net/?retryWrites=true&w=majority&appName=database"
client = MongoClient(MONGO_URI)
db = client["crime_db"]
collection = db["crime_data"]
user_collection = db["users"]

def generate_charts():
    data = pd.DataFrame(list(collection.find({}, {"_id": 0})))
    chart_info = [
        ('img1.png', ['Cybercrime', 'Domestic_Violence'], 'Cybercrime vs Domestic Violence'),
        ('img2.png', ['Total_Crimes', 'Theft'], 'Total Crimes vs Theft'),
        ('img3.png', ['Murder', 'Assault'], 'Murder vs Assault')
    ]

    for filename, columns, title in chart_info:
        plt.figure(figsize=(13, 7))
        bar_width = 0.35
        index = range(len(data['State']))

        plt.bar(index, data[columns[0]], bar_width, label=columns[0], color='black')
        plt.bar([i + bar_width for i in index], data[columns[1]], bar_width, label=columns[1], color='gray')

        plt.xticks([i + bar_width / 2 for i in index], data['State'], rotation=45, ha='right', fontsize=9)
        plt.xlabel('States')
        plt.ylabel('Reported Cases')
        plt.title(title)
        plt.legend()
        plt.tight_layout()

        plt.savefig(os.path.join(IMAGE_FOLDER, filename))
        plt.close()
@app.route('/')
def dashboard():
    generate_charts()  # Generate charts before rendering dashboard
    return render_template('dashboard.html')
if __name__ == '__main__':
    app.run(debug=True)
