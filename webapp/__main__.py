import sys
import os

# add the modiule location to PATH
# this is necessary to execute the package as a script without installing it
to_append = os.path.dirname(os.path.dirname(__file__))
sys.path.append(to_append)

import webapp

from webapp import parsing


def main():
    webapp.app.run(debug=False)


if __name__ == '__main__':
    main()
