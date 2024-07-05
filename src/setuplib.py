"""scap_novx installer library module. 

Version @release

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from shutil import copytree
from shutil import copy2
import zipfile
import os
import sys
import stat
from shutil import rmtree
from pathlib import Path
from string import Template
try:
    from tkinter import *
except ModuleNotFoundError:
    print('The tkinter module is missing. Please install the tk support package for your python3 version.')
    sys.exit(1)

from tkinter import messagebox
import relocate

APPNAME = 'scap_novx'
VERSION = ' @release'
APP = f'{APPNAME}.py'
INI_FILE = f'{APPNAME}.ini'
INI_PATH = '/config/'
SAMPLE_PATH = 'sample/'
SUCCESS_MESSAGE = '''

$Appname is installed here:

$Apppath'''

SHORTCUT_MESSAGE = '''
Now you might want to create a shortcut on your desktop.  

On Windows, open the installation folder, hold down the Alt key on your keyboard, 
and then drag and drop $Appname.py to your desktop.

On Linux, create a launcher on your desktop. With xfce for instance, the launcher's command may look like this:
python3 '$Apppath' %F
'''

root = Tk()
processInfo = Label(root, text='')
message = []

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


def output(text):
    message.append(text)
    processInfo.config(text=('\n').join(message))


def open_folder(installDir):
    """Open an installation folder window in the file manager.
    """
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


def install(novxPath, zipped):
    """Install the script."""
    if zipped:
        copy_file = extract_file
        copy_tree = extract_tree
    else:
        copy_file = copy2
        copy_tree = cp_tree

    #--- Relocate the v1.x installation directory, if necessary.
    message = relocate.main()
    if message:
        messagebox.showinfo('Moving the novelibre installation directory', message)

    # Create a general novelibre installation directory, if necessary.
    os.makedirs(novxPath, exist_ok=True)
    installDir = f'{novxPath}{APPNAME}'
    cnfDir = f'{installDir}{INI_PATH}'
    if os.path.isfile(f'{installDir}/{APP}'):
        simpleUpdate = True
    else:
        simpleUpdate = False
    os.makedirs(cnfDir, exist_ok=True)

    # Delete the old version, but retain configuration, if any.
    rmtree(f'{installDir}/icons', ignore_errors=True)
    with os.scandir(installDir) as files:
        for file in files:
            if not 'config' in file.name:
                os.remove(file)
                output(f'Removing "{file.name}"')

    # Install the new version.
    output(f'Copying "{APP}" ...')
    copy_file(APP, installDir)

    # Install the icon files.
    output('Copying icons ...')
    copy_tree('icons', installDir)

    # Make the script executable under Linux.
    st = os.stat(f'{installDir}/{APP}')
    os.chmod(f'{installDir}/{APP}', st.st_mode | stat.S_IEXEC)

    # Display a success message.
    mapping = {'Appname': APPNAME, 'Apppath': f'{installDir}/{APP}'}
    output(Template(SUCCESS_MESSAGE).safe_substitute(mapping))

    # Ask for shortcut creation.
    if not simpleUpdate:
        output(Template(SHORTCUT_MESSAGE).safe_substitute(mapping))


def main(zipped=True):
    scriptPath = os.path.abspath(sys.argv[0])
    scriptDir = os.path.dirname(scriptPath)
    os.chdir(scriptDir)

    # Open a tk window.
    root.geometry("800x600")
    root.title(f'Install {APPNAME}{VERSION}')
    header = Label(root, text='')
    header.pack(padx=5, pady=5)

    # Prepare the messaging area.
    processInfo.pack(padx=5, pady=5)

    # Run the installation.
    homePath = str(Path.home()).replace('\\', '/')
    novxPath = f'{homePath}/.novx/'
    try:
        install(novxPath, zipped)
    except Exception as ex:
        output(str(ex))

    # Show options: open installation folders or quit.
    root.openButton = Button(text="Open installation folder", command=lambda: open_folder(f'{homePath}/.novx/{APPNAME}'))
    root.openButton.config(height=1, width=30)
    root.openButton.pack(padx=5, pady=5)
    root.quitButton = Button(text="Quit", command=quit)
    root.quitButton.config(height=1, width=30)
    root.quitButton.pack(padx=5, pady=5)
    root.mainloop()
