
import time

def timeme(method):
   def inner(*args, **kw):
      ts = time.perf_counter()
      result = method(*args, **kw)
      te = time.perf_counter()
      print('# performance: %r: %2.2f ms' % (method.__name__, (te - ts) * 1000))
      return result    
   return inner

