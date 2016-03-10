# This is old, and out of date it will not work with current releases of pyramid.  Am working on a new one.

#summary Example setup running pyramid on appengine.

# Introduction #

This is a tutorial on getting the basic tutorial code for Pyramid running on appengine.
Its based on predefined project.  A paster based template to build the project will come later.


# Details #

This setup assumes your using linux. Code and buildout config for the tutorial is found at http://bfg-pages.googlecode.com/svn/pyramid-gae-tutorial/trunk

## Setup ##

To do the setup I am going to use a buildout recipe developed by Rodrigo Moraes <rodrigo moraes at gmail com>.  Recipe at http://pypi.python.org/pypi/appfy.recipe.gae/0.9.1.



Make a directory for your tutorial.
```
timh@chrome:~$ mkdir tut1
timh@chrome:~$ cd tut1
```

Then setup virtualenv so you can install the buildout recipe.
```

timh@chrome:~/tut1$ virtualenv --no-site-packages --python=/usr/bin/python2.5 .
Running virtualenv with interpreter /usr/bin/python2.5
New python executable in ./bin/python2.5
Also creating executable in ./bin/python
Installing setuptools............done.
```

Don't activate the virtualenv.  Use explicit paths when referencing scripts set up by virtualenv.

Now use easy\_install to install the appfy.recipe.gae
```
timh@chrome:~/tut1$ ./bin/easy_install appfy.recipe.gae
```

Next check out the sample app which has the bootstrap and buildout configs to be used for the rest of the tutorial.

```
timh@chrome:~/tut1$
timh@chrome:~/tut1$ svn checkout http://bfg-pages.googlecode.com/svn/pyramid-gae-tutorial/trunk app
A    app/default_error.html
A    app/settings.yaml
A    app/app.yaml
A    app/pkg_resources.py
A    app/views.py
A    app/bootstrap.py
A    app/buildout.cfg
A    app/lib
A    app/lib/dist
A    app/utils.py
A    app/static
A    app/static/logo.png
A    app/static/pylons.css
A    app/static/favicon.ico
A    app/tests.py
A    app/models.py
A    app/main.py
A    app/templates
A    app/templates/mytemplate.pt
Checked out revision 159.
```

Next we need to create some symlinks to varios .cfg files required for buildout.
```
timh@chrome:~/tut1$ ln -s app/buildout.cfg 
timh@chrome:~/tut1$ ln -s app/bootstrap.py 
timh@chrome:~/tut1$ ln -s app/gaetools.cfg 
timh@chrome:~/tut1$ ln -s app/versions.cfg 

```

make a var/downloads so that buildout can cache its downloads.

```
timh@chrome:~/tut1$ mkdir -p var/downloads
```

Then run bootstrap.py which sets up the environment (this will use distribute)

```

timh@chrome:~/tut1$ ./bin/python bootstrap.py 

... stuff happens ...
```

Now run buildout, which will download and install pyramid and all of it's dependancies in app/lib/dist.  This recipe unpicks the eggs and only deploys the required files.

```
timh@chrome:~/tut1$ ./bin/buildout

... stuff happens ...

timh@chrome:~/tut1$

```

Now start the dev server.

```
timh@chrome:~/tut1$ bin/dev_appserver app
INFO     2010-12-03 15:24:27,784 appengine_rpc.py:153] Server: appengine.google.com
WARNING  2010-12-03 15:24:27,788 datastore_file_stub.py:573] Could not read datastore data from /home/timh/tut1/var/data.store
INFO     2010-12-03 15:24:27,816 dev_appserver_main.py:485] Running application pyramid-gae-tutorial on port 8080: http://localhost:8080
WARNING  2010-12-03 15:24:33,924 main.py:20] Starting main
```

Point your web browser at http://localhost:8080/
and something similar to below will appear in the terminal

```
INFO     2010-12-03 15:24:34,171 dev_appserver.py:3317] "GET / HTTP/1.1" 200 -
```

This sample app has been deployed on appspot. You can see it at http://pyramid-gae-tutorial.appspot.com/

## Details of the sample app ##

Now lets look at the difference between this sample app and the one in the original tutorial.

things to discuss.

### whats in the app ###

```
   + app
      + lib
         + dist
            #unpicked pyramid and it's dependancies
            + chameleon  
            + mako  
            + markupsafe  
            + paste  
            + pyramid  
            + README.txt  
            + repoze  
            + simplejson  
            + tests  
            + translationstring  
            + venusian  
            + webob  
            + zope
 
      app.yaml
      default_error.html
      main.py
      pkg_resources.py
      + static
         favicon.ico  
         logo.png  
         pylons.css

      + templates
          mytemplate.pt

      tests.py
      views.py

```

You will also note there are the **.cfg files that you created the symlink to eariler. These are not part of the appengine application.  (I need to stick them somewhere else ;-)**

The contents of  lib are as a result of running buildout, which installs pyramid from PyPI eggs and all of its dependancies and then proceeds to copy the actual code from the eggs to lib/dist  _(I need to move everything up to dist, thats a hold over from the original recipe for tipfy, which I am leveraging off)_

### main.py ###

```
import logging

logging.getLogger().setLevel(logging.INFO)

import sys,os

sys.path.insert(0,'lib/dist')

from pyramid.configuration import Configurator
from models import get_root
from google.appengine.ext.webapp.util import run_wsgi_app

settings = {
    'reload_templates': 'false',
    'debug_authorization': 'false',
    'debug_notfound': 'false',
    'debug_templates': 'false',
    'default_locale_name': 'en',
}

def main():
    """ This function runs a Pyramid WSGI application.
    """
    
    config = Configurator(root_factory=get_root,settings=settings)
    config.add_view('views.my_view',
                    context='models.MyModel',
                    renderer='templates/mytemplate.pt')
    app = config.make_wsgi_app()
    run_wsgi_app(app)
            
if __name__ == '__main__':
  main()
```




  * run\_wsgi\_app
  * settings
  * debugging with pdb
  * static handlers.
  * default\_error handler
  * app.yaml
  * configuring chameleon


## Deploying the app ##

  * appcfg

## Running tests ##

> put stuff here ...

## Some important info/links for appengine ##

### Import things to note ###

here are some random things a pyramid developer new to appengine needs to know.

  * appengine runs python 2.5 in production.  **Do not be even tempted to run python 2.6 or later.  You have been warned** ;-)
  * appengine runs multiple single threaded instances of your code, to service the requests.
  * instances of your app can only share state/information via the datastore or memcache.
  * web requests must run within 30seconds.
  * startup time for a cold instance is crucial.
    * Try and defer things if you can. For instance don't load up a deform/formish schemas for forms until you actually need them.
    * do all you configuration imperatively.  zcml and scan is slower.
  * You can not write to the filesystem in appengine.


### Important links to documents and/or resources ###

  * Read Nick Johnsons blog.  http://blog.notdot.net/
  * Appengine docs.  http://code.google.com/appengine/docs/python/gettingstarted/

