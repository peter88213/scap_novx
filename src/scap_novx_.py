"""Scapple to novelibre converter 

usage: scap_novx.py [--silent] Sourcefile

Version @release
Requires Python 3.6+
Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
from pathlib import Path
from novxlib.ui.ui import Ui
from novxlib.ui.ui_tk import UiTk
from novxlib.config.configuration import Configuration
from scapnovxlib.scap_converter import ScapConverter

SUFFIX = ''
APPNAME = 'scap_novx'
GREEN = '0.0 0.5 0.0'
BLUE = '0.0 0.0 1.0'
RED = '1.0 0.0 0.0'
PURPLE = '0.5 0.0 0.5'
SETTINGS = dict(
    location_color=BLUE,
    item_color=GREEN,
    major_chara_color=RED,
    minor_chara_color=PURPLE,
    )
OPTIONS = dict(
    export_sections=True,
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
