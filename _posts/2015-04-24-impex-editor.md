---
title: "Writing SAP-Hybris Impex with Style !"
layout: post
og_image_url: "https://eljoujat.github.io/images/impex/image004.jpg"
description: "Writing SAP-Hybris Impex with style: An eclipse plugin that will change the way you work with Impex."
disqus_comments: true
---


> Two things that drive us, software development addicts: enthusiasm and laziness...
ANONYMOUS


## The idea behind the current lab.

Impex is a [SAP Hybris](https://hybris.com) specific language on top of SQL to import/export data.

The lack of tools makes things difficult when working with Impex. In fact, some available options are:

- Web console offered by SAP Hybris:
  - Pros: Syntax highlighting, validation, execution.
  - Cons: Requires a running instance of Hybris, going out from Eclipse, risking losing all your work if the browser crashes.
- Excel or similar tools that could read and format CSV files:
  - Pros: Formatting that offers higher readability.
  - Cons: No syntax highlighting, no validation, and no execution.
- Eclipse or similar IDE:
  - Pros: You stay focused on your IDE.
  - Cons: No formatting, no syntax highlighting, no validation, and no execution.

And guess what? Eclipse is the most used option! Developers choose it over other options because it allows them to stay more focused.

## Eclipse Plugin:

To boost my productivity and to be more focused while working with Impex on Eclipse, I decided to develop an Impex Editor. The plugin should bring the Hybris web console features to Eclipse.
Still, all I knew about Eclipse plugin development were some basic notions.

### Learn by example:

I believe the best way to learn new things is to start with some theory, then jump to a practical example where the real wisdom is gained.

- A good theoretical article is [Introduction To Eclipse Plugin Development](http://www.eclipsepluginsite.com/).
- A good practical tutorial I found interesting is: [Extending the Eclipse IDE - Plug-in development - Tutorial](http://www.vogella.com/tutorials/EclipsePlugIn/article.html).

I took as an example the sample plugin project given by Eclipse to create an XML editor.

### Features of the plugin:

#### Syntax highlighting:

The syntax highlighting feature uses the rule-based scanner class. Given a set of rules, the scanner consumes the Impex file and evaluates each token. If the token matches a rule, the scanner exits with the corresponding properties.

The ruleset is based on the Hybris [Impex syntax documentation](https://wiki.hybris.com/display/release5/ImpEx+Syntax).

Before:
![Before](/images/impex/avant.png)

After:
![After](/images/impex/after.png)

### Preferences of the plugin:

To provide a more friendly user experience, I used the Preferences API to allow customization.

![Preference Snapshot](/images/impex/perferences_1.png)

It is also possible to configure the connection parameters with Hybris. This connection will be used to execute and validate the Impex.

![Preference Snapshot](/images/impex/perferences_2.png)

#### Detecting Hybris Items and attributes:

The first time Eclipse runs, the plugin connects to the already configured running Hybris instance, calls the REST Web service `allItems` and `allAttributes` (exposed by Hybris), and stores the information to avoid calling the web service again.

I implemented an action to refresh the already stored data definition. The action will allow detecting newly added Items or attributes.

#### A challenge and a new technique acquired:

The web services exposed by Hybris require a registered Hybris account and are secured against [Cross-site request forgery](http://en.wikipedia.org/wiki/Cross-site_request_forgery).

To make a successful call, the request should pass a CSRF token. It is associated with the connected account and stored in the HTML code of a response, so I had to use the [Jsoup](http://jsoup.org/) library to retrieve its value.

- Make a first call to login. The call returns with a `JSESSIONID`, which I store for further calls.
- Use Jsoup with the stored `JSESSIONID`, and get the CSRF token from the HTML.
- Make a REST call to retrieve the Items and attributes definition.

### The coolest feature: Autocompletion.

The auto-completion is the most liked feature. Since I have stored the data definition, this feature was easy to implement as well.

![Preference Snapshot](/images/impex/autosuggest.png)

## Install the plugin:

To install the plugin, just open your Eclipse, click **Help > Install New Software…** and enter the URL [http://eljoujat.github.io/updates/](http://eljoujat.github.io/updates/).

Or:

Just copy the latest release from here: [Impex Editor releases](https://github.com/eljoujat/eclipseimpexeditor/releases) to the `dropins` folder under the Eclipse directory, restart Eclipse, and enjoy :)

## What's next:

Other features I'm working on are:

- Validate the Impex with error markers.
- Execute the Impex.
- Hyperlink features to easily locate where an item is already valued from the same Impex.
- Find usage features, find all usages for the selected defined and selected item.
- Formatting.

## Code Source Repos:

[The code source repo is available here](https://github.com/eljoujat/eclipseimpexeditor).


> “I believe that there is always another way to do it, and I hope that you let me know.”


