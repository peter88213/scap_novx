"""Build a Python script for the scap_novx distribution.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the novxlib package.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import sys
import os
sys.path.insert(0, f'{os.getcwd()}/../../novxlib/src')
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}scap_novx_.py'
TARGET_FILE = f'{BUILD}scap_novx.py'


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'scapnovxlib', '../src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'novxlib', '../../novxlib/src/')
    print('Done.')


if __name__ == '__main__':
    main()
