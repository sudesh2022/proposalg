import os
import fitz  # PyMuPDF for PDF extraction
import pandas as pd
from flask import Flask, request, render_template
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Watsonx.ai credentials
credentials = Credentials(
    url=os.getenv("WATSONX_URL"),
    api_key=os.getenv("WATSONX_API_KEY")
)
client = APIClient(credentials)

# Configure the model inference
model = ModelInference(
    model_id="ibm/granite-13b-instruct-v2",
    api_client=client,
    project_id=os.getenv("WATSONX_PROJECT_ID"),
    params={"max_new_tokens": 1000}
)

# Load the Excel data for proposal analysis rules
excel_path = "word_usage.xlsx"
data = pd.read_excel(excel_path)

# Helper function to safely convert text to lowercase
def safe_lower(text):
    return text.lower() if isinstance(text, str) else ""

# Function to split text into chunks of 300 words
def split_text_into_chunks(text, chunk_size=300):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Function to analyze the proposal based on rules
def analyze_proposal(proposal):
    issues = []
    proposal_lower = safe_lower(proposal)

    for _, row in data.iterrows():
        word = safe_lower(row['Word/Phrase'])
        if word and word in proposal_lower:
            issue = {
                'word': row['Word/Phrase'],
                'explanation': row['Explanation'] or "",
                'inappropriate_example': row['Inappropriate Usage'] or "",
                'suggested_change': row['Suggested Change'] or ""
            }

            # Ensure the issue is not empty before adding it
            if any(issue.values()):
                issues.append(issue)

    return issues


# Extract text from PDF files
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        text += doc.load_page(page_num).get_text()
    doc.close()
    return text

# Generate suggestions for each chunk using watsonx.ai
def generate_suggestions_for_chunks(chunks):
    all_suggestions = []
    for chunk in chunks:
        prompt = f"Review the following proposal chunk and suggest improvements:\n\n{chunk}\n"
        response = model.generate_text(prompt)

        # Ensure response is a string
        if isinstance(response, str):
            all_suggestions.append(response.strip())
        elif isinstance(response, dict):
            all_suggestions.append(response.get("generated_text", "").strip())

    return "\n\n".join(all_suggestions)

# Define the route after all helper functions
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        proposal = request.form.get("proposal", "")

        # Check if a PDF file is uploaded
        pdf_file = request.files.get("pdf_file")
        if pdf_file:
            pdf_path = f"temp/{pdf_file.filename}"
            pdf_file.save(pdf_path)
            proposal = extract_text_from_pdf(pdf_path)

        # Split the proposal into 300-word chunks
        chunks = split_text_into_chunks(proposal)

        # Analyze and generate suggestions for each chunk
        issues = [issue for chunk in chunks for issue in analyze_proposal(chunk)]
        improvements = generate_suggestions_for_chunks(chunks)

        return render_template(
            "index.html", proposal=proposal, issues=issues, improvements=improvements
        )

    return render_template("index.html")

# Run the Flask app
if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)  # Ensure temp directory exists
    app.run(debug=True)
