import sys
import os
import logging
import webapp

logger = logging.getLogger(__name__)

# add the modiule location to PATH
# this is necessary to execute the package as a script without installing it
to_append = os.path.dirname(os.path.dirname(__file__))
sys.path.append(to_append)


def main():
    webapp.app.run(debug=True)


if __name__ == '__main__':
    main()
