FROM python:3

WORKDIR /app

COPY . /app

RUN apt-get update \
    && apt-get install -y ffmpeg

RUN pip install --trusted-host pypi.python.org -r requirements.txt

ENTRYPOINT ["python", "niconicoreload.py"]