---
title: "How i wrote my first post !"
layout: post
og_image_url: "http://eljoujat.github.io/images/blogger_joke.jpg"
description: "This is my first post , it took me time to write it so it's worth to write a post about it and how i wrote it!"
disqus_comments: true
---


> “There is no greater agony than bearing an untold story inside you.” .
[Maya Angelou](http://www.mayaangelou.com/) 

I'm programmer, i've always believed that every good progammer [should have a blog](http://architects.dzone.com/articles/why-programmers-should-have). This week i made the decision to write my first post, before writing the first post i had to answer some questions :

- What shoud i blogg about ? 
- which blogging platform to use ?
- then i can start blogging 



##Blogging about ...?


For me This was the most difficult question to answer, as i thoought for a long time that i have no good things share ... 

 was wrong all the time, and what's obvious to me could be amazing for others  <iframe width="560" height="315" src="https://www.youtube.com/embed/xcmI5SSQLmE" frameborder="0" allowfullscreen></iframe>


So blogging about ....

![Blog about ...](/images/blogger_joke.jpg)

Eevery programming experiments i do, every new software notion i learn or i wish to learn. On my daily job tasks, i face problems that take me time to solve, so i will write posts describing how i solve them. I will write posts about every idea that found its path to my mind.

Bref, This blog will be my laboratory.

## Ghost, Medium, Blogger,... which blogging platform to use ?

I start my day with reading what's new on [Hacker News](https://news.ycombinator.com/news), most of them are posts on blog hosted on platforms , like [Medium](https://medium.com/), [svbtle](https://svbtle.com/), [Blogger](https://www.blogger.com), [ghost](https://ghost.org/). each one of theme has pros and cons that i will not details here .

I made a short list of what features i need .

- Free hosting ☺  (a personal domain is not) .
- Progammer freindly :allow to write code with features like , formatting, syntax highliting...
- Simple and minimalist
- Easy and powerful customization 
- Allow to write fast and publishing faster.


[Jekyll](http://jekyllrb.com/) with [github pages](http://pages.github.com/) as free hosting solution was what suited for me the best .

## Start Blogging

### Create the blog

Github give a simple and easye to follow step by step [guide](https://pages.github.com/) to create your blogg, all what one should do is to follow the guide.

i cloned the site into my local post so i can preview any change and validate before publishing to github . 


### Install Jekyll

To Install Jekyll is a simple task, unless you are a windows user like me .

- Download and install Ruby from [Ruby Installer](http://rubyinstaller.org/downloads#download-links)
- Download and install Ruby Devkit  from [Ruby Dev Kit](http://rubyinstaller.org/downloads#ownload-links)
- Extract the Dev kit zip to a local directory, and add it to the windows PATH variable.
- Open up a command prompt and type : `gem install Bundle`

 If you have this error `ERROR:  While executing gem (Encoding::UndefinedConversionError)
    U+2019 to CP850 in conversion from UTF-16LE to UTF-8 to CP850`.

 don't panic , just type `chcp 1252` and then re execute your command. 

 - type `Bundle --version ` to verify if all went well .

### Structuring the Blog Site 


[Sites using Jekyll](http://jekyllrb.com/docs/sites/) is a very good list of sites that i used as starting point to understand how to structure the site and good best practices to use. 

I got inspired a lot by  the site of [Rasmus Andersson](http://rsms.me/)([Source](https://github.com/rsms/rsms.github.com))


{% highlight ruby linenos %}
def show
  puts "Outputting a very lo-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-ong lo-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-ong line"
  @widget = Widget(params[:id])
  respond_to do |format|
    format.html # show.html.erb
    format.json { render json: @widget }
  end
end
{% endhighlight %}











