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
    # model_id="meta-llama/llama-3-1-70b-instruct",
    model_id ="ibm/granite-13b-instruct-v2",
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

# Function to analyze the proposal based on rules
def analyze_proposal(proposal):
    issues = []
    proposal_lower = safe_lower(proposal)

    for _, row in data.iterrows():
        word = safe_lower(row['Word/Phrase'])
        if word and word in proposal_lower:
            issues.append({
                'word': row['Word/Phrase'],
                'explanation': row['Explanation'] or "",
                'inappropriate_example': row['Inappropriate Usage'] or "",
                'suggested_change': row['Suggested Change'] or ""
            })

    return issues

# Extract text from PDF files
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        text += doc.load_page(page_num).get_text()
    doc.close()
    return text

# Generate suggestions using watsonx.ai
# Define helper functions like generate_suggestions above the routes

def generate_suggestions(proposal, issues):
    response = "" 
    prompt = f"Review the following proposal and rewrite based on the provided suggestions:\n\n{proposal}\n\n"
    if issues:
        prompt += "Identify the following issues and suggest improvements:\n"
        for issue in issues:
            prompt += f"- Issue with '{issue['word']}': {issue['explanation']}\n"
            prompt += f"  Suggested Change: {issue['suggested_change']}\n"
            response += model.generate_text(prompt)
            
   
    # Generate text using watsonx.ai model
    # response = model.generate_text(prompt)

    # Check if response is already a string
    if isinstance(response, str):
        return response.strip()

    # Handle unexpected response types
    return response.get("generated_text", "").strip() if isinstance(response, dict) else "No suggestions generated."


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

        # print(proposal)
        issues = analyze_proposal(proposal)
        improvements = generate_suggestions(proposal, issues)

        return render_template("index.html", proposal=proposal, issues=issues, improvements=improvements)

    return render_template("index.html")

# Run the Flask app
if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)  # Ensure temp directory exists
    app.run(debug=True)
