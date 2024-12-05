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

loadbalancer is uploaded to dockerhub ajettesla/sdnprojectapp:1 

