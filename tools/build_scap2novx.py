"""Build a Python script for the scap2novx distribution.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the novxlib package.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/scap2novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import sys
import os
sys.path.insert(0, f'{os.getcwd()}/../../novxlib-Alpha/src')
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}scap2novx_.pyw'
TARGET_FILE = f'{BUILD}scap2novx.pyw'


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'scap2novxlib', '../src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'novxlib', '../../novxlib-Alpha/src/')
    print('Done.')


if __name__ == '__main__':
    main()
