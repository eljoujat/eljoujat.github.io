---
title: "Writing SAP-Hybris Impex with Style !"
layout: post
lang: en
og_image_url: "http://eljoujat.github.io/images/impex/image004.jpg"
description: "Writing SAP-Hybris Impex with style: An eclipse plugin that will change the way you work with Impex."
disqus_comments: true
---


> Two things that drive us, software development addicts: enthusiasm and laziness...
ANONYMOUS


## The idea behind the current lab.


Impex is a [Sap-hybris](http://hybris.com) specific language in top of SQL to import/export data .

The lack of tools make things difficult when working with Impex, in fact some available options are :

- Web console offered by SAP-hybris:
	- Pros: Syntax highlighting, validation, execution.
	- Cons : requires a running instance of hybris, going out from eclipse, risking to loose all you work if the browser crashes.
- Excel or similar tools that could read and format CSV file:
	- Pros: Formatting that offers higher readability
	- Cons: no syntax highlighting, no validation and execution.
- Eclipse or similar IDE:
	- Pros: you stay focus on your IDE.
	- Cons: no formatting, no syntax highlighting, no validation and execution.


And guess what, Eclipse is The most used option ! developers choose it over other options , beacause it allow them to stay more focus.

## Eclipse Plugin :

To boost my productivity and to be more focus while working withe impex on Eclipse, I decided to develop an Impex Editor.The plugin should bring the hybris web console features to eclipse.
Still that all what I know about eclipse plugin development is some basic notions.

### Learn by example:

I believe the best way to learn new things is to start with some theory, then jump to a practical example where the real wisdom is gained.

- A good theorical Article is [Introduction To Eclipse Plugin Development](http://www.eclipsepluginsite.com/).
- A good practical tutorial i found interesting is :  [Extending the Eclipse IDE - Plug-in development - Tutorial](http://www.vogella.com/tutorials/EclipsePlugIn/article.html)

I took as example the sample plugin project given by eclipse to create a xml editor .

### Features of the plugin :

#### Syntax highlighting:

The Syntax highlighting feature uses the rule based scanner class, given a set of rules, the scanner consumes the impex file and evaluates each token. If the token matches a rule, the scanner exits with the corresponding properties.

The ruleset are based on the Hybris [Impex syntax documentation](https://wiki.hybris.com/display/release5/ImpEx+Syntax)


Before :
![Before](/images/impex/avant.png)


After :

![After](/images/impex/after.png)


### Preferences of the plugins :

To give the more friendly user experience,i used the Preferences API to allow customisation.

![Preference Snapshot](/images/impex/perferences_1.png)

I also possible to configure the connection parameters with hybris, this connection will be used to execute and validate the impex .

![Preference Snapshot](/images/impex/perferences_2.png)



#### Detecting hyrbis Item and attributes :

The first time eclipse run, the plugin connect to the already configured running hybris instance, calls the Rest Webservice `allItems` , and `allAttributes` (exposed by hybris) and store the information to avoid calling the web service again.

I Implemented an action to refresh the already stored data definition, the action will allo detecting newly added Items or attributes.

#### A challenge and a new techniques acquired :  

The web services exposed by hybris requires a registered hybris account and it's secured against [Cross-site request forgery](http://en.wikipedia.org/wiki/Cross-site_request_forgery).

To make a successful call the request should pass a crsf token, it's associated with the connected account. and it's stored on the HTML code of a response,so i had to use the [jsoup](http://jsoup.org/) library to retrieve its value.

- Make a first to login, the call return with a JSESSIONID, I store the JSESSIONID for a further call.
- Use jsoup with the stored JSESSIONID, and get the crsf token from the html.
- Make a Rest Call to retrieve the Items and attributes definition.

### The coolest feature : Autocompletion .
The auto-completion is the most liked feature, since i have stored the data deffinition, this feature was easy to implement as well .

![Preference Snapshot](/images/impex/autosuggest.png)


## Install the plugin :

To install the plugin , just open your eclipse , click Help > Install New Software… and enter the URL [http://eljoujat.github.io/updates/](http://eljoujat.github.io/updates/).

Or :

just copy the latest release  from here [impex editor relases ](https://github.com/eljoujat/eclipseimpexeditor/releases) to the dropins folder under eclipse directory , restart eclipse , and enjoy :)



## What next:

Other features i'm working on are :

- Validate the impex with error markers.
- Execute the impex .
- Hyperlink features to easily locate where an Item is already valued from the same impex .
- Find usage Features, find all usage for the selected definied and selected item .
- Formatting .

## Code Source Repos:

[The code source repo is available here ](https://github.com/eljoujat/eclipseimpexeditor)




> “I believe that there is always an other way to do it, and i hope that you let me know .”
