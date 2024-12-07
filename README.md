 #This is a application loadbalancer 
 
 This is docker setup where loadbalancer is facing internet and it exposed on port 5000
 
 The backend server are listening on port 80
 
 To run this you must install docker and docker-compose.
 
 To run this execute  " Docker-compose up -d  "
 
 This command complete the setup of one loadbalancer and two bankend servers.
 
 To check the loadbalancer jush curl localhost:5000
 
 You get mutiple backend server information when you refresh the page.
 
 Here Roundrobin algorithm is used to distribute the load. 
 
You can change the .yml for to change no of backend server.

loadbalancer is uploaded to dockerhub ajettesla/sdnprojectlb:1 

loadbalancer is uploaded to dockerhub ajettesla/sdnprojectapp:1 . In :2 version added weighited loadbalanceing. 

If you obeserver docker-composer.yaml file there you can see env variable where we update the backend server. 

If you are using ajettesla/sdnprojectapp:1 then formate of 'BACKEND_SERVERS: "backend1:80,backend2:80"' if you wanted use weighted loadbalancing then use 
BACKEND_SERVERS: "backend1:80|2,backend2:80|1" for ajettesla/sdnprojectlb:2 .


How this weight work ? 

from above example probabilty of picking backend1 is 2/(2+1). I think you get this.

if you change anything in you dockerfile. You must build it."docker build -t <yourdockerhubid>/<nameofcontainer>:<version> -f <nameofthedockerfile> ( or you can use present directory by {./} but docker file name must be Dockerfile)

After that you must push the repository to you dockerhub by docker push <containername> (login into your dockerhub before pushing the container.)

