FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install psycopg2-binary
CMD ["python", "scraper.py"]
