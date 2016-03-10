bfg-pages is a simple CMS based repoze.bfg, io.formish and is intended to run on google app engine.

bfg-pages presents content in a persistent folder hierarchy for content management.  It includes content types for a basic page, file, image, news item, a lightbox gallery of a picasaweb rss feed, and a stored query view object that allows the persistent definition of queries as a part of content authoring, and author able actions that can represent page tabs, menus or whatever else you would like.

It uses zope.pagetemplate for templating with additions to suit app engine and allows the use of metal macros when template.

You can see an example site running this code at http://repoze-bfg-gae.appspot.com/

I need to get a paster script working so people can set a site up out of the box.