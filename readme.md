# Py_Drop

A python flask app to store files and their data.

## Technologies

* python 3.6
* flask
* sqlite

## Usage

* main.py - sets up the db and has the main app functionality
* helpers.py - the sql functions are in here
* data.db - database used to store file metadata (database is automatically created on app start up)
* /uploads - dir where files will be stored
* tests.sh - used to test apps functions
* run.sh - starts the flask application
* requirements.txt - the dependencies for this app

The app is currently only configured to receive 'txt' files.

#### Docker

I have pushed an image of this app to Docker:

`mudd101/py_drop:latest`

Providing Docker is installed, to grab this from the Docker hub, do the following in your terminal

```
docker login
docker pull mudd101/py_drop:latest
docker run -p 5000:5000 mudd101/py_drop:latest
```
The docker container for py_drop should then start up on the local server.

To make full use of my app, I like using cURL:

```bash
# POST/ 
#Sends text.txt to the app. Also, have file data returned in json format.
curl -i -X POST -F file=@text.txt http://127.0.0.1:5000
# GET/ 
#Have the list of files and their data returned in json format
curl http://127.0.0.1:5000
# GET/a_file_from_the_list
#Have the contants of text.txt returned to the termianl in json format.
curl http://127.0.0.1:5000/text.txt
```

#### Local Set-Up

Alternatively, if not using Docker, there are two simple bash scripts I set up for local testing purposes that are with this repo.

You will need to create a new folder/dir for the uploads folder by typing `mkdir uploads` in the terminal.

The first `run.sh` is used to run the the flask app, which will run on your local server.

The second, `tests.sh` is a simple little bash script which tests the features of `main.py`:

1. It makes a new file, the name specified by user input
2. It sends that file to the app via POST and prints what's returned to the terminal
3. It then sends a get request and prints that output
4. And then sends another get request, this time with the filename of the created file
5. The output is then printed to the terminal

The `tests.sh` can also be used against the Docker container to test it.

To run app in Local Linux env, in terminal type:
```bash
bash run.sh
```
To test the apps features:
```bash
# filename.txt is the user input. Use whatever name you like.
bash tests.sh filename.txt
```
