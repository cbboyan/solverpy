from multiprocessing import Pool, Manager
from tqdm import tqdm
from . import bars

WAIT = 365*24*60*60 # a year

def starmap(fun, args, cores=4, chunksize=1):
   pool = Pool(cores)
   runner = pool.starmap_async(fun, args, chunksize=chunksize)
   results = runner.get(WAIT)
   pool.close()
   pool.join()
   return results

def apply(fun, args, cores=4, chunksize=1, bar=None, callback=None):
   pool = Pool(cores)
   m = Manager()
   queue = m.Queue()
   todo = len(args)
   #if bar: bar = tqdm(total=todo, desc=bar ,bar_format=bar_format) #, ncols=80, ascii="ox") 
   if isinstance(bar,str): bar = bars.default(todo, bar)
   queuedata = callback is not None
   args = [(fun,job,queue,queuedata) for job in args]
   runner = pool.starmap_async(runjob, args, chunksize=chunksize)
   while todo:
      res = queue.get(WAIT)
      if callback:
         callback(res, bar)
      todo -= 1
      if bar: bar.update(1)
   if bar: bar.close()
   pool.close()
   pool.join()
   return None if queuedata else runner.get(WAIT)

def runjob(fun, job, queue, queuedata):
   result = None
   try:
      result = fun(*job)
   except Exception as e:
      print(e)
      import traceback
      print("Error: "+traceback.format_exc())
      print(job)
   # send the result throught the queue or return it
   queue.put(result if queuedata else "DONE")
   return None if queuedata else result

