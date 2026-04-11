import sys
import grackle.state
import grackle.main


def main():
   if len(sys.argv) != 2:
      print("usage: %s grackle.fly" % sys.argv[0])
      sys.exit(-1)

   init = grackle.state.State(sys.argv[1])
   grackle.main.loop(init)
