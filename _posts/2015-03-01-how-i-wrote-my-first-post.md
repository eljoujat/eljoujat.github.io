---
title: How I wrote my first post ?
layout: post
og_image_url: 'http://eljoujat.github.io/images/blogger_joke.jpg'
description: 'A step by step guide on how to create your blog with Github and Jekyll '
disqus_comments: true
published: true
---


> “There is no greater agony than bearing an untold story inside you.” .
[Maya Angelou](http://www.mayaangelou.com/)

I'm a programmer, I believe that a good programmer [should have a blog](http://architects.dzone.com/articles/why-programmers-should-have). This week I made the decision to write my first post, before start writing, i had to answer some questions :

- What should I blog about ?
- which blogging platform to use ?

##Blogging about ...?

This was the most difficult question to answer, as I thought for a long time that I have no good things share ...

 was wrong all the time, and what's obvious to me could be amazing for others  <iframe width="560" height="315" src="https://www.youtube.com/embed/xcmI5SSQLmE" frameborder="0" allowfullscreen></iframe>


So blogging about ....

![Blog about ...](/images/blogger_joke.jpg)

Every programming experiments I do, every new software notion I learn or I wish to learn. Also On my daily job , I face problems that take me time to solve, so I will write posts describing how I solved them. I will write posts about every idea that found its path to my mind.


## Ghost, Medium, Blogger,... which blogging platform to use ?

I start my day with reading what's new on [Hacker News](https://news.ycombinator.com/news), most of them are posts on blog hosted on platforms , like [Medium](https://medium.com/), [svbtle](https://svbtle.com/), [Blogger](https://www.blogger.com), [ghost](https://ghost.org/). each one of the themes has pros and cons that I will not details here .

I made a short list of what features I need .

- Free hosting ☺ .
- Programmer friendly : allow to write code with features like , formatting, syntax highlighting...
- Simple and minimalist
- Easy and powerful customization
- Allow to write fast and publishing faster.


[Jekyll](http://jekyllrb.com/) with [github pages](http://pages.github.com/) as the free hosting solution are the best choice for me .

## Start Blogging

### Create the blog

Github gives a simple and easy to follow step by step [guide](https://pages.github.com/) to create your blog, I had just follow the guide.

### Install Jekyll

Installation of Jekyll is a simple task unless you are a windows user like me .

- Download and install Ruby from [Ruby Installer](http://rubyinstaller.org/downloads#download-links)
- Download and install Ruby Devkit  from [Ruby Dev Kit](http://rubyinstaller.org/downloads#ownload-links)
- Extract the Dev kit zip to a local directory, and add it to the windows PATH variable.
- Open up a command prompt and type : {% highlight ruby %} gem install Bundle{% endhighlight %}

 If you have this error
{% highlight ruby %}
 ERROR:  While executing gem (Encoding::UndefinedConversionError)
    U+2019 to CP850 in the conversion from UTF-16LE to UTF-8 to CP850.
{% endhighlight %}


 don't panic , just type {% highlight ruby %} chcp 1252 {% endhighlight %} and then re-execute the previous command.

 - Execute {% highlight ruby %}Bundle --version {% endhighlight %} to verify if all went well .

### Structure of the Blog


I took these list of [Sites using Jekyll](http://jekyllrb.com/docs/sites/) , as a starting  point to understand how I should structure my blog and some best practices to apply.

I got especially inspired  by the blog of [Rasmus Andersson](http://rsms.me/)([Source](https://github.com/rsms/rsms.github.com))

#### Layouts :

Layouts allow you to define a structure and used as I want with just a declaration .

I defined two Layouts :

- the default layout for the page (header , footer ,sidebars, comments section) .
- the post layout for the post ,that include the default layout.

 [code source](https://github.com/eljoujat/eljoujat.github.io/tree/master/_layouts)

### Includes :

I used these feature , to include google analytics code and [disqus comments engine ](https://disqus.com/)

[Code source](https://github.com/eljoujat/eljoujat.github.io/tree/master/_includes)

### Write the first post

Once the structure of the blog is well defined, all that's left is to print my ideas in a text format that Jekyll and GitHub can render to obtain what you are seeing and reading right now .

 ***




> “I believe that there is always the other way to do it, and I hope that you let me know .”
