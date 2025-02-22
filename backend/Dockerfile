FROM python:3.11.5-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

# Expose port 8000 for the application
EXPOSE 8000

# Set the command to run the app
CMD ["python", "main.py"]
