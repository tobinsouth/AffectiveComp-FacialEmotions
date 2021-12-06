FROM jhonatans01/python-dlib-opencv
COPY . /app
WORKDIR /app
RUN apt-get install wget -y
RUN pip3 install -r requirements.txt
EXPOSE 8050:8050
CMD ["python3", "app.py"]