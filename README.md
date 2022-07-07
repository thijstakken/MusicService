This program is currently in its experimental phase
All functionality is present and could be used
Now it comes down to see if there are any bugs, testing, testing, testing...

Use at your own risk, never trust the code of a random dude on the internet without first checking it yourself :)

Feel free to submit issues, and pull requests!

# MusicService
This container will download your Youtube Playlists and upload the MP3's to your Nextcloud cloud storage!

It downloads your YouTube playlists as MP3 with the highest quality possible using as few conversions as possible. It will then upload those files to your Nextcloud account.


## Testing recommendation
To test this container, it's recommended to test it with a free Nextcloud trial account. Go to: https://try.nextcloud.com/ and use the instant trial. You will recieve an account which will be valid for 60 minutes. When the account is created, copy the username into the NCUSERNAME variable and start the container.
This way we can safely experiment with the container program. It supposed to only upload files, so the risk of files getting deleted is very low, but just in case this is the recommended way.


## Installation for Docker (recommended)
See the Docker release here at Docker Hub:
https://hub.docker.com/r/thijstakken/musicservice

1. Have the Docker engine installed
2. Run this command in your terminal (make sure to change the variables: URL, NCUSERNAME, NCPASSWORD):
```
docker run -d \
 --name musicservice \
 --restart=no \
 -v musicdatabase:/usr/app/src/database/ \
 -v musiccache:/usr/app/src/music/ \
 -e LOCAL_DIRECTORY=music \
 -e REMOTE_DIRECTORY=some/folder/ \
 -e URL=https://demo2.nextcloud.com/remote.php/dav/files/43LiaqqEGjD6b8xB/ \
 -e NCUSERNAME=43LiaqqEGjD6b8xB \
 -e NCPASSWORD=demo \
 -e INTERVAL=8 \
 --network=host \
thijstakken/musicservice:latest
```
3. That's all! After the container stops, you should now see that you have an MP3 in your Nextcloud account in a folder called "music" at the root of your account.
4. You can update which playlists to download here: ./database/playlists.txt. The recommended way is to update that file when the container is turned off. Go to your Docker volumes location and find the file there.

(the INTERVAL variable is optional, by default it's set to 5 if you dont specify anthting. if you want to run the script more often or slower, you can just punt in a number. It's in minutes, so 10 will be 10 minutes. If you only want to run the script one time. You can set the number to 0 and then the script will not run on shedule and just stop after one run)

## OLD manual installation for Linux/Ubuntu, (not recommended)

1. Install ffmpeg package with: 
- sudo apt update
- sudo apt install ffmpeg

2. Install the requirements with: pip3 install -r requirements.txt

3. Copy the "example-database" folder and name it "database"

4. Put your own Youtube playlists URL's in the /database/playlists.txt file

5. Cpoy the .env into your local enviroment and change the variabels to your liking

6. Run the main.py script and see your songs appear in the /music folder

