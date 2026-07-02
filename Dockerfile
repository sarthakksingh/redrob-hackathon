FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Ranking is standard-library only. Install Streamlit only when using the demo:
# docker build -t redrob-ranker .
# docker run --rm -p 8501:8501 redrob-ranker
RUN pip install --no-cache-dir streamlit

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
