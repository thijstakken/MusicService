#Deriving the latest base image
#FROM python:latest

FROM mcr.microsoft.com/windows/servercore:ltsc2019
ADD https://www.python.org/ftp/python/3.5.1/python-3.5.1.exe /temp/python-3.5.1.exe

# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/src

#to COPY the remote file at working directory in container
COPY ffmpeg.exe ./
COPY ffplay.exe ./
COPY ffprobe.exe ./
COPY requirements.txt ./
# Now the structure looks like this '/usr/app/src/test.py'

RUN pip install -r requirements.txt

#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD [ "python", "./downloader.py"]