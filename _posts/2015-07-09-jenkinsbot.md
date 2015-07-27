---
title: "How to use Docker to build a Skype Robot controlling  Jenkins?"
layout: post
og_image_url: "http://eljoujat.github.io/images/jenkinsbot_schma.png"
description: "How to use Docker to build a Skype Robot communicating with jenkins ? "
disqus_comments: true
---


> “There is no greater agony than bearing an untold story inside you.” .
[Maya Angelou](http://www.mayaangelou.com/)

Where i work, Jenkins is what we use for continuous integration. Skype is what we use to communicate.
Now imagine with me that every day at least 6 times I'm being asked to run a build, another 6  to check the status of the build!  another 6 to run a deploy.

And guess what ?! another 6 times to checks the status of the deploy and another 4 questions why the platform is down ?!!

![Dolor de Cabeza...](/images/dolor-de-cabeza.jpg)

All this because some managers are too scared to let  non-technical person touch Jenkins, and some of the non-technical persons are too lazy to take the initiative to know how to run or check Jenkins's jobs.

 I was getting annoyed and bored with this repeatedly tasks when i decided to build a Robot and delegate the task to him!

So every request is sent directly to him as a command, he performs the action automatically and listens for any change on the status of the Jenkins job, if he detects any change or transitions, he sends us a notification.

![Dolor de Cabeza...](/images/gif_demo.gif)](/images/gif_demo.gif)

The robot is just s python script running on the background as demon,  using Skype4Py and Jenkins API module, and some basic logic that can easily extended.

![Communication Diagramm](/images/jenkinsbot_schma.png)

Things are not so easy as it looks and i will present step by step how i built a functional Robot !

First we cannot run two instances of Skype on the same machine, and i could not use another windows machine, I had access to the server where Jenkins is installed: so why not install Skype there and run the python script?

The Server has no GUI! that was not an issue, I had only to forward X11 socket to my machine, the probleme was that there is no installable version of Skype on that server.

