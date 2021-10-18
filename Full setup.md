
# Django_ANPR



## Steps to setup the project

- Make sure you have both docker and docker-compose installed. (latest versions)
- Clone this repository using ``` https://github.com/robin-jr/anpr-backend-v2.git ```




## To start the server

- Get inside the folder using ``` cd anpr-backend-v2 ```
- Now build the docker image of the project using ``` sudo docker-compose build ```
- Now run ``` sudo docker-compose up ```
- if your terminal stops at some stage, press ``` ctrl+c ``` to terminate 
- then run again ``` sudo docker-compose up ```
- now your terminal should show ``` Watching for file changes with StatReloader ``` which means your server is up and running.


That's it! Now the app is up and running...


- Go ahead and check if it is working by navigating to '``` Server IP ```:8001/anpr/' or '``` Server IP ```:8001/rlvd/' in your browser

### To reflect the change you make in sample database

- To check the running docker containers, use command ``` sudo docker ps ```
- run ``` sudo docker-compose down ``` if u have any containers up
- now run ``` sudo docker container prune ``` then press 'y'
- then run ``` sudo docker volume prune ``` then press 'y'
> Now start the server using the steps given above


### To get the bash inside the container

- To check the running docker containers, use command ``` sudo docker ps ```
- Note the container id of the anpr-backend-v2_app_1 
- To get the bash of the app inside docker, use command ``` sudo docker exec -it container_id /bin/bash ```
- now you got the access to bash inside docker container


### To make migrations in django

- open the bash inside the docker container
- run ``` python manage.py makemigrations ```
- then run ``` python manage.py migrate ```
- if the migrations get terminated due to "table already exist" error apply the migrations one by one (account, admin , auth, authtoken, contenttypes, sessions, anpr, rlvd)
- to apply migrations one by one run  ``` python manage.py migrate migration_name ```



### To create super user

- once you made all the migrations correctly, run ``` python manage.py createsuperuser ```
- enter the username, email, password, confirm password
- once you entered those details, super user will be created
- go to '``` Server IP ```:8001/admin/' then enter your super user credentials there, you will be able to pass through the authenticaion


### To create a normal user

- once you created the super user, go to " ``` Server IP ```:8001/api/accounts/register/ "
- In the content section enter the details for the normal user credentials 
- E.g  ```{
    "username":"user1",
    "email":"user1@email.com",
    "password":"pass",
    "password2":"pass"
    }```
- This might throw an warning page 'Token matching query does not exist.', but the user will be created
- you can check the users in ``` Server IP ```:8001/admin/ inside the accounts section
- now you can login as user inside the rlvd/anpr website


### To note

- Any updates to the project will be reflected realtime because of the volume binding used in docker. So no need to re-build or restart the containers every time a change is made.


### Some configurations to consider:

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
Note: The above configuration is for mysql. Config will change with DB engine used.

2) Request for the static file zip and replace existing anpr > static folder

## To speed up search time:

1) Open a terminal session of mysql server
2) Login to mysql
3) Setup the working database using ``` USE __DATABASE NAME__; ```
4) now run ``` create index license_plates_rlvd_entry_index on license_plates_rlvd (object_id); ```
5) then run ``` create index evidence_cam_entry_index on evidence_cam_img (object_id); ```
6) atlast run ``` create index violations_entry_index on violations (object_id); ```

> Please make sure to run all the above commands correctly. Creating index may take upto a minute. Please stay calm

## Parameters

1. Latest5 - Refreshes every 2 seconds

> Now your server is ready to go


# ANPR Website

## Getting the project running

- Clone this repository using ``` https://github.com/kuttyhub/anpr-website.git ```
- Open the terminal inside the ANPR Website folder
- Install the dependencies by running ``` npm i ```
- Now start the project by typing ```npm start```

## Connecting with the backend

- Navigate to src/api/anpr.ts and change the endpoint to that of the backend
- Edit the following lines
 ```
  export const ENDPOINT = "http://<SERVER IP>:8001/anpr/";
  export const STATIC_ENDPOINT = "http://<SERVER IP>:8001/static/";
  ```
  
  
  
# RLVD Website

## Getting the project running

- Clone this repository using ``` https://github.com/kuttyhub/RLVD-website.git ```
- Open the terminal inside the RLVD Website folder
- Install the dependencies by running ``` npm i ```
- Now start the project by typing ```npm start```

## Connecting with the backend

- Navigate to src/api/anpr.ts and change the endpoint to that of the backend
- Edit the following lines 
```
  export const ENDPOINT = "http://<SERVER IP>:8001/rlvd/";
  export const STATIC_ENDPOINT = "http://<SERVER IP>:8001/static/";
  const AUTH_ENDPOINT = "http://<SERVER IP>:8001/api/accounts/";
  ```
  

That's it! You are good to go.



