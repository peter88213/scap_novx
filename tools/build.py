"""Build the scap_novx application package.
        
Note: VERSION must be updated manually before starting this script.

For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys

sys.path.insert(0, f'{os.getcwd()}/../../novelibre/tools')
from package_builder import PackageBuilder

VERSION = '5.2.0'


class ApplicationBuilder(PackageBuilder):

    PRJ_NAME = 'scap_novx'
    LOCAL_LIB = 'scapnovxlib'

    def __init__(self, version):
        super().__init__(version)
        self.distFiles.append(
            (f'{self.sourceDir}relocate.py', self.buildDir)
            )
        self.sourceFile = f'{self.sourceDir}{self.PRJ_NAME}_.py'
        self.iconDir = '../icons'

    def add_extras(self):
        self.add_icons()
        self.add_sample()


def main():
    ab = ApplicationBuilder(VERSION)
    ab.run()


if __name__ == '__main__':
    main()

