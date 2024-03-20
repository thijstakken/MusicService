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

<br>

<img src="images/WebDAVURL.png" alt="syncShowcase" align="right" width="220px"/>

2. Configure `URL` (required):

    1. Go to your Nextcloud website
    2. Go to the "files" menu at the top
    3. Now in the lower left corner, select "Settings"
    4. Copy the whole WebDAV URL you see there
    5. And place it after the `URL=`

<br>
<br>
<br>
<br>


3. Configure `DIRECTORY` (required): <br/>

    - Option 1: You can leave it empty like this `-e DIRECTORY= \`, then it will save the files to the root directory off your cloud storage. (not recommended) 
    
    <br>

    - Option 2: Or you can specify a custom directory, like your music folder:<br>
    1. Navigate to your music folder in Nextcloud 
    2. In the URL you have to copy the path, everything between `dir=` and the `&fileid=2274`
    3. And then copy it to the DIRECTORY variable, example: `/some/01%20my%20music`

    <img src="images\DirectoryLocationVariantBackup.png" alt="syncShowcase" width="600px"/>

<br>
<br>

<img src="images/ncusername.png" alt="syncShowcase" align="right" width="160px"/>

4. Configure `USERNAME` (required): <br>
    1. Go to your Nextcloud webpage and and click on your user-icon in the top right
    2. Click "View profile"
    3. Copy and paste your username in the USERNAME variable
    
<br>
<br>
<br>
<br>
<br>
<br>
<br>

5. Configure `PASSWORD` (required): <br/>

    - Option 1: (account without 2FA multifactor)
    1. Copy your password into the PASSWORD variable
    
    <br>
    
    <img src="images/ncusername.png" alt="syncShowcase" align="right" width="160px"/>
    

    - Option 2: (account has 2FA multifactor protection)
    1. Go to the right top corner of your Nextcloud website and click the user-icon 
    2. Click on `Settings`

    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>

    <img src="images/securityNavigation.png" alt="syncShowcase" align="right" width="160px"/>

    3. In the left bar, go to "Security" 

    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>
    <br>

    4. Scroll down to the bottom where you will find `Devices & sessions`

    <img src="images/generateAppPassword.png" alt="syncShowcase" width="500px"/>

    5. Fill in an app name like `musicservice`
    6. Click `Create new app password`
    7. Copy the code that appears (53Xqg-...) into the PASSWORD variable


    ![Copy this app password](images/CredentialGenerated.png)

<br>

6. Configure `INTERVAL` (optional): <br>
By default it's set to 5 if you don't specify anything. This is true even if you leave the whole INTERVAL variable out of the command. <br>
If you want to run the script more often or less often, you can just put in a number. 

- It's in minutes, so a `10` will represent 10 minutes. The program will then run with intervals of 10 minutes. 
- If you only want to run the script one time. You can set the number to `0` and then the script will not run on shedule and just stop after one run.

<br>

7. Open a terminal and run your command!
    - If you did the steps with the docker-compose file, do `docker compose up -d` (make sure your command line interface is active in the same directory as where the docker-compose.yml file lives).
    - If you did the steps with the docker run command, paste it in your command line interface and run it.
<br>
8. That's all! If everything is correct, it will create the container, mount the volumes with the configuration and then do it's first run. Let it run for a minute or so. If everything works you should see a new folder and song in your cloud storage. If that happened everything is working fine. <br>
But if this is not the case, the program crashed or it's taking longer then 5 minutes, then you should check out the logs. <br>

9. Check the logs (optional): <br>
To check a crashed container or just have a peek at the logs, you can run this command on your terminal `docker logs musicservice` and it will display the logs for you. This is how you can do debugging, find out if everything is working like it should or if there are any errors.

<br>

## Managing your playlist list

> :information_source: **Tip**: You can update the playlists file while the container is running. If you made any changes, they will be in effect the next time it checks for newly added music. Default `INTERVAL` is 5 minutes.

1. You can update which playlists to download here: `/config/playlists` 
2. On your machine open up a terminal.
3. With `docker volume inspect config` you can see the directory location of the volume.
4. Go to that directory, go into the `_data` directory and there you will find the `playlists` file, 
5. Edit the `playlists` file with your favorite editor like Nano :), and add every playlist/song that you want to add **as a new line**. Like this:
```
youtube.com/playlist1
youtube.com/playlist2
youtube.com/video3
```
6. Save the file, and the next time the container runs or checks for newly added songs, it will look at the playlists file for any updates.

<br>

## Join the team 👪
Feel free to contribute, you can [submit issues here](https://github.com/thijstakken/MusicService/issues) and [fix issues/bugs, improve the application!](https://github.com/thijstakken/MusicService/wiki/Development-technical)

<br>

Use at your own risk, never trust the code of a random dude on the internet without first checking it yourself :)
