#!/usr/bin/env python
'''
The main entry point of this file.

Usage:
    python main.pyw [filename]
'''

import sys

import script_parser
import renderer
import errors


def get_file():
    '''Gets the filename of the script to parse, and does some
    error checking.'''
    if len(sys.argv) != 2:
        errors.warn('Drag and drop your text file over me')
    path = sys.argv[1]
    if path in ['help', '--help', '-h']:
        print 'Please see the readme.'
        sys.exit()
    try:
        with open(path, 'r') as script:
            return script.read().split('\n')
    except IOError:
        errors.error('Could not find the file "{0}"'.format(path))
        
def main():
    '''Combine together all the modules to parse and render a script.'''
    file_contents = get_file()
    script = script_parser.Script(file_contents)
    plot = renderer.Plot(script)
    plot.show()
        
if __name__ == '__main__':
    main()