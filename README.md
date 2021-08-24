# Django_ANPR

Some configurations to consider:

1) Change db configuration in arima > settings.py   
DATABASES = {  
&nbsp;&nbsp;&nbsp;&nbsp;"default": {  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ENGINE": "django.db.backends.mysql",  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"NAME": \<your db name>,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"HOST": "localhost",  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"USER": \<your mysql username>,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"PASSWORD": \<your mysql password>,  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"PORT": "3306",  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"OPTIONS": {"init_command": "SET default_storage_engine=INNODB",},  
&nbsp;&nbsp;}  
  }  
Note: The above configuration is for mysql. Config will change wrt DB engine used.

2) Request for the static file zip and replace existing anpr > static folder

## Parameters

1. Latest5 - Refreshes every 2 seconds


# How to get this working

Considering that we have a lot to setup before starting the project, I've setup DOCKER.
The doker-compose.yaml file has two apps (anpr_backend and mysql). So no need to setup anything beforehand.
The initial sql files to run inside mysql are put in 'Database' folder, and will be run automatically inside the mysql container when starting.

## Steps 

- Make sure you have both docker and docker-compose installed. (latest versions)
- Clone this repository using ``` git clone https://github.com/kuttyhub/anpr-backend.git ```
- Get inside the folder using ``` cd anpr_backend ```
- Now build the docker image of the project and tag it as 'anpr-backend_app:latest' using ``` sudo docker build -t anpr-backend_app:latest . ``` (This exact same tag is referenced in the docker-compose.yaml file)
- Now run ``` sudo docker-compose up ```

That's it! Now the app is up and running...

- To check the running docker containers, use command ``` sudo docker ps ```
- Go ahead and check if it is working by navigating to '127.0.0.1:8000/anpr' in your browser

### To note

- Any updates to the project will be reflected realtime because of the volume binding used in docker. So no need to re-build or restart the containers every time a change is made.
