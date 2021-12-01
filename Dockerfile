FROM jhonatans01/python-dlib-opencv
COPY . /app
WORKDIR /app
RUN apt-get install wget -y
RUN pip3 install -r requirements.txt
CMD ["python3", "app.py"]