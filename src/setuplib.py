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
from tkinter import messagebox
import zipfile

major = sys.version_info.major
minor = sys.version_info.minor
if  major != 3 or minor < 7:
    print(
        f'Wrong Python version installed: {major}.{minor}.\n'
        'Must be 3.7 or newer.'
    )
    input('Press ENTER to quit.')
    sys.exit(1)

APPNAME = 'scap_novx'
VERSION = '@release'
APP = f'{APPNAME}.py'
INI_PATH = '/config/'

SHORTCUT_MESSAGE = f'''
Now you might want to create a shortcut on your desktop.  

Open the installation folder, 
hold down the Alt key on your keyboard, 
and then drag and drop {APP} to your desktop.
'''

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


def open_folder(installDir):
    try:
        os.startfile(os.path.normpath(installDir))
        # Windows
    except:
        try:
            os.system('xdg-open "%s"' % os.path.normpath(installDir))
            # Linux
        except:
            try:
                os.system('open "%s"' % os.path.normpath(installDir))
                # Mac
            except:
                pass


def install(zipped):
    if zipped:
        copy_file = extract_file
        copy_tree = extract_tree
    else:
        copy_file = copy2
        copy_tree = cp_tree

    scriptPath = os.path.abspath(sys.argv[0])
    scriptDir = os.path.dirname(scriptPath)
    os.chdir(scriptDir)

    print(f'*** Installing {APPNAME} {VERSION} ***\n')
    homePath = str(Path.home()).replace('\\', '/')
    applicationDir = f'{homePath}/.novx/'
    if not os.path.isdir(applicationDir):
        print(
            'ERROR: Cannot find a novelibre installation '
            f'at "{os.path.normpath(applicationDir)}".'
        )
        input('Press ENTER to quit.')
        sys.exit(1)

    installDir = f'{applicationDir}{APPNAME}'
    if os.path.isfile(f'{installDir}/{APP}'):
        simpleUpdate = True
    else:
        simpleUpdate = False
    cnfDir = f'{installDir}{INI_PATH}'
    os.makedirs(cnfDir, exist_ok=True)

    #--- Delete the old version, but retain configuration, if any.
    rmtree(f'{installDir}/icons', ignore_errors=True)
    rmtree(f'{installDir}/sample', ignore_errors=True)
    with os.scandir(installDir) as files:
        for file in files:
            if 'config' in file.name:
                continue

            os.remove(file)
            print(f'"{os.path.normpath(file)}" removed.')

    #--- Install the new version.
    print(f'Copying "{APP}" ...')
    copy_file(APP, installDir)

    #--- Install the icon files.
    print('Copying icons ...')
    copy_tree('icons', installDir)

    #--- Make the script executable under Linux.
    st = os.stat(f'{installDir}/{APP}')
    os.chmod(f'{installDir}/{APP}', st.st_mode | stat.S_IEXEC)

    #--- Provide the sample files.
    print('Copying sample files ...')
    copy_tree('sample', installDir)

    #--- Display a success message.
    print(
        f'\nSucessfully installed {APPNAME} '
        f'at "{os.path.normpath(installDir)}".'
    )

    #--- Ask for shortcut creation.
    if not simpleUpdate:
        print(SHORTCUT_MESSAGE)
        if messagebox.askyesno(
            title=f'{APPNAME} {VERSION} Setup',
            message='Open the installation folder now?',
        ):
            open_folder(installDir)
            input('Press ENTER to quit.')
    else:
        input('Press ENTER to quit.')


def main(zipped=True):
    try:
        install(zipped)
    except Exception as ex:
        print(str(ex))
        input('Press ENTER to quit.')

