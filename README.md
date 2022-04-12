# MusicService
Automatically download your YouTube playlists as MP3 with the highest quality possible using as few conversions as possible

Made to run on Ubuntu with Python and FFmpeg
or a Docker container

## Installation for Linux/Ubuntu

1. Install ffmpeg package with: 
- sudo apt update
- sudo apt install ffmpeg

2. Install the requirements with: pip3 install -r requirements.txt

3. Copy the "example-database" folder and name it "database"

4. Put your own Youtube playlists URL's in the /database/playlists.txt file

5. Run the script and see your songs appear in the /music folder


## Installation for Docker

See the Docker release here at Docker Hub:
https://hub.docker.com/repository/docker/tsivim/musicservice

1. docker pull tsivim/musicservice
2. docker run musicservice
