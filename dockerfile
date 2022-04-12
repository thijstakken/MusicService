#Deriving the latest base image
FROM python:latest

# Any working directory can be chosen as per choice like '/' or '/home' etc
# i have chosen /usr/app/src
WORKDIR /usr/app/src

#to COPY the remote file at working directory in container
COPY downloader.py ./
COPY requirements.txt ./
# Now the structure looks like this '/usr/app/src/test.py'

RUN pip install -r requirements.txt

#CMD instruction should be used to run the software
#contained by your image, along with any arguments.

CMD ["sudo apt install", "ffmpeg"]

CMD [ "python", "./downloader.py"]