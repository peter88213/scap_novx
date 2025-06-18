"""Scapple to novelibre converter 

usage: scap_novx.py [--silent] Sourcefile

Version @release
Requires Python 3.6+
Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by 
the Free Software Foundation, either version 3 of the License, or 
(at your option) any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of 
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.
"""
import os
from pathlib import Path
import sys

from nvlib.configuration.configuration import Configuration
from nvlib.user_interface.ui import Ui
from nvlib.user_interface.ui_tk import UiTk
from scapnovxlib.scap_converter import ScapConverter

SUFFIX = ''
APPNAME = 'scap_novx'
GREEN = '0.0 0.5 0.0'
BLUE = '0.0 0.0 1.0'
RED = '1.0 0.0 0.0'
PURPLE = '0.5 0.0 0.5'
SAND = '0.6 0.2 0.0'
SETTINGS = dict(
    location_color=BLUE,
    item_color=GREEN,
    major_chara_color=RED,
    minor_chara_color=PURPLE,
    plot_line_color=SAND,
)
OPTIONS = dict(
    export_sections=True,
    export_plot_lines=True,
    export_characters=True,
    export_locations=True,
    export_items=True,
)


def main(sourcePath, silentMode=True, installDir='.'):
    if silentMode:
        ui = Ui('')
    else:
        ui = UiTk('Scapple to novelibre converter @release')

    #--- Try to get persistent configuration data
    sourceDir = os.path.dirname(sourcePath)
    if not sourceDir:
        sourceDir = '.'
    iniFileName = f'{APPNAME}.ini'
    iniFiles = [f'{installDir}/config/{iniFileName}', f'{sourceDir}/{iniFileName}']
    configuration = Configuration(SETTINGS, OPTIONS)
    for iniFile in iniFiles:
        configuration.read(iniFile)
    kwargs = {'suffix': SUFFIX}
    kwargs.update(configuration.settings)
    kwargs.update(configuration.options)
    converter = ScapConverter()
    converter.ui = ui
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    silentMode = False
    sourcePath = ''
    if len(sys.argv) > 1:
        sourcePath = sys.argv[-1]
        silentMode = sys.argv[1] in ['--silent', '-s']
    else:
        print('usage: scap_novx.py [--silent] Sourcefile')
        sys.exit(1)
    try:
        homeDir = str(Path.home()).replace('\\', '/')
        installDir = f'{homeDir}/.novx/{APPNAME}/config'
    except:
        installDir = '.'
    main(sourcePath, silentMode, installDir)
