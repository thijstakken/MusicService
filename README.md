there is a new environment variable called: DATABASE_URL
through that variable you can configure your own database to run the app with

<img src="images/normalLogo.png" alt="MusicServiceLogo" align="left" width="130"/>

# Music sync Service (youtube-dl-sync) <br> ![Release version](https://img.shields.io/github/v/release/thijstakken/musicservice?label=latest) ![Docker Pulls](https://img.shields.io/docker/pulls/thijstakken/musicservice?label=downloads) ![DevOps Build](https://img.shields.io/azure-devops/build/mydevCloudThijsHVA/d94ee522-5f5b-43cf-a9e3-175c5cf1fb03/3) ![License](https://img.shields.io/github/license/thijstakken/musicservice) ![Issues](https://img.shields.io/github/issues/thijstakken/musicservice)

<br>

**A tool that synchronizes your YouTube playlists and other music providers with your Cloud Storage like Nextcloud as MP3s.**

### What does it do? ✨
- 🎵 Downloads your music from YouTube, SoundCloud [and many more](http://ytdl-org.github.io/youtube-dl/supportedsites.html)
- 😁 Automatically monitors your playlists for newly added music
- 🔄 Converts video files to the highest quality MP3 possible
- &nbsp;☁ &nbsp;Uploads your music as MP3 to your Cloud Storage account. Supports all Cloud providers with WebDAV compatibility: Nextcloud, ownCloud, pCloud, STACK [and many more](https://community.cryptomator.org/t/webdav-urls-of-common-cloud-storage-services/75)
- 🖼 Adds coverart to your MP3s automatically
- 🗃 It's aware of the songs that have already been downloaded. This saves a lot of time since they don't get redownloaded every time the application runs again.

<br>
<img src="images/syncShowcase.png" alt="syncShowcase" width="700"/>
<br>
<br>

## How to install
The Music Service is a microservice application and runs as a [Docker container](https://www.docker.com/resources/what-container/). Because of using Docker, every installation runs the same, for everyone. This brings programming efficiency and improves reliability. [Docker image release](https://hub.docker.com/r/thijstakken/musicservice)

> :warning: **You must have Docker installed**: Either the Docker [Desktop](https://www.docker.com/products/docker-desktop/) (with GUI) or [Engine](https://docs.docker.com/engine/install/) (no GUI) installed on your system.

> :information_source: **Tip**: If you just want to test this application, luckily there is a good tool to use. Just do `docker run -d -p 8080:80 nextcloud` to start a fresh Nextcloud environment. When started, go to `http://localhost:8080/` in some cases you have to replace `localhost` with your computers IP. And you can continue to follow the steps below!

> :information_source: **Recommendation**: For the best experience, install this container on a computer/server which runs 24/7, so you will always have your music in sync.

<br>

1. Prepare the code (required):
    - Option 1 Docker Compose (recommended): Copy the [docker-compose](docker-compose.yml) file contents to your editor and follow the steps
    - Option 2 (Docker run): Copy the code below to your favorite editor, Notepad, Word etc. 

```
docker run -d \
 --name musicservice \
 --restart=always \
 -v config:/config \
 -v musiccache:/music \
 -e URL=https://demo2.nextcloud.com/remote.php/dav/files/kA2kSpbk2tMwCPpB/ \
 -e DIRECTORY=/some/01%20my%20music \
 -e USERNAME=kA2kSpbk2tMwCPpB \
 -e PASSWORD=demo \
 -e INTERVAL=5 \
thijstakken/musicservice:latest
```

Before you can run the docker-compose or docker run command, you will first have to make a few changes.


## How to best migrate from existing youtube-dl solution
If you where already using youtube-dl with the archive function, you probably have an downloaded.txt or similar file with all the songs you have already downloaded.

1. :warning: Shut down the musicservice container first

2. To migrate, just copy the contents of the old file over to the `/config/downloaded` file. You can find that file at the musicdatabase volume

3. Run `docker volume inspect config` at your command line to find the location of that volume on your disk

4. Open the file, paste the old information in and save it.

5. That's it!

<br>

## Join the team 👪
Feel free to contribute, you can [submit issues here](https://github.com/thijstakken/MusicService/issues) and [fix issues/bugs, improve the application!](https://github.com/thijstakken/MusicService/wiki/Development-technical)

<br>

Use at your own risk, never trust the code of a random dude on the internet without first checking it yourself :)
