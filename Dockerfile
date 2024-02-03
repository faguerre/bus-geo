FROM python:3.10

RUN apt-get update && \
    apt-get install -y build-essential 
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY . /app

RUN pip install --upgrade pip && \
    pip install uwsgi && \
    pip install setuptools && \
    pip install wheel

RUN pip install -r app/requirements.txt

CMD ["uvicorn", "app.src.app:app", "--workers", "4", "--host", "0.0.0.0", "--port", "5000"]
