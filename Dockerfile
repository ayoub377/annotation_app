# Use an official Python runtime as a parent image

FROM python:3.9.0

# Set the working directory to /app

WORKDIR /app

COPY . /app

# --------------- Install python packages using `pip` ---------------

RUN pip install -r requirements.txt

# Make port 8501 available to the world outside this container

EXPOSE 8501

CMD ["streamlit", "run", "--server.port", "8501", "streamlit_app.py","--server.address=0.0.0.0"]