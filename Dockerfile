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

# run the program with Python
CMD [ "python", "./main.py"]

# test to check if local env is present
#ENTRYPOINT echo $REBOOT_TIMER

# sleep for reboot_timer time
#CMD [ "sleep", "REBOOT_TIMER"]

# after the the script is done with downloading and uploading the music it exits
# therefore the container will stop