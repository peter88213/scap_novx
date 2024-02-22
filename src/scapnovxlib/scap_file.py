"""Provide a class for Scapple file representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from novxlib.model.chapter import Chapter
from novxlib.model.character import Character
from novxlib.model.section import Section
from novxlib.model.world_element import WorldElement
from novxlib.novx.novx_file import NovxFile
from novxlib.novx_globals import ARC_PREFIX
from novxlib.novx_globals import ARC_POINT_PREFIX
from novxlib.novx_globals import CHAPTER_PREFIX
from novxlib.novx_globals import CHARACTER_PREFIX
from novxlib.novx_globals import CH_ROOT
from novxlib.novx_globals import AC_ROOT
from novxlib.novx_globals import CR_ROOT
from novxlib.novx_globals import ITEM_PREFIX
from novxlib.novx_globals import IT_ROOT
from novxlib.novx_globals import LC_ROOT
from novxlib.novx_globals import LOCATION_PREFIX
from novxlib.novx_globals import SECTION_PREFIX
from scapnovxlib.scap_note import ScapNote
import xml.etree.ElementTree as ET


class ScapFile(NovxFile):
    """File representation of a Scapple file. 

    Represents a scap file containing an outline according to the conventions.
    - Sections are shadowed.
    - Characters/locations/items are textColor-coded.
    """
    EXTENSION = '.scap'
    DESCRIPTION = 'Scapple diagram'
    SUFFIX = ''

    # Events assigned to the "narrative arc" (case insensitive) become
    # regular sections, the others become Notes sections.

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
        ScapNote.arcColor = kwargs['arc_color']
        ScapNote.itemColor = kwargs['item_color']
        ScapNote.majorCharaColor = kwargs['major_chara_color']
        ScapNote.minorCharaColor = kwargs['minor_chara_color']
        super().__init__(filePath, **kwargs)
        self._exportSections = kwargs['export_sections']
        self._exportCharacters = kwargs['export_characters']
        self._exportLocations = kwargs['export_locations']
        self._exportItems = kwargs['export_items']

    def read(self):
        """Parse the Scapple xml file, fetching the Novel attributes.
        
        Create an object structure of Scapple notes.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
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
        for xmlNote in root.iter('Note'):
            note = ScapNote()
            note.parse_xml(xmlNote)
            scapNotes[note.uid] = note
            uidByPos[note.position] = note.uid

            # Create Novel elements.
            if note.isSection:
                if self._exportSections:
                    scId = f'{SECTION_PREFIX}{note.uid}'
                    self.novel.sections[scId] = Section(scPacing=0)
                    self.novel.sections[scId].title = note.text.strip()
                    self.novel.sections[scId].scType = 0
                    self.novel.sections[scId].status = 1
                    # Status = Outline
                    self.novel.sections[scId].sectionContent = '<p></p>'
            elif note.isArc:
                if self._exportArcs:
                    acId = f'{ARC_PREFIX}{note.uid}'
                    self.novel.arcs[acId] = Character()
                    arcTitle = note.text.strip().split(':', maxsplit=1)
                    if len(arcTitle) > 1:
                        self.novel.arcs[acId].shortName = arcTitle[0].strip()
                        self.novel.arcs[acId].title = arcTitle[1].strip()
                    else:
                        self.novel.arcs[acId].shortName = arcTitle[0][0]
                        self.novel.arcs[acId].title = arcTitle[0]
                    self.novel.tree.append(AC_ROOT, acId)
            elif note.isPoint:
                if self._exportArcs:
                    tpId = f'{ARC_POINT_PREFIX}{note.uid}'
                    self.novel.arcs[tpId] = Character()
                    self.novel.arcs[tpId].title = note.text.strip()
                    self.novel.tree.append(acId, tpId)
                    # TODO: Create sorted lists of connected points
            elif note.isMajorChara:
                if self._exportCharacters:
                    crId = f'{CHARACTER_PREFIX}{note.uid}'
                    self.novel.characters[crId] = Character()
                    self.novel.characters[crId].title = note.text.strip()
                    self.novel.characters[crId].fullName = note.text.strip()
                    self.novel.characters[crId].isMajor = True
                    self.novel.tree.append(CR_ROOT, crId)
            elif note.isMinorChara:
                if self._exportCharacters:
                    crId = f'{CHARACTER_PREFIX}{note.uid}'
                    self.novel.characters[crId] = Character()
                    self.novel.characters[crId].title = note.text.strip()
                    self.novel.characters[crId].fullName = note.text.strip()
                    self.novel.characters[crId].isMajor = False
                    self.novel.tree.append(CR_ROOT, crId)
            elif note.isLocation:
                if self._exportLocations:
                    lcId = f'{LOCATION_PREFIX}{note.uid}'
                    self.novel.locations[lcId] = WorldElement()
                    self.novel.locations[lcId].title = note.text.strip()
                    self.novel.tree.append(LC_ROOT, lcId)
            elif note.isItem:
                if self._exportItems:
                    itId = f'{ITEM_PREFIX}{note.uid}'
                    self.novel.items[itId] = WorldElement()
                    self.novel.items[itId].title = note.text.strip()
                    self.novel.tree.append(IT_ROOT, itId)

        #--- Sort notes by position.
        srtNotes = sorted(uidByPos.items())
        for srtNote in srtNotes:
            scId = f'{SECTION_PREFIX}{srtNote[1]}'
            if scId in self.novel.sections:
                self.novel.tree.append(chId, scId)

        #--- Assign characters/locations/items/tags/notes to the sections.
        for scId in self.novel.sections:
            scCharacters = []
            scLocations = []
            scItems = []
            scTags = []
            sectionNotes = ''
            for uid in scapNotes[scId[2:]].connections:
                crId = f'{CHARACTER_PREFIX}{uid}'
                lcId = f'{LOCATION_PREFIX}{uid}'
                itId = f'{ITEM_PREFIX}{uid}'
                if crId in self.novel.characters:
                    if scId[2:] in scapNotes[uid].pointTo:
                        scCharacters.insert(0, crId)
                    else:
                        scCharacters.append(crId)
                elif lcId in self.novel.locations:
                    scLocations.append(lcId)
                elif itId in self.novel.items:
                    scItems.append(itId)
                elif scapNotes[uid].isTag:
                    scTags.append(scapNotes[uid].text)
                elif scapNotes[uid].isNote:
                    sectionNotes = f'{sectionNotes}{scapNotes[uid].text}'
            self.novel.sections[scId].characters = scCharacters
            self.novel.sections[scId].locations = scLocations
            self.novel.sections[scId].items = scItems
            self.novel.sections[scId].tags = scTags
            self.novel.sections[scId].notes = sectionNotes

        #--- Assign tags/notes to the characters.
        for crId in self.novel.characters:
            characterTags = []
            characterNotes = ''
            for uid in scapNotes[crId[2:]].connections:
                if scapNotes[uid].isTag:
                    characterTags.append(scapNotes[uid].text)
                elif scapNotes[uid].isNote:
                    characterNotes = f'{characterNotes}{scapNotes[uid].text}'
            self.novel.characters[crId].tags = characterTags
            self.novel.characters[crId].notes = characterNotes

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

        self.novel.check_locale()

        return 'Scapple data converted to novel structure.'
