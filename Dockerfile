FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_ENV=production
CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "60"]

