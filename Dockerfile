FROM jhonatans01/python-dlib-opencv
COPY . /app
WORKDIR /app
RUN apt-get update
RUN apt install libgl1-mesa-glx
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install -y python3-opencv
RUN pip3 install -r requirements.txt
CMD ["python3", "app.py"]