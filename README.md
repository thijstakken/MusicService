# Music sync Service

An container application that automatically downloads your YouTube music to your Nextcloud!

This application will monitor your playlists, and when you added a new song, it will detect it, download it and upload it to your Nextcloud account!

It downloads your YouTube playlists as MP3 with the highest quality possible using as few conversions as possible. It will then upload those files to your Nextcloud account.

## How to install
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


## Join the team 👪
Feel free to contribute, you can [submit issues here](https://github.com/thijstakken/MusicService/issues) and [fix issues/bugs, improve the application!](#developer-instructions-)

### Developer instructions 👩🏻‍💻👨🏻‍💻
System requirements: Have [Docker (Desktop or Engine)](https://www.docker.com/) installed on your system <br/>
Techniques: [Python](https://www.python.org/), [Docker](https://www.docker.com/), [youtube-dl](https://youtube-dl.org/) and [WebDAV](http://www.webdav.org/)

1. 🤠 Git clone the project with `git clone https://github.com/thijstakken/MusicService.git`
2. 🐛 [Pick a issue from the list or create a new issue and use that one](https://github.com/thijstakken/MusicService/issues)
3. 🐍 Start editing the code (Python)
4. 🏗 To build your new image, open a command line in the project folder and run `docker build -t musicservice:dev .`
5. 🧪 For testing, there is a good tool to use. [Nextcloud has a website](https://try.nextcloud.com/) where it will create a Nextcloud test environment. Select the "Instant trial" and you get a fresh environment for 60 minutes to play around. This way we can safely experiment with new code and functions. Copy the username into NCUSERNAME and the password is always: demo <br/>

You can use this base developer Docker command, and change it to your needs to get started:
```
docker run \
 --name musicservice \
 --restart=no \
 -v musicdatabase:/usr/app/src/database/ \
 -v musiccache:/usr/app/src/music/ \
 -e REMOTE_DIRECTORY= \
 -e URL=https://demo1.nextcloud.com/remote.php/dav/files/wpS97kPjnDJo6gGQ/ \
 -e NCUSERNAME=wpS97kPjnDJo6gGQ \
 -e NCPASSWORD=demo \
 -e INTERVAL=0 \
 --network=host \
musicservice:dev
```

6. 🎉 Create a branch and make your changes. When committing changes please use [Gitmoji](https://gitmoji.dev/) and [close the corresponding issue with "fixed"](https://github.com/gitbucket/gitbucket/wiki/How-to-Close-Reference-issues-and-pull-request) and the number of the issue `git commit -m ":bug: fixed #21 Your commit message"`
7. ⬆ Create a [pull request](https://github.com/thijstakken/MusicService/pulls)
8. 🚀 Wait for it to be reviewed and merged!

Use at your own risk, never trust the code of a random dude on the internet without first checking it yourself :)
