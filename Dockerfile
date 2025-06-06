# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including TeX Live packages
# Added texlive-latex-extra to get enumitem.sty and other common packages
# Consider texlive-fonts-recommended if you face font issues later
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        docker.io \
        texlive-latex-base \
        texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY main.py .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]