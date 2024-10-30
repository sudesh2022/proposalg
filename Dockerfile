# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy application files to the container
COPY . /app

# Install required system libraries for pandas and PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    pkg-config \
    libmupdf-dev \
    libopenjp2-7 \
    libtiff5 \
    libxml2 \
    libxslt1.1 \
    libglib2.0-0 \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip and upgrade the tools for building packages
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set environment variables (optional)
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Command to run the Flask application
CMD ["python", "app.py"]
