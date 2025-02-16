"""Provide a class for a novelibre project tree substitute.

This is a variant that gives the parents of plot points.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvlib.model.data.nv_tree import NvTree
from nvlib.novx_globals import PLOT_POINT_PREFIX


class ScNvTree(NvTree):

    def parent(self, item):
        """Return the ID of the parent of item, or '' if item is at the
        top level of the hierarchy."""
        if item.startswith(PLOT_POINT_PREFIX):
            for plId, ppIds in self.srtTurningPoints.items():
                if item in ppIds:
                    return plId

        raise NotImplementedError

