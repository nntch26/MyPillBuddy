# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Move to the myapp directory to run the Django development server
WORKDIR /app/myapp

# Expose port 8000 for Django
EXPOSE 8000

# Run the Django development server (this can be changed for production)
CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]