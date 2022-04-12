#Deriving the latest base image
FROM python:latest

# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/src

RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg -y

#to COPY the remote file at working directory in container
COPY example-database ./database
COPY music ./music
COPY downloader.py ./
COPY requirements.txt ./

#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD [ "python", "./downloader.py"]

#After the music has been downloaded the Python script will end
#Therefore the container will stop