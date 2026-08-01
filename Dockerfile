FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

ENV API_BASE_URL=http://localhost:8000
EXPOSE 7860

CMD ["./start.sh"]
