"""scap_novx installer library module. 

Version @release

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
from pathlib import Path
from shutil import copy2
from shutil import copytree
from shutil import rmtree
import stat
import sys
import zipfile

APPNAME = 'scap_novx'
VERSION = ' @release'
APP = f'{APPNAME}.py'
INI_FILE = f'{APPNAME}.ini'
INI_PATH = '/config/'

pyz = os.path.dirname(__file__)


def extract_file(sourceFile, targetDir):
    with zipfile.ZipFile(pyz) as z:
        z.extract(sourceFile, targetDir)


def extract_tree(sourceDir, targetDir):
    with zipfile.ZipFile(pyz) as z:
        for file in z.namelist():
            if file.startswith(f'{sourceDir}/'):
                z.extract(file, targetDir)


def cp_tree(sourceDir, targetDir):
    copytree(sourceDir, f'{targetDir}/{sourceDir}', dirs_exist_ok=True)


def main(zipped=True):
    if zipped:
        copy_file = extract_file
        copy_tree = extract_tree
    else:
        copy_file = copy2
        copy_tree = cp_tree

    scriptPath = os.path.abspath(sys.argv[0])
    scriptDir = os.path.dirname(scriptPath)
    os.chdir(scriptDir)

    print(f'*** Installing {APPNAME} {VERSION} *** ')
    homePath = str(Path.home()).replace('\\', '/')
    applicationDir = f'{homePath}/.novx/'
    if os.path.isdir(applicationDir):
        installDir = f'{applicationDir}{APPNAME}'
        cnfDir = f'{installDir}{INI_PATH}'
        os.makedirs(cnfDir, exist_ok=True)

        # Delete the old version, but retain configuration, if any.
        rmtree(f'{installDir}/icons', ignore_errors=True)
        rmtree(f'{installDir}/sample', ignore_errors=True)
        with os.scandir(installDir) as files:
            for file in files:
                if 'config' in file.name:
                    continue

                os.remove(file)
                print(f'Removing "{file.name}"')

        # Install the new version.
        print(f'Copying "{APP}" ...')
        copy_file(APP, installDir)

        # Install the icon files.
        print('Copying icons ...')
        copy_tree('icons', installDir)

        # Make the script executable under Linux.
        st = os.stat(f'{installDir}/{APP}')
        os.chmod(f'{installDir}/{APP}', st.st_mode | stat.S_IEXEC)

        # Provide the sample files.
        print('Copying sample files ...')
        copy_tree('sample', installDir)

        # Show a success message.
        print(
            f'Sucessfully installed "{APPNAME}" '
            f'at "{os.path.normpath(installDir)}".'
        )
    else:
        print(
            'ERROR: Cannot find a novelibre installation '
            f'at "{os.path.normpath(applicationDir)}".'
        )

    input('Press any key to quit.')

