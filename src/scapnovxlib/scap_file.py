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

        self._tree = ET.parse(self.filePath)
        root = self._tree.getroot()

        #--- Create a single chapter and assign all sections to it.
        chId = f'{CHAPTER_PREFIX}1'
        self.novel.chapters[chId] = Chapter(chLevel=2, chType=0)
        self.novel.chapters[chId].title = 'Chapter 1'
        self.srtChapters = [chId]
        self.novel.tree.append(CH_ROOT, chId)

        #--- Parse Scapple notes.
        scapNotes = {}
        uidByPos = {}

        #--- Create Novel elements from the notes.
        for xmlNote in root.iter('Note'):
            note = ScapNote()
            note.parse_xml(xmlNote)
            scapNotes[note.uid] = note
            uidByPos[note.position] = note.uid
            create_novel_element(note)

        #--- Sort notes by position.
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

        #--- Assign related elements to the sections.
        for scId in self.novel.sections:
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

        #--- Assign notes to the sections.
        for scId in self.novel.sections:
            sectionNotes = []
            for uid in scapNotes[scId[2:]].connections:
                if scapNotes[uid].isNote:
                    sectionNotes.append(scapNotes[uid].text)
            self.novel.sections[scId].notes = '\n'.join(sectionNotes)

        #--- Assign notes to the characters.
        for crId in self.novel.characters:
            characterNotes = []
            for uid in scapNotes[crId[2:]].connections:
                if scapNotes[uid].isNote:
                    characterNotes .append(scapNotes[uid].text)
            self.novel.characters[crId].notes = '\n'.join(characterNotes)

        #--- Assign tags to the sections.
        for scId in self.novel.sections:
            scTags = []
            for uid in scapNotes[scId[2:]].connections:
                if scapNotes[uid].isTag:
                    scTags.append(scapNotes[uid].text)
            self.novel.sections[scId].tags = scTags

        #--- Assign tags to the characters.
        for crId in self.novel.characters:
            characterTags = []
            for uid in scapNotes[crId[2:]].connections:
                if scapNotes[uid].isTag:
                    characterTags.append(scapNotes[uid].text)
            self.novel.characters[crId].tags = characterTags

        #--- Assign tags to the locations.
        for lcId in self.novel.locations:
            locationTags = []
            for uid in scapNotes[lcId[2:]].connections:
                if scapNotes[uid].isTag:
                    locationTags.append(scapNotes[uid].text)
            self.novel.locations[lcId].tags = locationTags

        #--- Assign tags to the items.
        for itId in self.novel.items:
            itemTags = []
            for uid in scapNotes[itId[2:]].connections:
                if scapNotes[uid].isTag:
                    itemTags.append(scapNotes[uid].text)
            self.novel.items[itId].tags = itemTags

        #--- Set section description.
        for scId in self.novel.sections:
            for uid in scapNotes[scId[2:]].connections:
                if scapNotes[uid].isDescription:
                    self.novel.sections[scId].desc = scapNotes[uid].text.strip()
                    break

        #--- Set character description.
        for crId in self.novel.characters:
            for uid in scapNotes[crId[2:]].connections:
                if scapNotes[uid].isDescription:
                    self.novel.characters[crId].desc = scapNotes[uid].text.strip()
                    break

        #--- Set location description.
        for lcId in self.novel.locations:
            for uid in scapNotes[lcId[2:]].connections:
                if scapNotes[uid].isDescription:
                    self.novel.locations[lcId].desc = scapNotes[uid].text.strip()
                    break

        #--- Set item description.
        for itId in self.novel.items:
            for uid in scapNotes[itId[2:]].connections:
                if scapNotes[uid].isDescription:
                    self.novel.items[itId].desc = scapNotes[uid].text.strip()
                    break

        #--- Set plot line description.
        for plId in self.novel.plotLines:
            for uid in scapNotes[plId[2:]].connections:
                if scapNotes[uid].isDescription:
                    self.novel.plotLines[plId].desc = scapNotes[uid].text.strip()
                    break

        #--- Set plot point description.
        for ppId in self.novel.plotPoints:
            for uid in scapNotes[ppId[2:]].connections:
                if scapNotes[uid].isDescription:
                    self.novel.plotPoints[ppId].desc = scapNotes[uid].text.strip()
                    break

        self.novel.check_locale()

        return 'Scapple data converted to novel structure.'

