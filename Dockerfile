FROM python:3.9

RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY . /ganemon
WORKDIR /ganemon

RUN python3 -m pip install -r requirements.txt 

ENTRYPOINT python app.py