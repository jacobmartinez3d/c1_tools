# C1 VR Tools for Nuke

This is a set of production tools for use in Foundry Nuke(https://www.foundry.com/products/nuke). These were developed to save time and alieviate QC errors during production of VR content.

## Getting Started

Clone or download this repository and save it to your .nuke folder. Make sure to back up your existing directory first.

In Windows 10 your .nuke folder can be found at:
```
C:\Users\<user>\.nuke
```
C1 Tools will now be loaded the next time you start Nuke.

### Prerequisites

* You must have Ffmpeg installed and the "ffmpeg" and "ffprobe" aliases added to your PATH variable in Windows.
	* To learn how to do this, follow both **Part 1 and Part 2** at: https://www.wikihow.com/Install-FFmpeg-on-Windows
* Install Python 2.7: https://www.python.org/downloads/

## First time restarting Nuke

When you first open Nuke, you'll be prompted with a one-time-only popup dialogue:

![Alt text](c1_tools/c1_Login.png?raw=true "C1 Login popup dialogue.")

* **Local working directory**: A local directory on preferably an SSD drive which you will be downloading to and working from using the Shot Browser.
* **Artist**: Artist's name. Used when submitting a shot.

#### Enter in a local directory,
Or click the "Set Working Dir" burron and navigate to one.

For example:
```
E:\Local_Working_Dir
```
This directory is where shots will be downloaded to from the server. It should be local, and fast to render to.

#### Then, enter an Artist name
Which will be used as an identifier when submitting shots.

#### Press the "Login" button,
Nuke will open with a new menu called "C1 Tools".

# C1 Tools menu

## C1 Shot Browser

Selecting this from the c1 menu will open the Shot Browser in your right pane, with the properties pane.

![Alt text](c1_tools/shot_browser.png?raw=true "C1 Shot Browser")

#### From the dropdown menu select the show you wish to download a shot from.
Here, I have chosen Brazil. All of the shots will be displayed as buttons(to download). The 2nd column shows the latest version on the server, or "No Submissions" if the shot hasn't been started yet.

#### Click a shot to start downloading.
A new shot folder will be created at your local working directory, as well as an auto-versioned folder with the previous version's nuke script inside.

This process invlves downloading the production stitches for both eyes, so it could take long...

When the download is complete, a windows explorer window will be opened containing the newly downloaded Nuke script.

### Guidelines for Nuke scripts
You must have a ** write ** node named *"\_render"* connected to the end of your network at all times:

![Alt text](c1_tools/render_network.png?raw=true "_render network")

In the write node's *"file"* knob, make sure your file-path matches this naming:

```
./Prerenders/<Nuke Script Filename>.####.png
```
C1 Naming convention:
```
<Show Code>_<Shot Name>_v000.####.png
```
The ** #### ** tells Nuke to auto-increment the frame-number.
```
Example:
./Prerenders/BRZ_D1S4_v003.####.png
```
![Alt text](c1_tools/file_knob.png?raw=true "File knob)

This way, each time you use ** * C1 Tools > Version Up * ** it will sync with the current version number.

## C1 Version Up
Once you have rendered your nuke scene, and don't want to rerender over the existing frames, you can version up. This will duplicate the current Nuke script and creates a new versioned-up folder.

## C1 Submit Shot
When you complete a shot and are ready to submit to the server, click ** *C1 Tools > C1 Submit Shot* ** from the menu, which will bring up the Shot Submission Dialogue.

![Alt text](c1_tools/submitShot_simple.png?raw=true "Submit Shot")

This dialogue will detect if there are any conflicts in versions(as seen above), and auto-version to the next available number before saving to the server.

There are also a number of other validations that take place when opening this dialogue that you should never encounter if you always use the * Shot Browser, * download and * C1 Version Up * tools.

Don't rename your local files or folders, or you will encounter these validation errors.

## Render OU.mp4 (Ffmpeg)

This tool scans the given directory for frames with naming that matches the current Nuke script. It is recommended to just navigate to a * Prerenders * folder with frames.

![Alt text](c1_tools/renderOU.png?raw=true "Render OU.mp4 (Ffmpeg)")

An Ffmpeg * .bat * file will be created in the folder, and begin running. When complete, you'll have a squished over-under mp4 located next to your Nuke script ready for viewing in GoPro VR player.

(cont...)








## Authors

* **Jacob Martinez** - *Technical Artist* - [Magnetic-Lab](https://www.magnetic-lab.com/)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Condition One(http://conditionone.com/)
* Ffmpeg
