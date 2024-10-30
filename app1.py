import openai
import pandas as pd
from flask import Flask, request, render_template
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load the Excel file and prepare the data
excel_path = "word_usage.xlsx"
data = pd.read_excel(excel_path)

# Function to safely convert values to lowercase if possible
def safe_lower(text):
    if isinstance(text, str):
        return text.lower()
    return ""

# Function to analyze the proposal based on the Excel rules
def analyze_proposal(proposal):
    issues = []
    proposal_lower = safe_lower(proposal)  # Ensure proposal is handled safely

    for _, row in data.iterrows():
        word = row['Word/Phrase']
        explanation = row['Explanation']
        inappropriate_example = row['Inappropriate Usage']
        suggested_change = row['Suggested Change']

        # Safely handle missing values and check for word usage
        word_lower = safe_lower(word)
        if word_lower and word_lower in proposal_lower:
            issues.append({
                'word': word,
                'explanation': explanation if isinstance(explanation, str) else "",
                'inappropriate_example': inappropriate_example if isinstance(inappropriate_example, str) else "",
                'suggested_change': suggested_change if isinstance(suggested_change, str) else ""
            })

    return issues

# Route for the homepage with form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        proposal = request.form["proposal"]
        issues = analyze_proposal(proposal)

        # Use OpenAI to suggest text improvements
        improvements = generate_suggestions(proposal, issues)

        return render_template("index.html", proposal=proposal, issues=issues, improvements=improvements)

    return render_template("index.html")

# Function to generate suggestions using OpenAI's newer model
def generate_suggestions(proposal, issues):
    prompt = f"Review the following proposal text:\n\n{proposal}\n\n"
    if issues:
        prompt += "Identify the following issues and suggest improvements:\n"
        for issue in issues:
            prompt += f"- Issue with '{issue['word']}': {issue['explanation']}\n"
            prompt += f"  Suggested Change: {issue['suggested_change']}\n"

    # Use OpenAI's gpt-3.5-turbo or gpt-4 model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # You can switch to "gpt-4" if needed
        messages=[
            {"role": "system", "content": "You are a helpful assistant who will act as the Executive Summary Analyzer. You will review the provided content for the words listed below only and flag them.   Resulting content generated should align with the ‘suggested change’ in the examples. Please generate full proposal "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    return response.choices[0].message['content'].strip()

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
