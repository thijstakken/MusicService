# using the latest Python image
FROM python:latest

# any working directory can be chosen as per choice like '/' or '/home' etc
WORKDIR /usr/app/src

# to COPY the remote file at working directory in container
COPY example-database ./database
COPY example-music ./music
COPY main.py ./
COPY requirements.txt ./

# install Python module requirements
RUN pip install -r requirements.txt

# update the enviroment
RUN apt-get update

# install ffmpeg, this is needed for .m4a/.mp4 to mp3 conversion
RUN apt-get install ffmpeg -y

# run the Music Service with Python
CMD [ "python", "./main.py"]