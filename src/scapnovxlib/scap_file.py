"""Provide a class for Scapple file representation.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from nvlib.model.data.chapter import Chapter
from nvlib.model.data.character import Character
from nvlib.model.data.plot_line import PlotLine
from nvlib.model.data.plot_point import PlotPoint
from nvlib.model.data.section import Section
from nvlib.model.data.world_element import WorldElement
from nvlib.model.novx.novx_file import NovxFile
from nvlib.novx_globals import CHAPTER_PREFIX
from nvlib.novx_globals import CHARACTER_PREFIX
from nvlib.novx_globals import CH_ROOT
from nvlib.novx_globals import CR_ROOT
from nvlib.novx_globals import ITEM_PREFIX
from nvlib.novx_globals import IT_ROOT
from nvlib.novx_globals import LC_ROOT
from nvlib.novx_globals import LOCATION_PREFIX
from nvlib.novx_globals import PLOT_LINE_PREFIX
from nvlib.novx_globals import PLOT_POINT_PREFIX
from nvlib.novx_globals import PL_ROOT
from nvlib.novx_globals import SECTION_PREFIX
from scapnovxlib.scap_note import ScapNote
import xml.etree.ElementTree as ET


class ScapFile(NovxFile):
    """File representation of a Scapple file. 

    Represents a scap file containing an outline according to the conventions.
    - Sections are shadowed.
    - Characters/locations/items are color-coded.
    """
    EXTENSION = '.scap'
    DESCRIPTION = 'Scapple diagram'
    SUFFIX = ''

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables and ScapNote class variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            location_color -- str: RGB text color that marks the locations in Scapple.
            item_color -- str: RGB text color that marks the items in Scapple.
            major_chara_color -- str: RGB text color that marks the major racters in Scapple.
            minor_chara_color -- str: RGB text color that marks the minor characters in Scapple.
            export_sections -- bool: if True, create sections from Scapple notes.
            export_characters -- bool: if True, create characters from Scapple notes.
            export_locations -- bool: if True, create location from Scapple notes. 
            export_items -- bool: if True, create items from Scapple notes. 
        
        Extends the superclass constructor.
        """
        ScapNote.locationColor = kwargs['location_color']
        ScapNote.plotLineColor = kwargs['plot_line_color']
        ScapNote.itemColor = kwargs['item_color']
        ScapNote.majorCharaColor = kwargs['major_chara_color']
        ScapNote.minorCharaColor = kwargs['minor_chara_color']
        super().__init__(filePath, **kwargs)
        self._exportSections = kwargs['export_sections']
        self._exportCharacters = kwargs['export_characters']
        self._exportLocations = kwargs['export_locations']
        self._exportItems = kwargs['export_items']
        self._exportPlotLines = kwargs['export_plot_lines']

    def read(self):
        """Parse the Scapple xml file, fetching the Novel attributes.
        
        Create an object structure of Scapple notes.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def create_novel_element(note):
            # Create a section, character, etc. from the note.

            if note.isSection:
                if not self._exportSections:
                    return

                scId = f'{SECTION_PREFIX}{note.uid}'
                self.novel.sections[scId] = Section(scene=0)
                self.novel.sections[scId].title = note.text.strip()
                self.novel.sections[scId].scType = 0
                self.novel.sections[scId].status = 1
                # status = Outline
                self.novel.sections[scId].sectionContent = '<p></p>'
                return

            if note.isPlotLine:
                if not self._exportPlotLines:
                    return

                plId = f'{PLOT_LINE_PREFIX}{note.uid}'
                self.novel.plotLines[plId] = PlotLine()
                plotLineTitle = note.text.strip().split(':', maxsplit=1)
                if len(plotLineTitle) > 1:
                    self.novel.plotLines[plId].shortName = plotLineTitle[0].strip()
                    self.novel.plotLines[plId].title = plotLineTitle[1].strip()
                else:
                    self.novel.plotLines[plId].shortName = plotLineTitle[0][0]
                    self.novel.plotLines[plId].title = plotLineTitle[0]
                self.novel.tree.append(PL_ROOT, plId)
                return

            if note.isPlotPoint:
                if not self._exportPlotLines:
                    return

                ppId = f'{PLOT_POINT_PREFIX}{note.uid}'
                self.novel.plotPoints[ppId] = PlotPoint()
                self.novel.plotPoints[ppId].title = note.text.strip()
                return

            if note.isMajorChara:
                if not self._exportCharacters:
                    return

                crId = f'{CHARACTER_PREFIX}{note.uid}'
                self.novel.characters[crId] = Character()
                self.novel.characters[crId].title = note.text.strip()
                self.novel.characters[crId].fullName = note.text.strip()
                self.novel.characters[crId].isMajor = True
                self.novel.tree.append(CR_ROOT, crId)
                return

            if note.isMinorChara:
                if not self._exportCharacters:
                    return

                crId = f'{CHARACTER_PREFIX}{note.uid}'
                self.novel.characters[crId] = Character()
                self.novel.characters[crId].title = note.text.strip()
                self.novel.characters[crId].fullName = note.text.strip()
                self.novel.characters[crId].isMajor = False
                self.novel.tree.append(CR_ROOT, crId)
                return

            if note.isLocation:
                if not self._exportLocations:
                    return

                lcId = f'{LOCATION_PREFIX}{note.uid}'
                self.novel.locations[lcId] = WorldElement()
                self.novel.locations[lcId].title = note.text.strip()
                self.novel.tree.append(LC_ROOT, lcId)
                return

            if note.isItem:
                if not self._exportItems:
                    return

                itId = f'{ITEM_PREFIX}{note.uid}'
                self.novel.items[itId] = WorldElement()
                self.novel.items[itId].title = note.text.strip()
                self.novel.tree.append(IT_ROOT, itId)

        def set_description(elemId, elements):
            for uid in scapNotes[elemId[2:]].connections:
                if scapNotes[uid].isDescription:
                    elements[elemId].desc = scapNotes[uid].text.strip()
                    return

        def set_notes(elemId, elements):
            elementNotes = []
            for uid in scapNotes[elemId[2:]].connections:
                if scapNotes[uid].isNote:
                    elementNotes .append(scapNotes[uid].text)
            elements[elemId].notes = '\n'.join(elementNotes)

        def set_relationships(scId):

            def add_relationship(uid):
                # Add related element specified by uid to the section's corresponding list.

                plId = f'{PLOT_LINE_PREFIX}{uid}'
                if plId in self.novel.plotLines:
                    scPlotLines.append(plId)
                    return

                ppId = f'{PLOT_POINT_PREFIX}{uid}'
                if ppId in self.novel.plotPoints:
                    scPlotPoints.append(ppId)
                    return

                crId = f'{CHARACTER_PREFIX}{uid}'
                if crId in self.novel.characters:
                    if scId[2:] in scapNotes[uid].pointTo:
                        scCharacters.insert(0, crId)
                        # setting the viewpoint
                    else:
                        scCharacters.append(crId)
                    return

                lcId = f'{LOCATION_PREFIX}{uid}'
                if lcId in self.novel.locations:
                    scLocations.append(lcId)
                    return

                itId = f'{ITEM_PREFIX}{uid}'
                if itId in self.novel.items:
                    scItems.append(itId)
                    return

            scCharacters = []
            scLocations = []
            scItems = []
            scPlotLines = []
            scPlotPoints = []
            for uid in scapNotes[scId[2:]].connections:
                add_relationship(uid)
            self.novel.sections[scId].characters = scCharacters
            self.novel.sections[scId].locations = scLocations
            self.novel.sections[scId].items = scItems
            self.novel.sections[scId].plotLines = scPlotLines
            for ppId in scPlotPoints:
                plId = self.novel.tree.parent(ppId)
                self.novel.sections[scId].scPlotPoints[ppId] = plId
                self.novel.plotPoints[ppId].sectionAssoc = scId
                if not plId in scPlotLines:
                    scPlotLines.append(plId)
            for plId in scPlotLines:
                plSections = self.novel.plotLines[plId].sections
                if plSections is None:
                    plSections = []
                plSections.append(scId)
                self.novel.plotLines[plId].sections = plSections

        def set_tags(elemId, elements):
            elementTags = []
            for uid in scapNotes[elemId[2:]].connections:
                if scapNotes[uid].isTag:
                    elementTags.append(scapNotes[uid].text)
            elements[elemId].tags = elementTags

        #--- Get the Scapple notes.
        self._tree = ET.parse(self.filePath)
        root = self._tree.getroot()

        #--- Create a single chapter.
        chId = f'{CHAPTER_PREFIX}1'
        self.novel.chapters[chId] = Chapter(chLevel=2, chType=0)
        self.novel.chapters[chId].title = 'Chapter 1'
        self.novel.tree.append(CH_ROOT, chId)

        #--- Create Novel elements from the notes.
        scapNotes = {}
        uidByPos = {}
        for xmlNote in root.iter('Note'):
            note = ScapNote()
            note.parse_xml(xmlNote)
            scapNotes[note.uid] = note
            uidByPos[note.position] = note.uid
            create_novel_element(note)

        #--- Sort the sections by note position and put them into the chapter.
        srtNotes = sorted(uidByPos.items())
        for srtNote in srtNotes:
            scId = f'{SECTION_PREFIX}{srtNote[1]}'
            if scId in self.novel.sections:
                self.novel.tree.append(chId, scId)

        #--- Assign plot points to plot lines.
        plotPoints = []
        for plId in self.novel.plotLines:
            for uid in scapNotes[plId[2:]].connections:
                if not scapNotes[uid].isPlotPoint:
                    continue

                ppId = f'{PLOT_POINT_PREFIX}{uid}'
                if ppId in plotPoints:
                    continue

                self.novel.tree.append(plId, ppId)
                plotPoints.append(ppId)
                searchNext = True
                while searchNext:
                    searchNext = False
                    for uid in scapNotes[ppId[2:]].connections:
                        if not scapNotes[uid].isPlotPoint:
                            continue

                        ppId = f'{PLOT_POINT_PREFIX}{uid}'
                        if ppId in plotPoints:
                            continue

                        self.novel.tree.append(plId, ppId)
                        plotPoints.append(ppId)
                        searchNext = True
                        break

        # Set the elements' properties.

        for scId in self.novel.sections:
            set_relationships(scId)
            set_description(scId, self.novel.sections)
            set_tags(scId, self.novel.sections)
            set_notes(scId, self.novel.sections)

        for crId in self.novel.characters:
            set_description(crId, self.novel.characters)
            set_tags(crId, self.novel.characters)
            set_notes(crId, self.novel.characters)

        for lcId in self.novel.locations:
            set_description(lcId, self.novel.locations)
            set_tags(lcId, self.novel.locations)

        for itId in self.novel.items:
            set_description(itId, self.novel.items)
            set_tags(itId, self.novel.items)

        for plId in self.novel.plotLines:
            set_description(plId, self.novel.plotLines)

        for ppId in self.novel.plotPoints:
            set_description(ppId, self.novel.plotPoints)

        self.novel.check_locale()

        return 'Scapple data converted to novel structure.'

