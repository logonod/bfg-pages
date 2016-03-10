# Introduction #

This is a very rough setup procedure, once I work out how to setup paster scripts I will include that in the project and then re-arrange everything to make it much easier


# Details #

Download and untar gae somewhere

Make a top level install dir for all the eggs using virtualenv.

```
timh@timh-desktop:~$ mkdir repoze-bfg-gae    # Call it whatever you want
timh@timh-desktop:~$ cd repoze-bfg-gae/
timh@timh-desktop:~/repoze-bfg-gae
```

Create a virtual env . Note the --no-site-packages , this is important.
See repoze.bfg install docs for more info

```
timh@timh-desktop:~/repoze-bfg-gae$ virtualenv -p /usr/bin/python2.5 --no-site-packages .
Running virtualenv with interpreter /usr/bin/python2.5
New python executable in ./bin/python2.5
Also creating executable in ./bin/python
Installing setuptools............done.
```


Activate virtualenv
```
timh@timh-desktop:~/repoze-bfg-gae$ source bin/activate
```

Install pip so you can manage large eggs and turn them into zipped eggs
```
timh@timh-desktop:~/repoze-bfg-gae$ easy_install pip
```

Install repoze.bfg
```
timh@timh-desktop:~/repoze-bfg-gae$ bin/easy_install -i http://dist.repoze.org/bfg/current/simple repoze.bfg
```

Install formish
```
(repoze-bfg-gae)timh@timh-desktop:~/repoze-bfg-gae$ easy_install formish
```

Install zope.pagetemplate and its dependancies
```
(repoze-bfg-gae)timh@timh-desktop:~/repoze-bfg-gae$ easy_install zope.pagetemplate
```

Install zope.lifecycleevent. - used for notifying on add/edit/delete content and a few other things
```
(repoze-bfg-gae)timh@timh-desktop:~/repoze-bfg-gae$ easy_install zope.lifecyleevent
```

Zip up the pytz egg as has heaps of file. - if you have this you still might crack the 3000 file limit.

list eggs for zipping
```
pip zip -l
```

zip up pytz
```
bin/pip zip pytz-2009g-py2.5.egg
```

Now make a directory to run the app engine instance out of. Call it whatever you want
```
mkdir myinstance
cd myinstance
svn co http://bfg-pages.googlecode.com/svn/trunk/samples samples
```

Now create some symlinks to the files in the samples folder.  Yeah I know this is daggy but the whole thing is really not setup of easy\_install yet.
```
for i in `ls samples`; do
    ln -s samples/${i}
done
```

Edit the app.yaml to set you application id to something appropriate

Now setup the libs
make a lib dir so we can setup just the eggs etc we need for gae as there are a few installed from repoze.bfg that we either can't use or I am not using.

```
mkdir lib
cd lib
for i in `ls ../../lib/python2.5/site-packages/`; do
    ln -s ../../lib/python2.5/site-packages/${i}
done
```


Now delete symlinks for the following eggs

  * Beaker
  * chameleon.core
  * chameleon.zpt
  * pip
  * setuptools    egg and .pth
  * WebOb         as it is already in gae

#now checkout pages and gae
```
svn co http://bfg-pages.googlecode.com/svn/trunk/gae gae
svn co http://bfg-pages.googlecode.com/svn/trunk/pages pages    
```

Now cd back to the top of the gae instance whatever you called it.

cd ~/repoze-gae-bfg

# Deactivate virtualenv - I don't run the sdk dev server under it

deactivate

# now run up your dev server  I assume the sdk is in your home dir.

```
python2.5 ~/google_appengine/dev_appserver.py --datastore_path=./repoze.ds ./myinstance/
```

Note we are above the actual gae instance.  That way when we are uploading we don't send things like the dev datatstore

In theory you can connect to the server and try stuff.  See [SiteSetup](SiteSetup.md) and use for more details

# If you want to upload to your gae live instance then
```
python2.5 ~/google_appengine/appcfg.py update ./myinstance/
```