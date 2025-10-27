from flask import Flask, render_template, request
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Static image folder for charts
IMAGE_FOLDER = os.path.join('static')
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# MongoDB setup
MONGO_URI = "mongodb+srv://harishv2021ai:DK12xpguurVBUKUE@database.lnoatsu.mongodb.net/?retryWrites=true&w=majority&appName=database"
client = MongoClient(MONGO_URI)
db = client["data_about_crime"]
section_collection = db["section_based"]

crime_db = client["crime_db"]
chart_collection = crime_db["crime_data"]

# ------------------ Text Analysis ------------------
def preprocess_text(text):
    text = re.sub(r'\W', ' ', str(text))
    return text.lower().strip()

def load_data():
    records = list(section_collection.find({}, {'_id': 0}))
    df = pd.DataFrame(records)
    df['Processed_Keywords'] = df['Keywords'].apply(preprocess_text)
    return df

def analyze_case(user_input, data, top_n=3):
    processed_input = preprocess_text(user_input)
    vectorizer = TfidfVectorizer()
    data_vectors = vectorizer.fit_transform(data['Processed_Keywords'])
    input_vector = vectorizer.transform([processed_input])
    similarity_scores = cosine_similarity(input_vector, data_vectors).flatten()
    top_indices = similarity_scores.argsort()[::-1][:top_n]

    results = []
    for idx in top_indices:
        score = similarity_scores[idx]
        if score > 0.1:
            results.append({
                "Section": data.iloc[idx]['Section'],
                "Category": data.iloc[idx]['Category'],
                "Description": data.iloc[idx]['Description'],
                "Action Taken": data.iloc[idx]['Action Taken'],
                "Similar Case": data.iloc[idx]['Similar Case (Judgment)'],
                "Section Description": data.iloc[idx]['section_desc'],
                "Keywords": data.iloc[idx]['Keywords'],
                "Relevance Score": round(score, 2)
            })
    return results

# ------------------ Chart Generation ------------------
def generate_charts():
    data = pd.DataFrame(list(chart_collection.find({}, {"_id": 0})))
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

# ------------------ Routes ------------------
@app.route('/', methods=['GET'])
def dashboard():
    generate_charts()
    return render_template('dashboard.html', result=None)

@app.route('/analyze', methods=['POST'])
def analyze():
    user_query = request.form['user_query']
    data = load_data()
    results = analyze_case(user_query, data)
    generate_charts()
    return render_template('dashboard.html', result=results)

# ------------------ Run App ------------------
if __name__ == '__main__':
    app.run(debug=True)
