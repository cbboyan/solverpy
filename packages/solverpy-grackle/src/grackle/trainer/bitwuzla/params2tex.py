#!/usr/bin/env python

import domain

def texstr(s):
   return "\\verb+%s+" % s

params = domain.PARAMS % domain.DEFAULTS
params = [x.split(" ") for x in params.split("\n") if "," in x]
params = [(x,y.strip("{}"),z.strip("[]")) for (x,y,z) in params]

for (name, domain, default) in sorted(params):
   name = texstr(name)
   default = texstr(default)
   domain = ",".join(texstr(x) for x in domain.split(","))
   print(f"{name} & {domain} & {default} \\\\")

