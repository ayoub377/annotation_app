# Use an official Python runtime as a parent image

FROM python:3.9-slim-buster

# Set the working directory to /app

WORKDIR /app

COPY . /app

RUN apt -y update && apt -y upgrade

RUN apt -y install libopencv-dev

RUN pip install --no-cache-dir -r /app/requirements.txt

# Make port 8501 available to the world outside this container

EXPOSE 8501

CMD ["streamlit", "run", "--server.port", "8501", "streamlit_app.py","--server.address=0.0.0.0"]
