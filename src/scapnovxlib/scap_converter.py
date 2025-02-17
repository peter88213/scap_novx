"""Provide a Scapple converter class for Scapple diagram import. 

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os

from nvlib.model.data.novel import Novel
from nvlib.model.data.nv_tree import NvTree
from nvlib.model.novx.data_writer import DataWriter
from nvlib.model.novx.novx_file import NovxFile
from scapnovxlib.scap_file import ScapFile


class ScapConverter:
    """A converter class for Scapple diagram import."""

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        """
        self.newFile = None

        if not os.path.isfile(sourcePath):
            self.ui.set_status(f'!File "{os.path.normpath(sourcePath)}" not found.')
            return
        fileName, fileExtension = os.path.splitext(sourcePath)
        if fileExtension == ScapFile.EXTENSION:
            if not os.path.isfile(f'{fileName}{NovxFile.EXTENSION}'):
                target = NovxFile(f'{fileName}{NovxFile.EXTENSION}', **kwargs)
            else:
                target = DataWriter(f'{fileName}{DataWriter.SUFFIX}{DataWriter.EXTENSION}', **kwargs)
            source = ScapFile(sourcePath, **kwargs)
            source.novel = Novel(tree=NvTree())
            source.read()
            target.novel = source.novel
            target.write()
        else:
            self.ui.set_status(f'!File type of "{os.path.normpath(sourcePath)}" not supported.')
        self.ui.set_status(f'{target.DESCRIPTION} successfully created.')

