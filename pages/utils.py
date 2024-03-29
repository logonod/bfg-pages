
import logging
import os.path
import os, sys
from datetime import datetime,timedelta
from time import mktime
import time

import wsgiref.util
from wsgiref.handlers import format_date_time

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext.webapp import Request
from google.appengine.ext.webapp.util import run_wsgi_app


#from repoze.bfg.registry import populateRegistry
#from repoze.bfg.interfaces import IGETRequest,IPOSTRequest
from gae.utils import BREAKPOINT

from zope.component import getSiteManager        
from zope.tales.engine import Engine


       
class ActionContext(object):
    _engine = Engine
    
    def __init__(self,req,d={}):
        self.dicts = d
        self.vars = d
        self.request = req 
        

##def get_cache():
##    if users.is_current_user_admin():
##        return None
##    env = dict(os.environ)
##    env["wsgi.input"] = sys.stdin
##    env["wsgi.errors"] = sys.stderr
##    env["wsgi.version"] = (1, 0)
##    env["wsgi.run_once"] = True
##    env["wsgi.url_scheme"] = wsgiref.util.guess_scheme(env)
##    env["wsgi.multithread"] = False
##    env["wsgi.multiprocess"] = False
##    req = Request(env)
##    cached_resp = memcache.get(req.path_url.rstrip('/'))
##    
##    if cached_resp:
##        def cache_app(env,start_resp):
##            logging.info('returning cached page (%s)' % req.path_url)
##            #BREAKPOINT()
##            write_handle = start_resp(cached_resp.status,(cached_resp.headers.items()))
##            write_handle(cached_resp.body)
##        return cache_app
##    else:
##
##        return None

def updateSessionCacheInfo(request,key='',info={},action=1):
    """Updates session cache key information for cache management view.
       session 'cache_info' is a record of the current cache keys. Cache keys are
       represented in the sessin by 'category' and contain at least a 'key' and a
       descriptive 'title'.

       Parameters:
         info: Dictionary with cache info, at least 'key' and 'title'
         action: Value indicating whether to add (1) or to delete (0) the information.
    """
    session = request.environ.get('beaker.session',None)
    if not session or not key:
        return
    cache_info = session.get('cache_info',dict())
    #cache_info = dict()
    #if 'cache_info' in session.keys():
    #    cache_info = session['cache_info']
    if key in cache_info.keys():
        # Nothing to do
        if action==0:
            # Delete key.
            cache_info.pop(key)
            session['cache_info'] = cache_info
            session.save()
        return
    # Handle adding.
    cache_info[key] = info
    session['cache_info'] = cache_info
    session.save()


def cacheoutput(func):
    """ memcache caching decorator"""
    def _wrapper(context, REQUEST):
        
        output = func(context, REQUEST)
        if not getattr(REQUEST.principal,'ADMIN',False):
            key=REQUEST.path_url.rstrip('/')
            logging.debug('cacheoutput: %s - %s' % (key,repr(output)))
            memcache.set(key,output,86400)
        else:
            key=REQUEST.path_url.rstrip('/')
            updateSessionCacheInfo(REQUEST,key,{'title':context.name})
        return output    
            
    return _wrapper


def cacheviewfragment(meth):
    def _wrapper(self):
        
        key = self.request.url.rstrip('/')+':FRAGMENT:'+repr(self.view.__class__) 
        isAdmin = getattr(self.request.principal,'ADMIN',False)
        
        if not isAdmin:
            output = memcache.get(key)
            if output:
                logging.debug('got from cacheviewfragment: %s' % (key))
                return output

        updateSessionCacheInfo(self.request,key,{'title':'Fragment'})
            
        output = meth(self)
        
        if not isAdmin:
            logging.debug('cacheviewfragment: %s' % (key))
            memcache.set(key,output,86400)
            
        return output    
            
    return _wrapper

def cachemethodreturn(meth):
    def _wrapper(self):
        
        key = self.request.url.rstrip('/')+':METHOD:'+meth.__name__ 
        isAdmin = getattr(self.request.principal,'ADMIN',False)
        
        if not isAdmin:
            output = memcache.get(key)
            if output:
                logging.debug('got from cachemethodreturn: %s' % (key))
                return output

        updateSessionCacheInfo(self.request,key,{'title':'Fragment'})
            
        output = meth(self)
        
        if not isAdmin:
            logging.debug('cachemethodreturn: %s' % (key))
            memcache.set(key,output,86400)
            
        return output    
            
    return _wrapper

def cachemethodoutput(meth):
    def _wrapper(self):
        
        key = self.request.url.rstrip('/') 
        isAdmin = getattr(self.request.principal,'ADMIN',False)
        
        if not isAdmin:
            #if IPOSTRequest.providedBy(self.request):
            if (self.request.method == 'POST'):
                key = key + ":POST:" + str(self.request.str_POST)
            
            output = memcache.get(key)
            if output:
                logging.debug('got from cachemethodoutput: %s' % (key))
                return output
        else:
            #if IPOSTRequest.providedBy(self.request):
            if (self.request.method == 'POST'):
                key = key + ":POST:" + str(self.request.str_POST)

        updateSessionCacheInfo(self.request,key,{'title':'Method'})
            
        output = meth(self)
        
        if not isAdmin:
            logging.debug('cachemethodoutput: %s' % (key))
            memcache.set(key,output,86400)
            
        return output    
            
    return _wrapper

def cachefixedportlet(meth):
    
    def _wrapper(self):
        output = None
        isAdmin = getattr(self.request.principal,'ADMIN',False)
        
        key=self.request.host+':'+self.request.SKIN_NAME+':PORTLET:'+self.portlet.getPath()
       
        if not isAdmin:
            output = memcache.get(key)
            if output:
                logging.debug('got from cachefixedportlet: %s' % (key))
                return output

        updateSessionCacheInfo(self.request,key,{'title':'Portlet'})
        
        output = meth(self)
        
        if not isAdmin:
            logging.debug('cachefixedportlet: %s' % (key))
            memcache.set(key,output,86400)
            
        return output    
            
    return _wrapper

def cachefixedview(meth):
    
    def _wrapper(self):
        
        output = None
        isAdmin = getattr(self.request.principal,'ADMIN',False)
        
        key=self.request.host+':'+self.request.SKIN_NAME+':VIEW:'+str(self.__class__)
        
        if not isAdmin:
            output = memcache.get(key)
            if output:
                return output

        updateSessionCacheInfo(self.request,key,{'title':'View'})
        
        output = meth(self)
        
        if not isAdmin:
            logging.debug('cachefixedview: %s' % (key))
            memcache.set(key,output,86400)
            
        return output    
            
    return _wrapper


##def cacheinstancemethodoutput(func):
##    """ memcache caching decorator for instance methods"""
##    def _wrapper(context, mcontext, REQUEST):
##        mcontext = context
##        if hasattr(context,'context'):
##            mcontext = context.context
##        output = func(context, mcontext, REQUEST)
##        if not getattr(REQUEST.principal,'ADMIN',False):
##            key=REQUEST.path_url.rstrip('/')
##            memcache.set(key,output,86400)
##            logging.info('cache key: %s' % key)
##        return output    
##            
##    return _wrapper

import time

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2):
    """Retry decorator
    original from http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            #BREAKPOINT()
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    logging.warning( "%s, Retrying in %d seconds..." % (str(e), mdelay))
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return
        return f_retry # true decorator
    return deco_retry
 



def make_time_header(thetime=None,add=0):
    
    if not thetime:
        thetime = datetime.now()
    
    if add:
        thetime = thetime + timedelta(days=add)
        
    return format_date_time(mktime(thetime.timetuple()))
