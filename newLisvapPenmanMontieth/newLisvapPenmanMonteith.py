import sys, imp

import lvPenmanMonteith


def main():
  sttsFlPth = sys.argv[1]

  print('loading settings from file')
  print(sttsFlPth)
  imp.load_source('settings', sttsFlPth)
  import settings

  print
  print('running lisvap')
  print
  lvPenmanMonteith.run(settings)


if __name__ == '__main__':
  main()

