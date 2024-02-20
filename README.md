[![Download the latest release](docs/img/download-button.png)](https://raw.githubusercontent.com/peter88213/scap_novx/main/dist/scap_novx_v2.0.0.zip)
[![Changelog](docs/img/changelog-button.png)](docs/changelog.md)
[![News](docs/img/news-button.png)](https://github.com/peter88213/noveltree/discussions/1)
[![Online help](docs/img/help-button.png)](docs/usage.md)

# ![S](icons/sLogo32.png) scap_novx

A Python script for creating new [noveltree](https://github.com/peter88213/noveltree/) projects from Scapple diagrams 

![Screenshot: Example](docs/Screenshots/screen01.png)

## Features

- Notes with a shadow are converted to sections in one single chapter.
- Notes with a "cloud" border and shadow are converted to "Notes" sections.
- Notes with a "cloud" border without shadow are converted to section and character notes.
- Notes with a square border are converted to tags.
- Notes with colored text are converted to characters, locations, or items.
- Connections between sections and characters/locations/items are considered.
- If a noveltree project already exists, Character/Location/Item XML files are generated instead.
- The *scap_novx* release includes a sample Scapple file with note styles to import.

 
## Requirements

- [Python](https://www.python.org/) version 3.6+.
- [Scapple 1.x](https://www.literatureandlatte.com/scapple/overview).


## Download and install

[Download the latest release (version 2.0.0)](https://raw.githubusercontent.com/peter88213/scap_novx/main/dist/scap_novx_v2.0.0.zip)

- Unzip the downloaded zipfile "scap_novx_v2.0.0.zip" into a new folder.
- Move into this new folder and launch **setup.pyw**. This installs the script for the local user.
- Create a shortcut on the desktop when asked.
- Open "README.md" for usage instructions.

### Note for Linux users

Please make sure that your Python3 installation has the *tkinter* module. On Ubuntu, for example, it is not available out of the box and must be installed via a separate package. 

------------------------------------------------------------------

[Changelog](docs/changelog.md)

## Usage

See the [instructions for use](docs/usage.md)

## Credits

- Frederik Lundh published the [xml pretty print algorithm](http://effbot.org/zone/element-lib.htm#prettyprint).


## License

This is Open Source software, and scap_novx is licensed under GPLv3. See the
[GNU General Public License website](https://www.gnu.org/licenses/gpl-3.0.en.html) for more
details, or consult the [LICENSE](https://github.com/peter88213/scap_novx/blob/main/LICENSE) file.


 




