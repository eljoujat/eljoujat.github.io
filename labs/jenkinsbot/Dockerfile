FROM python:2.7.10

# make sure the package repository is up to date and update ubuntu



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

## Install Pythin lib

RUN apt-get install -y python-pip && \
    pip install Skype4Py && \
    pip install jenkinsapi
ADD supervisor.conf /etc/supervisor.conf

ADD buildchatbot.py /opt/buildchatbot.py

# default command
#RUN supervisord -c /etc/supervisor.conf

# Start Skype
#CMD skype && supervisord -c /etc/supervisor.conf

CMD [ "sh", "-c", " supervisord -c /etc/supervisor.conf && skype" ]


