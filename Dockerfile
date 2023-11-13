# Use the official Python image as the base image
FROM python:3.9

# Set environment variables for the Django app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file and install Python dependencies
COPY req.txt /app/
RUN pip install --upgrade pip
RUN pip install -r req.txt

# Copy the Django project files to the container
COPY .. /app/

# Set MySQL database credentials as environment variables


# Expose the port that Django runs on (default is 8000)
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py","makemigrations"]
CMD ["python", "manage.py","migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]