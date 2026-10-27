FROM python:3.10-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates ./templates

RUN chown -R appuser:appuser /app

USER appuser
EXPOSE 5000

CMD ["python", "app.py"]