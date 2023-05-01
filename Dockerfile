# Use the official Python image as the base image
FROM python:3.9

# Set the working directory
WORKDIR /

# Copy requirements.txt into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --upgrade pip && \
		pip install -r requirements.txt && \
            apt-get update && \
		        cat packages.txt | xargs apt-get install -y

# Copy the rest of the application code
COPY . .

# Expose the port the app will run on
EXPOSE 5000

# Start the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "5000", "main:app"]

