---
title: "How to use Docker to build a Skype Bot controlling  Jenkins!"
layout: post
og_image_url: "https://eljoujat.github.io/images/jenkinsbot_schma.png"
description: "How to use Docker to build a Skype Bot communicating with jenkins! "
disqus_comments: true
---

> "Besides black art, there is only automation and mechanization."
> — [Federico García Lorca](https://en.wikipedia.org/wiki/Federico_Garc%C3%ADa_Lorca)

At my workplace, we use Jenkins for continuous integration and Skype for communication.
Now, imagine being asked at least six times a day to run a build, another six times to check its status, another six to deploy, and yet another six to verify the deployment.
And of course, four more times to explain why the platform is down!

![Dolor de Cabeza...](/images/dolor-de-cabeza.jpg)

This happens because some managers are too afraid to let non-technical staff touch Jenkins, and some non-technical people are too lazy to learn how to use it themselves.

I was getting frustrated with these repetitive tasks, so I decided to build a bot to handle them for me!

Now, every request is sent directly to the bot as a command. It performs the action automatically and listens for any status changes in the Jenkins job. If it detects a transition, it sends a notification.

[![Dolor de Cabeza...](/images/gif_demo.gif)](/images/gif_demo.gif)

The bot is simply a Python script running in the background as a daemon, using Skype4Py and the Jenkins API module. The logic is basic but easily extendable.

![Communication Diagram](/images/jenkinsbot_schma.png)

Things weren’t as simple as they seemed, so I'll explain step by step how I built a functional bot.

### Running Skype in a Docker Container

First, I couldn't run two instances of Skype on the same machine, and I didn’t have another Windows machine available. However, I did have access to the server where Jenkins was installed.

The problem? The server had no GUI, and no installable version of Skype.

The solution? **Docker!**

I used the [python:2.7.10](https://registry.hub.docker.com/u/library/python/) image as a base for my Dockerfile and added instructions to install Skype, inspired by [jess/skype](https://registry.hub.docker.com/u/jess/skype/dockerfile/).

```dockerfile
FROM python:2.7.10

MAINTAINER Youssef El Jaoujat <eljoujat@gmail.com>

# Tell debconf to run in non-interactive mode
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -f install --fix-missing
# Setup multiarch because Skype is 32-bit only
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y curl --no-install-recommends

# Install Skype
RUN curl -o /usr/src/skype.deb http://download.skype.com/linux/skype-debian_4.3.0.37-1_i386.deb
RUN dpkg -i /usr/src/skype.deb || true
RUN apt-get -fy install --fix-missing
RUN rm -rf /var/lib/apt/lists/* # Purge temp data

# Start Skype
ENTRYPOINT ["skype"]
```

To build the Docker image, run:

```bash
docker build -t eljoujat/skype .
```

Now, to test the container:

```bash
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY --device /dev/snd eljoujat/skype
```

If you get an error related to X11 protocols, run:

```bash
xhost +
```

### Installing Python Modules

We need two Python modules: `Skype4Py` and `jenkinsapi`. To install them inside the container, update the Dockerfile:

```dockerfile
## Install Python modules
RUN apt-get install -y python-pip && \
    pip install Skype4Py && \
    pip install jenkinsapi
```

### Mounting the Script into the Container

A best practice with Docker is to decouple applications into multiple containers.
For simplicity, I mapped my local script directory inside the container using the `-v` option:

```bash
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -v /media/eljaoujat/Linux/job/labs/docker/skype:/scripts -e DISPLAY=unix$DISPLAY --device /dev/snd eljoujat/skype:V1.1
```

### Persisting Skype Login

When running the image, Skype launches, but I have to manually accept the Terms of Use and log in each time.
Since there’s no argument to auto-login, I used Docker's `commit` command to create an image with my logged-in session.

After logging in with the "Remember Me" option enabled, I ran:

```bash
docker commit <container_id> eljoujat/skype:v1.1
```

To get the container ID, run:

```bash
docker ps
```

### Accessing the Running Container

To debug inside the running container, I used `nsenter`:

```bash
docker run --rm -v /usr/local/bin:/target jpetazzo/nsenter
```

Then, to enter the container:

```bash
PID=$(docker inspect --format {{.State.Pid}} <container_id>)
sudo nsenter --target $PID --mount --uts --ipc --net --pid
```

Inside, I could verify that my Python script was present and working.

### Running the Bot on Container Startup

To automate script execution, I used **supervisor**, a process control system. Here’s the config file:

```ini
[supervisord]
nodaemon=false

[include]
files = /etc/supervisor/conf.d/*.conf

[program:skype]
command=python /scripts/buildchatbot.py
autostart=true
autorestart=true
startretries=20
stderr_logfile=/opt/skypebot.err.log
stdout_logfile=/opt/skypebot.out.log
```

### Final Dockerfile

```dockerfile
FROM python:2.7.10

MAINTAINER Youssef El Jaoujat <eljoujat@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -f install --fix-missing
RUN dpkg --add-architecture i386 && \
    apt-get update && apt-get install -y curl supervisor --no-install-recommends

# Install Skype
RUN curl -o /usr/src/skype.deb http://download.skype.com/linux/skype-debian_4.3.0.37-1_i386.deb
RUN dpkg -i /usr/src/skype.deb || true
RUN apt-get -fy install --fix-missing
RUN rm -rf /var/lib/apt/lists/*

# Install Python modules
RUN apt-get install -y python-pip && \
    pip install Skype4Py jenkinsapi

# Add Supervisor config
ADD supervisor.conf /etc/supervisor.conf

CMD [ "sh", "-c", "supervisord -c /etc/supervisor.conf && skype" ]
```

### Running the Final Version

```bash
docker build -t eljoujat/skype:V1.2 .
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -v /media/eljaoujat/Linux/job/labs/docker/skype:/scripts -e DISPLAY=unix$DISPLAY --device /dev/snd eljoujat/skype:V1.2
```


- To test  :  just send a messgae to the jenkins Bot telling him to run a job .


> “I believe that there is always an other way to do it, and i hope that you let me know .”
