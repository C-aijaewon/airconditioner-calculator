FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Airconditioner.py .
COPY .streamlit .streamlit

EXPOSE 8501

CMD ["streamlit", "run", "Airconditioner.py", "--server.port=8501", "--server.address=0.0.0.0"]