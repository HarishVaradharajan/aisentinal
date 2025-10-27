from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# MongoDB Setup
MONGO_URI = "mongodb+srv://harishv2021ai:DK12xpguurVBUKUE@database.lnoatsu.mongodb.net/?retryWrites=true&w=majority&appName=database"
client = MongoClient(MONGO_URI)
db = client["data_about_crime"]
collection = db["section_based"]  # Update this to match your collection name

# Preprocess text: Clean and normalize
def preprocess_text(text):
    text = re.sub(r'\W', ' ', str(text))  # Remove special characters
    text = text.lower()  # Convert to lowercase
    return text.strip()

# Load and preprocess data from MongoDB
def load_data():
    records = list(collection.find({}, {'_id': 0}))
    df = pd.DataFrame(records)
    df['Processed_Keywords'] = df['Keywords'].apply(preprocess_text)
    return df

# Analyze user input and return top 3 matches
def analyze_case(user_input, data, top_n=3):
    processed_input = preprocess_text(user_input)

    # Vectorize keywords
    vectorizer = TfidfVectorizer()
    data_vectors = vectorizer.fit_transform(data['Processed_Keywords'])
    input_vector = vectorizer.transform([processed_input])

    # Compute similarity
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

# Example usage
if __name__ == "__main__":
    user_input = input("Enter the case details: ")
    data = load_data()
    results = analyze_case(user_input, data)

    if results:
        print("\nTop Matching Sections:\n")
        for i, res in enumerate(results, 1):
            print(f"--- Match {i} ---")
            for key, value in res.items():
                print(f"{key}: {value}")
            print()
    else:
        print("No relevant case found.")
