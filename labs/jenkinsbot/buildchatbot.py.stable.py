#
# buildchatbot - Monitors Jenkins builds and sends notifications to a Skype chat
#
# Copyright (c) 2012 Mirko Nasato - All rights reserved.
# Licensed under the BSD 2-clause license; see LICENSE.txt
#
import platform
import Skype4Py # http://skype4py.sourceforge.net/doc/html/
import jenkinsapi
from time import sleep
from urllib import urlopen
from Skype4Py import Skype
from xml.etree import ElementTree
from jenkinsapi.jenkins import Jenkins

JENKINS_URL = 'http://10.42.0.123:8080/jenkins/'
SKYPE_CHAT = '#eljoujat/$jenkins.printemps;8a33eaa7b369830e'
UPDATE_INTERVAL = 15  # seconds
MESSAGE_PREFIX = '[Jenkins] '

class Build:
  def __init__(self, attrs):
    self.name = attrs['name']
    self.number = attrs['lastBuildLabel']
    self.status = attrs['lastBuildStatus']

class BuildMonitor:

  def __init__(self, listener):
    self.builds = None
    self.listener = listener

  def loop(self):
    while True:
      try:
        self.check_for_new_builds()
      except IOError as e:
        print 'WARNING! update failed:', e.strerror
      sleep(UPDATE_INTERVAL)

  def check_for_new_builds(self):
    builds = self.fetch_builds()
    if self.builds is not None:
      for build in builds.values():
        name = build.name
        if not self.builds.has_key(name):
          self.handle_new_build(build, None)
        elif build.number != self.builds[name].number:
          self.handle_new_build(build, self.builds[name].status)
    self.builds = builds

  def handle_new_build(self, build, old_status):
    transition = (old_status, build.status)
    if transition == ('Failure', 'Failure'):
      self.listener.notify(build, '(rain) Still failing')
    elif transition == ('Failure', 'Success'):
      self.listener.notify(build, '(sun) Fixed')
    elif build.status == 'Success':
       self.listener.notify(build, '(sun) Success')
    elif build.status == 'Failure':
      self.listener.notify(build, '(rain) Failed')

  def fetch_builds(self):
    builds = {}
    response = urlopen(JENKINS_URL +'/cc.xml')
    projects = ElementTree.parse(response).getroot()
    for project in projects.iter('Project'):
      build = Build(project.attrib)
      builds[build.name] = build
    return builds

class BuildNotifier:

  def __init__(self):
    if platform.system() == 'Windows':
      skype = Skype()
    else:
      skype = Skype(Transport='x11')
    skype.Attach()
    self.chat = skype.Chat(SKYPE_CHAT)
    skype.OnMessageStatus = self.MessageStatus

  def notify(self, build, event):
    message = event +': Job'+ build.name +' - '+ JENKINS_URL +'/job/'+ build.name +'/'+ build.number +'/'
    print message
    self.chat.SendMessage(MESSAGE_PREFIX + message)

  def MessageStatus(self, Message, Status):
        """ Event handler for Skype chats """
        print "status is "+Status
        if Status == Skype4Py.cmsReceived:
            print "Message '%s' received from user %s", Message.Body, Message.FromHandle
            if Message.Body=='build':
                j = Jenkins('http://10.42.0.123:8080/jenkins/')
                j.build_job('Build')
                print 'command jenkins received'
            
if __name__ == '__main__':
  try:
    BuildMonitor(BuildNotifier()).loop()
  except KeyboardInterrupt:
    pass


class Hudson():
    def StartJob(self, server, port, jobname, waitForCompletion = False):
        args = ["-s", "http://%s:%s/hudson/" % (server, port), "build", jobname]
        if waitForCompletion: args.append("-s")
        CLI.main(args)

