---
title: The hybris lean developper
layout: post
og_image_url: 'http://eljoujat.github.io/images/blogger_joke.jpg'
description: 'How to avoid wasting your time and be  super productive leand developper'
disqus_comments: true
published: true
lang: en
ref: productivity
---



##Hybris Build system

Hybris build system depends heavily on ant macros and target, basicaly you can get the list of all available possibles target by {% highlight  antlr %} ant -p {% endhighlight %}

### Compilation

* Optimize the localextention file , i came across many localextention that activate  extensions not used . so be carefull  .
* Activate the build parallel : build.parallel=true.
* when you are not developing unit tests, it's better to deactivate test class scanner and compilation.
* Deactivate datamodel checking if no data model was changed  


##Hybris start

* the nature of generated extesion i very critcal, an extension should not have a aweb nature if it's not expose a web interface.
* A Web nature open a  new gate to your platform that shoulds handle by security policies , somtimes we didn't even it exists until pentest if .
* A web nature implies an addition spring web context to initialise and load , costly operations that impacts the startup performance .
* Do not activate extension which will not be used
* Optimize your tomcat startup time :
  * Activate parallel startup
  * Let only the used .
* Deactivate junit tenant  : hybris will start as times as there activated tenants 

##Hybris Dev

##Hybris



> “I believe that there is always the other way to do it, and I hope that you let me know .”
