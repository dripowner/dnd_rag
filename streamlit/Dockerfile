FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir streamlit requests python-dotenv

COPY . .

CMD ["python", "-m", "streamlit", "run", "app.py"]
