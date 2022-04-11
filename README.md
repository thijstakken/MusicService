# MusicService
Automatically download your YouTube playlists as MP3 with the highest quality possible using as few conversions as possible

Made to run on Ubuntu with Python and FFmpeg

## Installation

1. Copy the "example-database" folder and name it "database"
2. Install the requirements with: pip3 install -r requirements.txt
3. Put your own Youtube playlists URL's in the /database/playlists.txt file
4. Run the script and see your songs appear in the /music folder

The pipeline jobs needs to be updated with these steps also

Why apt? Isn't it possible with PIP?

To get FFmpeg installed on your Ubuntu system use:
sudo apt update
sudo add-apt-repository ppa:jonathonf/ffmpeg-4
sudo apt install ffmpeg
ffmpeg -version

https://www.codegrepper.com/code-examples/shell/install+ffprobe+ubuntu

This is also possible: sudo apt install ffmpeg
https://www.tecmint.com/install-ffmpeg-in-linux/

What's the difference?