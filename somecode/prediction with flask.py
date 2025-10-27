from flask import Flask, render_template, request
from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

app = Flask(__name__)

# MongoDB Setup
MONGO_URI = "mongodb+srv://harishv2021ai:DK12xpguurVBUKUE@database.lnoatsu.mongodb.net/?retryWrites=true&w=majority&appName=database"
client = MongoClient(MONGO_URI)
db = client["data_about_crime"]
collection = db["section_based"]

# Preprocess text
def preprocess_text(text):
    text = re.sub(r'\W', ' ', str(text))
    text = text.lower()
    return text.strip()

# Load and preprocess data from MongoDB
def load_data():
    records = list(collection.find({}, {'_id': 0}))
    df = pd.DataFrame(records)
    df['Processed_Keywords'] = df['Keywords'].apply(preprocess_text)
    return df

# Analyze case
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

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    message = None

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            data = load_data()
            results = analyze_case(user_input, data)
            if not results:
                message = "No relevant case found."
        else:
            message = "Please enter a query."

    return render_template('index.html', result=results, message=message)

if __name__ == '__main__':
    app.run(debug=True)