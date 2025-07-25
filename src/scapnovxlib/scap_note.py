"""Provide a class for Scapple note representation.

Copyright (c) 2025 Peter Triesberger
For further information see https://github.com/peter88213/scap_novx
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""


class ScapNote:
    """Scapple note representation.
    
    Public instance variables:
        text -- str: note text.
        isSection -- bool: True, if the note represents a novelibre section.
        isTag -- bool: True, if the note represents a novelibre tag.
        isNote -- bool: True, if the note represents a novelibre note.
        self.textColor -- str: text color; RGB components in a single string.
        connections -- list of connected note IDs.
        pointTo -- list of note IDs pointed to.
        position -- float: combined x/y position.
        uid -- str: Scapple UID, incremented by 1.
    """
    Y_FACTOR = 100000
    # Sortable position = y * Y_FACTOR + x
    # This works if x and y are not greater than 9999.9
    plotLineColor = None
    locationColor = None
    itemColor = None
    majorCharaColor = None
    minorCharaColor = None

    def __init__(self):
        self.text = None
        self.isSection = None
        self.isPlotLine = None
        self.isPlotPoint = None
        self.isTag = None
        self.isNote = None
        self.isMajorChara = None
        self.isMinorChara = None
        self.isLocation = None
        self.isItem = None
        self.isDescription = None
        self.textColor = None
        self.connections = None
        self.pointTo = None
        self.position = None
        self.uid = None

    def parse_xml(self, xmlNote):
        """Parse a single Scapple note.
        
        Positional argument:
            xmlNote -- Scapple <Note> XML subtree
        """

        def str_to_rgb(colorStr):
            # Return a RGB tuple of floats for a given string.
            try:
                red, green, blue = colorStr.split(' ')
                return float(red), float(green), float(blue)
            except(ValueError):
                return (0.0, 0.0, 0.0)

        def color_matches(color1, color2):
            # Return True if color1 is close to color2, otherwise return False.
            TOLERANCE = 0.1
            c1 = str_to_rgb(color1)
            c2 = str_to_rgb(color2)
            for i in range(3):
                if abs(c1[i] - c2[i]) > TOLERANCE:
                    return False

            return True

        self.isSection = False
        self.isPlotLine = False
        self.isPlotPoint = False
        self.isTag = False
        self.isNote = False
        self.isMajorChara = False
        self.isMinorChara = False
        self.isLocation = False
        self.isItem = False
        self.isDescription = False
        self.textColor = ''
        self.text = xmlNote.find('String').text
        positionStr = xmlNote.attrib['Position'].split(',')
        self.position = (
            float(positionStr[1]) * self.Y_FACTOR + float(positionStr[0])
        )

        # Set UID.
        # Because Scapple UIDs begin with zero, they are all
        # incremented by 1 for novelibre use.
        scappId = xmlNote.attrib['ID']
        self.uid = str(int(scappId) + 1)
        appearance = xmlNote.find('Appearance')

        color = appearance.find('TextColor')
        if color is not None:
            self.textColor = color.text

        border = appearance.find('Border')
        if border is not None:
            borderStyle = border.attrib.get('Style', '')
            borderWeight = border.attrib.get('Weight', '0')
        else:
            borderStyle = ''
            borderWeight = '0'

        if 'Shadow' in xmlNote.attrib:
            self.isSection = True
        elif borderStyle == 'Square':
            self.isTag = True
        elif borderStyle == 'Cloud':
            self.isNote = True
        elif color_matches(self.textColor, self.plotLineColor):
            if borderWeight == '0':
                self.isPlotPoint = True
            else:
                self.isPlotLine = True
        elif color_matches(self.textColor, self.majorCharaColor):
            self.isMajorChara = True
        elif color_matches(self.textColor, self.minorCharaColor):
            self.isMinorChara = True
        elif color_matches(self.textColor, self.locationColor):
            self.isLocation = True
        elif color_matches(self.textColor, self.itemColor):
            self.isItem = True
        elif borderWeight == '0':
            self.isDescription = True

        #--- Create a list of connected notes.
        self.connections = []
        if xmlNote.find('ConnectedNoteIDs') is not None:
            connGroups = xmlNote.find('ConnectedNoteIDs').text.split(', ')
            for connText in connGroups:
                if '-' in connText:
                    conns = connText.split('-')
                    start = int(conns[0]) + 1
                    end = int(conns[1]) + 2
                    for i in range(start, end):
                        self.connections.append(str(i))
                else:
                    i = int(connText) + 1
                    self.connections.append(str(i))

        #--- Create a list of notes pointed to.
        self.pointTo = []
        if xmlNote.find('PointsToNoteIDs') is not None:
            pointGroups = xmlNote.find('PointsToNoteIDs').text.split(', ')
            for pointText in pointGroups:
                if '-' in pointText:
                    points = pointText.split('-')
                    start = int(points[0]) + 1
                    end = int(points[1]) + 2
                    for i in range(start, end):
                        self.pointTo.append(str(i))
                else:
                    i = int(pointText) + 1
                    self.pointTo.append(str(i))
