"""Provide a Scapple converter class for Scapple diagram import. 

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_scapple
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
from novxlib.novx_globals import *
from novxlib.novx.novx_file import NovxFile
from novxlib.novx.data_writer import DataWriter
from novxlib.converter.converter import Converter
from nvscapplelib.scap_file import ScapFile


class ScapConverter(Converter):
    """A converter class for Scapple diagram import.

    Public methods:
        run(sourcePath, **kwargs) -- Create source and target objects and run conversion.
    """

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        """
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!File "{os.path.normpath(sourcePath)}" not found.')
            return
        fileName, fileExtension = os.path.splitext(sourcePath)
        if fileExtension == ScapFile.EXTENSION:
            sourceFile = ScapFile(sourcePath, **kwargs)
            if os.path.isfile(f'{fileName}{NovxFile.EXTENSION}'):
                targetFile = DataWriter(f'{fileName}{DataWriter.EXTENSION}', **kwargs)
                self.import_to_novx(sourceFile, targetFile)
            else:
                targetFile = NovxFile(f'{fileName}{NovxFile.EXTENSION}', **kwargs)
                self.create_novx(sourceFile, targetFile)
        else:
            self.ui.set_info_how(f'!File type of "{os.path.normpath(sourcePath)}" not supported.')
