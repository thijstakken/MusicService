# using the latest Python image
FROM python:slim

# any working directory can be chosen as per choice like '/' or '/home' etc
WORKDIR /

# to COPY the remote file at working directory in container
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql cryptography


COPY webapp webapp
COPY migrations migrations
COPY musicservice.py config.py boot.sh ./
#COPY example-music ./music
#COPY main.py ./
RUN chmod a+x boot.sh

ENV FLASK_APP musicservice.py

# update the enviroment
RUN apt-get update
# install ffmpeg, this is needed for .m4a/.mp4 to mp3 conversion
RUN apt-get install ffmpeg -y

# configure default environment variabels
# Python buffers it log output, this created a delayed output on the console
# to mitigate slow log ouput of the application, disable the buffer with:
ENV PYTHONUNBUFFERED=1
# by default the script will use 5, which means that the script will rerun every 5 minutes
# users can overrule the default by simply providing their own INTERVAL variable
ENV INTERVAL=5

# let's dance: "In 5, 6, 7, 8!"
EXPOSE 5678
ENTRYPOINT ["./boot.sh"]