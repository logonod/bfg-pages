# Introduction #

Chameleon with zpt has a couple of ways of running.
One way is for it to parse the templates on first load and keep an
in memory cache of the parsed template, which it then uses to render.

The other way is when chameleon parses the template it produces python code output
that represents the template.  (This process is also performed in the first option
but doesn't result in a .pt.py file in the filesystem.)

Chameleon is supposed to be faster than zope.pagetemplate for rendering (I haven't
benchmarked it myself, but I think I believe the authors ;-)  However the parsing
and production of the intermediate python code is also supposed to be slower
than parsing performed by zope.pagetemplate.  So in theory there is a big win for long running processes especially if you can write out the python files to the filesystem, as the cost  parsing of templates would only be performed once for any version of the code.

The problem is appengine doesn't allow writing to the filesystem so in memory
caching is the only option.  This also means that every instance of appengine
starting up will incurr the cost of reparsing the templates over and over again.

So the plan here is to pre-compile the pagetemplate to python in the dev environment
and then deploy the .pt.py files to appengine and not incurr the cost of reparsing
over and over again.

The one wart is even on the dev\_server you can't write to the filesystem, so a seperate
precompilation phase is needed.  Ideally this should be run just prior to running
appcfg update.  (Or even earlier, however recompiling everything each time you
change a template would be a pain. ;-)

# Details #

Here is an early implementation, it has hard coded paths and assumes the project has been setup using the Pyramid on appengine project has been setup using the PyramidTutorial

```
#!/usr/bin/python2.5

import os
os.environ['CHAMELEON_CACHE'] = "true"
os.environ['CHAMELEON_DEBUG'] = "false"
join = os.path.join
base = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
base = os.path.dirname(base)

import sys
sys.path[0:0] = [
    join(base, 'app'),
    join(base, 'app/lib'),
    join(base, 'app/lib/dist'),
    join(base, 'eggs/appfy.recipe.gae-0.9.1-py2.5.egg'),
    join(base, 'var/parts/google_appengine'),
    ]


gae = join(base, 'var/parts/google_appengine')
cfg = join(base, 'gaetools.cfg')

import appfy.recipe.gae.scripts
from chameleon.zpt import loader, template
loader = loader.TemplateLoader(base)

def compile(template_file):
    ctemplate = template.PageTemplateFile(template_file)
    ctemplate.parse()
    if not ctemplate.macros.names:
        source = ctemplate.compiler(macro=None,global_scope=True)
        key = None, True, ctemplate.signature
        ctemplate.registry.add(key, source, ctemplate.filename)
    else:
        for name in ctemplate.macros.names:
            source = ctemplate.compiler(macro=name,global_scope=False)
            key = name, False, ctemplate.signature
            ctemplate.registry.add(key, source, ctemplate.filename)

def main():
   
   path = "app"
   for (dirpath, dirnames, filenames) in os.walk(path):
      if 'paster_templates' in dirnames:
          idx = dirnames.index('paster_templates')
          popped = dirnames.pop(idx)
          print "skipping ", os.path.join(dirpath,popped)
      for name in filenames:
         if name.endswith('.pt'):
             tspec = os.path.join(dirpath,name)
             print "compiling", tspec   
             compile(tspec)

if __name__ == '__main__':
    main()
```


To use the cached templates you will need to set the following in your main.py
```
os.environ['CHAMELEON_CACHE'] = "true"
os.environ['CHAMELEON_DEBUG'] = "false"
```
and set pyramid settings
```
'reload_templates': 'false',
'debug_templates': 'false',
```

## Whats Next ##

  * build some tests
  * make a patch for chameleon to have a readonly cache. In other words try to load the .pt.py and if not found, fall back to the in memory filecache rather than try to regenerate a filesystem .pt.py file.  Which will obviously fail on appengine.
  * Make this script have command line args so that it's actually useful.
  * write decent documentation
  * do some benchmarks to prove if this is usefull or not