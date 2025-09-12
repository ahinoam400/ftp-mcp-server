# Docker Workflow
If you don't want to install anything manually in order to run our project, using our docker image is recommended.
Here we will show how to run an existing docker we created already or how to build a new one from scratch.

## Prerequisites
- Docker application (Could be downloaded from here: https://www.docker.com/get-started/)

## Steps
### Build the docker image
Open terminal\ command line in the root directory of this project and run:
`docker build -t mcp-server:v1 .`

### Run the docker
Open terminal\ command line and run (this command will run the docker and delete it when finished):
`docker run -it --rm --name mcp-server mcp-server:v1 sh`
We used port 8000, if you want to change it to another port, instead of the previous command, run this command (insert value to the '<new_port>' inside the command):
`docker run -it --rm -p <new_port>:8000 --name mcp-server mcp-server:v1 sh`
