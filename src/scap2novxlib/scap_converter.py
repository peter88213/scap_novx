"""Provide a Scapple converter class for Scapple diagram import. 

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/noveltree_scapple
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os

from novxlib.model.novel import Novel
from novxlib.model.nv_tree import NvTree
from novxlib.novx.data_writer import DataWriter
from novxlib.novx.novx_file import NovxFile
from scap2novxlib.scap_file import ScapFile


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

