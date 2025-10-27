from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId
app = Flask(__name__)
MONGO_URI = "mongodb+srv://harishv2021ai:DK12xpguurVBUKUE@database.lnoatsu.mongodb.net/?retryWrites=true&w=majority&appName=database"
client = MongoClient(MONGO_URI)
db = client["data_about_crime"]
collection = db["section_based"]
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/add_data', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        # Collect user input from the form
        section = request.form['section']
        keywords = request.form['keywords']
        category = request.form['category']
        description = request.form['description']
        action_taken = request.form['action_taken']
        similar_case = request.form['similar_case']
        section_desc = request.form['section_desc']
        data = {
            "Section": section,
            "Keywords": keywords,
            "Category": category,
            "Description": description,
            "Action Taken": action_taken,
            "Similar Case (Judgment)": similar_case,
            "Section Description": section_desc
        }
        collection.insert_one(data)
        return redirect(url_for('home'))
    return render_template('add_data.html')
if __name__ == "__main__":
    app.run(debug=True)