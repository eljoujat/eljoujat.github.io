---
title: How did I write my first post?
layout: post
og_image_url: 'http://eljoujat.github.io/images/blogger_joke.jpg'
description: 'A step by step guide on how to create your blog with Github and Jekyll '
published: true
---

> "There is no greater agony than bearing an untold story inside you."
[Maya Angelou](http://www.mayaangelou.com/)

I'm a programmer, and I believe that a good programmer [should have a blog](http://architects.dzone.com/articles/why-programmers-should-have). This week, I made the decision to write my first post. Before starting to write, I had to answer some questions:

- What should I blog about?
- Which blogging platform should I use?

## Blogging about ...?

This was the most difficult question to answer, as I thought for a long time that I had nothing valuable to share...

I was wrong all along. What's obvious to me could be amazing for others.  

So, blogging about...

![Blog about ...](/images/blogger_joke.jpg)

Every programming experiment I do, every new software concept I learn or wish to learn. Also, in my daily job, I face problems that take me time to solve, so I will write posts describing how I solved them. I will write posts about every idea that finds its way into my mind.

## Ghost, Medium, Blogger... Which blogging platform to use?

I start my day by reading what's new on [Hacker News](https://news.ycombinator.com/news), and most of the articles are posts hosted on platforms like [Medium](https://medium.com/), [Svbtle](https://svbtle.com/), [Blogger](https://www.blogger.com), and [Ghost](https://ghost.org/). Each one of these platforms has pros and cons that I will not detail here.

I made a short list of the features I need:

- Free hosting ☺
- Programmer-friendly: allows writing code with features like formatting, syntax highlighting, etc.
- Simple and minimalist
- Easy and powerful customization
- Allows fast writing and even faster publishing

[Jekyll](http://jekyllrb.com/) with [GitHub Pages](http://pages.github.com/) as the free hosting solution is the best choice for me.

## Start Blogging

### Create the blog

GitHub provides a simple and easy-to-follow step-by-step [guide](https://pages.github.com/) to create your blog. I just followed the guide.

### Install Jekyll

Installing Jekyll is a simple task unless you are a Windows user like me.

- Download and install Ruby from [Ruby Installer](http://rubyinstaller.org/downloads#download-links)
- Download and install Ruby DevKit from [Ruby Dev Kit](http://rubyinstaller.org/downloads#download-links)
- Extract the DevKit zip to a local directory and add it to the Windows PATH variable.
- Open up a command prompt and type: {% highlight ruby %} gem install bundler {% endhighlight %}

If you encounter this error:
{% highlight ruby %}
ERROR:  While executing gem (Encoding::UndefinedConversionError)
    U+2019 to CP850 in the conversion from UTF-16LE to UTF-8 to CP850.
{% endhighlight %}

don't panic! Just type {% highlight ruby %} chcp 1252 {% endhighlight %} and then re-execute the previous command.

- Execute {% highlight ruby %} bundler --version {% endhighlight %} to verify if everything went well.

### Structure of the Blog

I took this list of [Sites using Jekyll](http://jekyllrb.com/docs/sites/) as a starting point to understand how I should structure my blog and apply some best practices.

I was especially inspired by the blog of [Rasmus Andersson](http://rsms.me/) ([Source](https://github.com/rsms/rsms.github.com)).

#### Layouts:

Layouts allow you to define a structure and use it as needed with just a declaration.

I defined two layouts:

- The default layout for the pages (header, footer, sidebars, comments section).
- The post layout, which includes the default layout.

[Code source](https://github.com/eljoujat/eljoujat.github.io/tree/master/_layouts)

### Includes:

I used this feature to include Google Analytics code and the [Disqus comments engine](https://disqus.com/).

[Code source](https://github.com/eljoujat/eljoujat.github.io/tree/master/_includes)

### Write the first post

Once the structure of the blog is well defined, all that's left is to put my ideas into a text format that Jekyll and GitHub can render to obtain what you are seeing and reading right now.

***

> "I believe that there is always another way to do it, and I hope that you let me know."

