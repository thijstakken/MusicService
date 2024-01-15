# uploading files to a server logic
import os
import requests

# webdav

# start uploading the music to the cloud using WebDAV
def uploadmusic(url, username, password, remoteDirectory):
    # Whenever the function is called it will upload all music present in the local music folder
    # At the moment it does not make a distinction between songs from other jobs, it will just upload everything...
    
    # THIS IS TEMPORARY ###
    localDirectory = 'music'
    ###

    print("")
    print('Creating cloud folder structure based on local directories...')
    create_folders(localDirectory, remoteDirectory, url, username, password)

    print("")
    print('Uploading music into the cloud folders...')
    upload_music(remoteDirectory, url, username, password)

    # deleting files is already don in the upload_music function... the delete part could be in a seperate function.

    #print("Clearing local MP3 files since they are no longer needed...")
    #clear_local_music_folder()


# creates directories in the cloud based on the local directory structure
def create_folders(localDirectory, remoteDirectory, url, username, password):
    
    # for every local directory create a directory at the users remote cloud directory
    for localDirectory, dirs, files in os.walk(localDirectory):
        for subdir in dirs:
            
            # construct URl to make calls to
            print(os.path.join(localDirectory, subdir))

            # remove first / from the string to correct the formatting of the URL
            formatRemoteDir = remoteDirectory[1:]

            fullurl = url + formatRemoteDir + "/" + subdir

            # first check if the folder already exists
            existCheck = requests.get(fullurl, auth=(username, password))

            # if the folder does not yet exist (everything except 200 code) then create that directory
            if not existCheck.status_code == 200:
                
            # create directory and do error handling, when an error occurs, it will print the error information and stop the script from running
                try:
                    r = requests.request('MKCOL', fullurl, auth=(username, password))
                    print("")
                    print(r.text)
                    print("Created directory: ")
                    print(r.url)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as erra:           # handle 4xx and 5xx HTTP errors
                    print("HTTP Error: ",erra)
                    raise SystemExit(erra)  
                except requests.exceptions.ConnectionError as errb:     # handle network problems, DNS, refused connections
                    print("Error Connecting: ",errb)
                    raise SystemExit(errb)
                except requests.exceptions.Timeout as errc:             # handle requests that timed out
                    print("Timeout Error: ",errc)
                    raise SystemExit(errc)
                except requests.exceptions.TooManyRedirects as eerd:    # handle too many redirects, when a webserver is wrongly configured
                    print("Too many redirects, the website redirected you too many times: ",eerd)
                    raise SystemExit(eerd)
                except requests.exceptions.RequestException as erre:    # handle all other exceptions which are not handled exclicitly
                    print("Something went wrong: ",erre)
                    raise SystemExit(erre)
            
            # if directory exists print message that is exists and it will skip it
            else:
                print("Directory already exists, skipping: " + fullurl)

    print("Finished creating directories")

# after the neccessary directories have been created we can start to put the music into the folders
# iterates over files and uploads them to the corresponding directory in the cloud
def upload_music(remoteDirectory, url, username, password):
    # THIS IS TEMPORARY
    localDirectory = 'music'
    for root, dirs, files in os.walk(localDirectory):
        for filename in files:
            
            # get full path to the file (example: 'music/example playlist/DEAF KEV - Invincible [NCS Release].mp3')
            path = os.path.join(root, filename)
            
            # removes the first 6 characters "music/" from the path, beacause that piece of the path is not needed and should be ignored
            reduced_path = path[6:]

            # get the folder name in which the file is located (example: 'example playlist')
            subfoldername = os.path.basename(os.path.dirname(reduced_path))
            
            # remove first / from the string to correct the formatting of the URL
            formatRemoteDir = remoteDirectory[1:]

            # construct the full url so we can PUT the file there
            fullurl = url + formatRemoteDir + "/" + subfoldername + "/" + filename
            
            # first check if the folder already exists
            existCheck = requests.get(fullurl, auth=(username, password))
            
            # if the file does not yet exist (everything except 200 code) then create that file
            if not existCheck.status_code == 200:
            # error handling, when an error occurs, it will print the error and stop the script from running
                try:

                    # configure header, set content-type as mpeg and charset to utf-8 to make sure that filenames with special characters are not being misinterpreted
                    headers = {'Content-Type': 'audio/mpeg; charset=utf-8', }
                    
                    # make the put request, this uploads the file
                    r = requests.put(fullurl, data=open(path, 'rb'), headers=headers, auth=(username, password))
                    print("")
                    print(r.text)
                    print("Uploading file: ")
                    print(r.url)
                    r.raise_for_status()
                except requests.exceptions.HTTPError as erra:           # handle 4xx and 5xx HTTP errors
                    print("HTTP Error: ",erra)
                    raise SystemExit(erra)  
                except requests.exceptions.ConnectionError as errb:     # handle network problems, DNS, refused connections
                    print("Error Connecting: ",errb)
                    raise SystemExit(errb)
                except requests.exceptions.Timeout as errc:             # handle requests that timed out
                    print("Timeout Error: ",errc)
                    raise SystemExit(errc)
                except requests.exceptions.TooManyRedirects as eerd:    # handle too many redirects, when a webserver is wrongly configured
                    print("Too many redirects, the website redirected you too many times: ",eerd)
                    raise SystemExit(eerd)
                except requests.exceptions.RequestException as erre:    # handle all other exceptions which are not handled exclicitly
                    print("Something went wrong: ",erre)
                    raise SystemExit(erre)
            
            # if file exists print message that is exists and it will skip it
            else:
                print("File already exists, skipping: " + fullurl)

            # in the event that the file either has been uploaded or already existed, we can delete the local copy
            print("Removing local file,", path, "no longer needed after upload")
            os.remove(path)

        # check if there are any directories left, if there are, we can delete them if they are empty
        # we want to remove unneeded files and dirs so they don't pile up until your storage runs out of space
        for directory in dirs:
            dirToDelete = os.path.join(root, directory)
            
            dirStatus = os.listdir(dirToDelete)

            if len(dirStatus) == 0:
                print("Empty DIRECTORY")
                print("Removing local directory,", dirToDelete, "no longer needed after upload")
                try:
                    os.rmdir(dirToDelete)
                    print("Done...")
                except OSError as error:
                    print(error)
                    print(dirToDelete)

            else:
                print("NOT EMPTY DIRECTORY")
                print("Cannot delete yet...")
            
    
    print("Finished uploading music files")



# ftp/sftp