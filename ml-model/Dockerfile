# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files (to avoid copying unnecessary files)
COPY . /app

# Install system dependencies if needed (for compiling certain packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK stopwords
RUN python -c "import nltk; nltk.download('stopwords')"

# Expose port 5001 to the world outside the container
EXPOSE 5001

# Set environment variables for Flask (this can be overwritten during runtime)
ENV FLASK_APP=api.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Use Gunicorn for production (Flask's built-in server isn't recommended for production)
RUN pip install gunicorn

# Run the application with Gunicorn (replaces Flask's built-in server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "api:app"]
