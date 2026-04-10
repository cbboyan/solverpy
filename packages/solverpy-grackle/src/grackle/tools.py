
def load_class(cls):
   i = cls.rindex(".")
   pkg = cls[:i]
   cls = cls[i+1:]
   mod = __import__(pkg, fromlist=[cls])
   return getattr(mod, cls)

def convert(string):
   if string == "True":
      return True
   elif string == "False":
      return False
   elif string.isdigit():
      return int(string)
   elif string.count(".") == 1 and all(x.isdigit() for x in string.split(".")):
      return float(string)
   else:
      return string

def parse_ini(f_run):
   ini = open(f_run).read().strip().split("\n")
   for (n,line) in enumerate(ini):
      if "#" in line:
         ini[n] = line[:line.index("#")]
   ini = [l.split("=") for l in ini if l and ("=" in l)]
   ini = {x.strip():y.strip() for (x,y) in ini}
   return ini