Docker is what i thought of to solve the problem , it was time for free shopping from [dockerhub](https://hub.docker.com/) !

I used [python:2.7.10](https://registry.hub.docker.com/u/library/python/) as a base image for my new docker file, and added the instruction to install Skype inspired from [jess/skype](https://registry.hub.docker.com/u/jess/skype/dockerfile/)

{% highlight docker %}
FROM python:2.7.10

MAINTAINER Youssef El Jaoujat <eljoujat@gmail.com>

# Tell debconf to run in non-interactive mode
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -f install --fix-missing
# Setup multiarch because Skype is 32bit only
# Make sure the repository information is up to date
RUN dpkg --add-architecture i386 && \
 apt-get update && apt-get install -y \
 curl \
 --no-install-recommends
# Install Skype
RUN curl http://download.skype.com/linux/skype-debian_4.3.0.37-1_i386.deb -o /usr/src/skype.deb
RUN dpkg -i /usr/src/skype.deb || true

# Automatically detect and install dependencies
RUN apt-get -fy install --fix-missing
RUN rm -rf /var/lib/apt/lists/* # pureg temp data
# Start Skype
ENTRYPOINT ["skype"]

{% endhighlight %}

To build this Docker just execute from the command line  :
 {% highlight bash %}
 docker build -t eljoujat/skype .
 {% endhighlight %}

At this point, i have a docker container with Skype and Python installed inside.
To test the container , just run the container
{% highlight bash %}
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix  -e DISPLAY=unix$DISPLAY --device /dev/snd  eljoujat/skype
{% endhighlight %}

if you get an error with the x11 protocols , just run the following command to grant access to everyone
{% highlight bash %}
xhost +
{% endhighlight %}

Our Python uses two modules  that need to be installed.
we have just to add the instruction on the Docker file and rebuild the image.
{% highlight docker %}
## Install Python modules
RUN apt-get install -y python-pip && \
    pip install Skype4Py && \
    pip install jenkinsapi
{% endhighlight %}

Next step is to make the script available inside the image so we can execute.

A best practice when working with docker  is decoupling applications into multiple containers,
For the sake of simplicity, I did not completely respect this rule, but it's simple to apply with the script and make things very easy.

So, to do it  I had just to use '-v' option when running the docker image


{% highlight bash %}
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -v /media/eljaoujat/Linux/job/labs/docker/skype:/scripts/scripts -e DISPLAY=unix$DISPLAY --device /dev/snd  eljoujat/skype:V1.1
{% endhighlight %}

 */media/eljaoujat/Linux/job/labs/docker/skype* is my locale folder and */scripts/scripts* will be created inside the container and will be mapped with my locale folder


When running the image, the skype get executed ...oups !

i have to accept the term of Use !

![accept the term of Use](/images/docker_skype_001.png)

And login !
![accept the term of Use](/images/docker_skype_002.png)

I have no problem with the term of Use (or I have !?) and login, but doing it each time I run the container is not good at all.

I searched for a solution to automate this on the docker file but with no help, there is no argument we can pass to skype so he will connect automatically.

The only solution I found is to use the commit command of docker.

this command allows you to make the change directly on the running container and create a new image from this changes,
it was so easy and simple, i had just to accept the terms, login with the remember me option .

![accept the term of Use](/images/docker_skype_003.png)

and Commit,
{% highlight bash %}
docker commit b2ec5c9e295e eljoujat/skype:v.1.1
{% endhighlight %}

b2ec5c9e295e is the container ID, can be obtainerd by running:
{% highlight bash %}
docker ps
{% endhighlight %}

after that I fall in love with docker instantly .

let's check what happens inside the Container, and test our script . To do this we have to access by ssh, which has to be added to the docker file and rebuild the image.

A better solution is to use [nsenter](https://github.com/jpetazzo/nsenter) .
to install run the following command

{% highlight bash %}
docker run --rm -v /usr/local/bin:/target jpetazzo/nsenter
{% endhighlight %}

To use nsenter with a running container we should first get his ID

![accept the term of Use](/images/docker_skype_004.png)

 Get his PID
{% highlight bash %}
PID=$(docker inspect --format {{.State.Pid}} 1d46c2cb556c)
 {% endhighlight %}

Then use nsenter
{% highlight bash %}
sudo nsenter  --target $PID --mount  --uts --ipc --net --pid
 {% endhighlight %}

After lsing the /scrtips directory inside the container we found our python script.

![accept the term of Use](/images/docker_skype_005.png)

we can also run it and see that's work well.

At this point all what it's left to do , is to run the script automatically when the container start.

A good solution I found for this is to use [supervisor](http://supervisord.org/).
supervisor is a process control system and when it's added to the container it will allow to execute as many processes as we want, we have just to configure them.
In our case, we want to execute our pyhton script once the container start, a possible configuration file coud be :

{% highlight bash %}
[supervisord]
nodaemon=false

[include]
files = /etc/supervisor/conf.d/*.conf

[program:skype]
command=python /scripts/buildchatbot.py
autostart=true

autorestart=true
startretries=20
stderr_logfile=/opt/nodehook.err.log
stdout_logfile=/opt/nodehook.out.log
{% endhighlight %}

So I added supervisor and rebuilt the image with a higher tag version.

The final dockerfile version is  :

{% highlight docker %}
FROM python:2.7.10


MAINTAINER Youssef El Jaoujat <eljoujat@gmail.com>



# Tell debconf to run in non-interactive mode
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -f install --fix-missing
# Setup multiarch because Skype is 32bit only
# Make sure the repository information is up to date
RUN dpkg --add-architecture i386 && \
	apt-get update && apt-get install -y \
	curl \
	--no-install-recommends




# Install Skype
RUN curl http://download.skype.com/linux/skype-debian_4.3.0.37-1_i386.deb -o /usr/src/skype.deb
RUN dpkg -i /usr/src/skype.deb || true
RUN apt-get -fy install --fix-missing					# Automatically detect and install dependencies
RUN rm -rf /var/lib/apt/lists/* # pureg temp data


# Install Supervisor
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade

# supervisor installation &&
# create directory for child images to store configuration in
RUN apt-get -y install supervisor && \
  mkdir -p /var/log/supervisor && \
  mkdir -p /etc/supervisor/conf.d

# supervisor base configuration

## Install skype4py and jenkinsapi modules

RUN apt-get install -y python-pip && \
    pip install Skype4Py && \
    pip install jenkinsapi

# add the Supervisor config
ADD supervisor.conf /etc/supervisor.conf


CMD [ "sh", "-c", " supervisord -c /etc/supervisor.conf && skype" ]

{% endhighlight %}


- To build :

{% highlight bash %}
docker build -t eljoujat/skype:V1.2 .
{% endhighlight %}

- To run  :
{% highlight bash %}
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -v /media/eljaoujat/Linux/job/labs/docker/skype:/scripts/scripts -e DISPLAY=unix$DISPLAY --device /dev/snd  eljoujat/skype:V1.2
{% endhighlight %}

- To test  :  just send a messgae to the jenkins robot telling him to run a job .


> “I believe that there is always an other way to do it, and i hope that you let me know .”
