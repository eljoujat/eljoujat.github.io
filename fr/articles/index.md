---
layout: default
lang: fr
---

{% assign posts=site.posts | where:"lang", page.lang %}
<div >
  <section class="posts">    
    {% for post in posts limit:25 %}

<div class="action">
    <a href='{{ post.url }}' class="{{ post.lang }}"><span class="title">{{ post.title }}</span></a>
  </div>
  <div class="image">
  {% if post.photo_url %}
        <img src="{{ post.photo_url }}">
  {% endif %}

  </div>
  <div class="content">
    <p>{{ post.description | strip_html }}</p>
  </div>
  <div class="action">
    <info datetime>{{ post.date | date: "%b %Y" }}</info>
  </div>

    {% endfor %}
  </section>
</div>


<script type="text/javascript">

$( function() {

  $('.posts').isotope({
    itemSelector: '.card',
    masonry: {

    }
  });

});
</script>
