import openai
import pandas as pd
from flask import Flask, request, render_template, redirect, url_for
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF for PDF extraction

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

        word_lower = safe_lower(word)
        if word_lower and word_lower in proposal_lower:
            issues.append({
                'word': word,
                'explanation': explanation if isinstance(explanation, str) else "",
                'inappropriate_example': inappropriate_example if isinstance(inappropriate_example, str) else "",
                'suggested_change': suggested_change if isinstance(suggested_change, str) else ""
            })

    return issues

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    doc.close()
    return text

# Route for the homepage with form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        proposal = request.form.get("proposal", "")

        # Check if a PDF file was uploaded
        pdf_file = request.files.get("pdf_file")
        if pdf_file:
            # Save the PDF temporarily and extract its content
            pdf_path = f"temp/{pdf_file.filename}"
            pdf_file.save(pdf_path)
            proposal = extract_text_from_pdf(pdf_path)

        issues = analyze_proposal(proposal)
        improvements = generate_suggestions(proposal, issues)

        return render_template("index.html", proposal=proposal, issues=issues, improvements=improvements)

    return render_template("index.html")

# Function to generate suggestions using OpenAI's API
def generate_suggestions(proposal, issues):
    prompt = f"Review the following proposal text:\n\n{proposal}\n\n"
    if issues:
        prompt += "Identify the following issues and suggest improvements:\n"
        for issue in issues:
            prompt += f"- Issue with '{issue['word']}': {issue['explanation']}\n"
            prompt += f"  Suggested Change: {issue['suggested_change']}\n"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant analyzing a proposal for issues based on provided rules."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )

    return response.choices[0].message['content'].strip()

# Run the app
if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)  # Ensure the temp folder exists
    app.run(debug=True)
