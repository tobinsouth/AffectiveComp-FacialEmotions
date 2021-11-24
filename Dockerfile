FROM python:3.9

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install -y cmake

COPY . /ganemon
WORKDIR /ganemon

RUN python3 -m pip install -r requirements.txt 

ENTRYPOINT python app.py