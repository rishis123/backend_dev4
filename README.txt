Name: Rishi Shah
NetID: rrs244

Challenges Attempted (Tier I/II/III): N/A
Working Endpoint: <Put a working endpoint from PA 4 here (e.g. GET /api/courses/)>

They should all be working, so GET /api/courses is one of them. That said, obviously venv 
and requirements must be installed first.

Your Docker Hub Repository Link:
https://hub.docker.com/r/uptoprshah/cs1998_pa5/tags

Questions:
Explain the concept of containerization in your own words.

Packaging code in a standardized way, so that containers execute the same way
regardless of their environment (e.g., OS and all those components). They are also detached from other containers.


What is the difference between a Docker image and a Docker container?

Docker image is a blueprint with source code and necessary libraries/dependencies, while docker container is one executed instance of the code.

What is the command to list all Docker images?

docker images


What is the command to list all Docker containers?
docker ps for all running containers


What is a Docker tag and what is it used for?

There are specific tags for images that serve as names, and tags within image histories
that represent versions.


What is Docker Hub and what is it used for?

Online repository for Docker images (allows for collab like Github)

What is Docker compose used for?

Defines and runs a docker app

What is the difference between the RUN and CMD commands?

In the way we've used it, RUN installs dependencies from requirements.txt, while
CMD runs the server itself.