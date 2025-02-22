FROM python:3.11.5-slim

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

COPY backend/ ./

EXPOSE 8000

CMD ["python", "main.py"] 
