"""Provide a class for Scapple file representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/novelyst_scapple
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import xml.etree.ElementTree as ET
from novxlib.novx_globals import *
from novxlib.novx.novx_file import NovxFile
from novxlib.model.chapter import Chapter
from novxlib.model.section import Section
from novxlib.model.character import Character
from novxlib.model.world_element import WorldElement
from nvscapplelib.scap_note import ScapNote


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
        chId = '1'
        self.chapters[chId] = Chapter()
        self.chapters[chId].title = 'Chapter 1'
        self.srtChapters = [chId]

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
                    section = Section()
                    section.title = note.text
                    section.isNotesSection = note.isNotesSection
                    section.status = 1
                    # Status = Outline
                    self.sections[note.uid] = section
            elif note.isMajorChara:
                if self._exportCharacters:
                    character = Character()
                    character.title = note.text
                    character.fullName = note.text
                    character.isMajor = True
                    self.characters[note.uid] = character
                    self.srtCharacters.append(note.uid)
            elif note.isMinorChara:
                if self._exportCharacters:
                    character = Character()
                    character.title = note.text
                    character.fullName = note.text
                    character.isMajor = False
                    self.characters[note.uid] = character
                    self.srtCharacters.append(note.uid)
            elif note.isLocation:
                if self._exportLocations:
                    location = WorldElement()
                    location.title = note.text
                    self.locations[note.uid] = location
                    self.srtLocations.append(note.uid)
            elif note.isItem:
                if self._exportItems:
                    item = WorldElement()
                    item.title = note.text
                    self.items[note.uid] = item
                    self.srtItems.append(note.uid)

        #--- Sort notes by position.
        srtNotes = sorted(uidByPos.items())
        for srtNote in srtNotes:
            if srtNote[1] in self.sections:
                self.chapters[chId].srtSections.append(srtNote[1])

        #--- Assign characters/locations/items/tags/notes to the sections.
        for scId in self.sections:
            self.sections[scId].characters = []
            self.sections[scId].locations = []
            self.sections[scId].items = []
            self.sections[scId].tags = []
            self.sections[scId].sectionNotes = ''
            for uid in scapNotes[scId].connections:
                if uid in self.characters:
                    if scId in scapNotes[uid].pointTo:
                        self.sections[scId].characters.insert(0, uid)
                    else:
                        self.sections[scId].characters.append(uid)
                elif uid in self.locations:
                    self.sections[scId].locations.append(uid)
                elif uid in self.items:
                    self.sections[scId].items.append(uid)
                elif scapNotes[uid].isTag:
                    self.sections[scId].tags.append(scapNotes[uid].text)
                elif scapNotes[uid].isNote:
                    self.sections[scId].sectionNotes = f'{self.sections[scId].sectionNotes}{scapNotes[uid].text}'

        #--- Assign tags/notes to the characters.
        for crId in self.characters:
            self.characters[crId].tags = []
            self.characters[crId].notes = ''
            for uid in scapNotes[crId].connections:
                if scapNotes[uid].isTag:
                    self.characters[crId].tags.append(scapNotes[uid].text)
                elif scapNotes[uid].isNote:
                    self.characters[crId].notes = f'{self.characters[crId].notes}{scapNotes[uid].text}'

        #--- Assign tags to the locations.
        for lcId in self.locations:
            self.locations[lcId].tags = []
            for uid in scapNotes[lcId].connections:
                if scapNotes[uid].isTag:
                    self.locations[lcId].tags.append(scapNotes[uid].text)

        #--- Assign tags to the items.
        for itId in self.items:
            self.items[itId].tags = []
            for uid in scapNotes[itId].connections:
                if scapNotes[uid].isTag:
                    self.items[itId].tags.append(scapNotes[uid].text)
        return 'Scapple data converted to novel structure.'
