# Introduction #

Here is a very simple way to preload you running instance with some initial
data. Specifically a root entity and some action (provides menus)
Only do the following procedure once for a specific datastore instance, otherwise you
stuff things up !  Yep I should put some guards in to stop that.

# Details #

Complete the [Install](Install.md) steps and start your server.
Connect to your server and with the following url

```
http://myserver:port/setup/
```
It requires admin privileges.

You will be given a very simple page with three links.

Setup

  * ROOT Process ROOT
  * FOLDERS Process FOLDERS
  * ACTIONS Process ACTIONS

Click on each in the above order.
It will setup the root entity, some basic folders and some actions that will provide  add and edit menus.

Once this is done you should be able to go to the / of the site
```
http://myserver:port/
```

And should be able to see something.
To enable the edit interface use the following url . I am deliberately not providing a login url on the site.

```
http://myserver:port/contents
```

Some usage docs will follow soon.