#!/usr/bin/env python
import sys, os
import getopt
import threading

from eisoil import config
from eisoil.core import pluginmanager as pm


def main():
    # set home environment variable to something (needed for apache deployment)
    os.environ['HOME'] = config.expand_eisoil_path('~')

    # load plugins
    pm.init(config.PLUGINS_PATH)

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hw', ['help', 'worker'])
    except getopt.GetoptError as e:
        print "Wrong arguments: " + str(e)
        print
        print_usage()
        return
    for option, opt_arg in opts:
        if option in ['-h', '--help']:
            print_usage()
            sys.exit(0)


    registration_server = pm.getService('registration')
    registration_server.runServer()

if __name__ == "__main__":
    main()
