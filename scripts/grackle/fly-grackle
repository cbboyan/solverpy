#!/usr/bin/env python3

if __name__ == '__main__':
   import sys
   import solverpy_grackle.state, solverpy_grackle.main

   if len(sys.argv) != 2:
      print("usage: %s grackle.fly" % sys.argv[0])
      sys.exit(-1)

   init = solverpy_grackle.state.State(sys.argv[1])
   solverpy_grackle.main.loop(init)

