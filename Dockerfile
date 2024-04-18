# Use the official Python image as the base image
FROM python:3.9

# Set environment variables for the Django app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set MySQL database credentials as environment variables
ENV DB_HOST 192.168.2.60
ENV DB_PORT 3306
ENV DB_NAME ocean
ENV DB_USER root
ENV DB_PASSWORD Sunderland@411

# Install system dependencies including ODBC library and Microsoft ODBC driver for SQL Server
RUN apt-get update && \
    apt-get install -y unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
	echo "deb [arch=amd64,arm64,armhf] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 \
	apt-get install -y msodbcsql17

# Create and set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file and install Python dependencies
COPY req.txt /app/
RUN pip install --upgrade pip && pip install -r req.txt

# Copy the Django project files to the container
COPY . /app/

# Expose the port that Django runs on (default is 8000)
EXPOSE 80

# Run the Django development server
CMD ["python", "manage.py", "makemigrations"]
CMD ["python", "manage.py", "migrate"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:80", "--insecure"]
