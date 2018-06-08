# VR Production Tools for Nuke

This is a set of production tools for use in Foundry Nuke(https://www.foundry.com/products/nuke). These were developed to save time and alieviate QC errors during production of 360 Stereo content.

<hr>
<hr>

## Getting Started

Clone or download this repository and save it to your *".nuke"* folder. Make sure to back up your existing directory first.

In Windows 10 your .nuke folder can be found at:
```
C:\Users\<user>\.nuke
```
C1 Tools will now be loaded the next time you start Nuke.

### Prerequisites

* You must have Ffmpeg installed and the *"ffmpeg"* and *"ffprobe"* aliases added to your PATH variable in Windows.
	* To learn how to do this, follow both **Part 1** and **Part 2** at: https://www.wikihow.com/Install-FFmpeg-on-Windows
* Install Python 2.7: https://www.python.org/downloads/

### First time restarting Nuke

When you first open Nuke, you'll be prompted with a one-time-only popup dialogue:

![Alt text](c1_tools/c1_Login.png?raw=true "C1 Login popup dialogue.")

* **Local working directory**: A local directory on preferably an SSD drive which you will be downloading to and working from using the Shot Browser.
* **Artist**: Artist's name. Used when submitting a shot.

#### Enter in a local directory,
Or click the "Set Working Dir" button and navigate to one.

For example:
```
E:\Local_Working_Dir
```
This directory is where shots will be downloaded to from the server. It should be local, and fast to render to.

#### Then, enter an Artist name
Which will be used as an identifier when submitting shots.

#### Press the "Login" button,
Nuke will open with a new menu called *"C1 Tools"*.

<hr>
<hr>

# C1 Tools menu

<hr>

## C1 Shot Browser

Selecting this from the c1 menu will open the Shot Browser in your right pane.

![Alt text](c1_tools/shot_browser.png?raw=true "C1 Shot Browser")

#### From the dropdown menu select the show you wish to download a shot from.
Here, I have chosen Brazil. All of the shots will be displayed as buttons(to download). The 2nd column shows the latest version on the server, or *"No Submissions"* if the shot hasn't been started yet.

#### Click a shot to start downloading.
A new shot folder will be created at your local working directory, as well as an auto-versioned folder with the previous version's nuke script inside.

This process involves downloading the production stitches for both eyes, so it could take long...

### Guidelines for Nuke scripts
You must have a **write** node named *"\_render"* connected to the end of your network at all times:

![Alt text](c1_tools/render_network.png?raw=true "_render network")

#### In the write node's *"file"* knob, make sure your file-path matches this naming:

```
./Prerenders/<Nuke Script Filename>.####.png
```
C1 Naming convention:
```
<Show Code>_<Shot Name>_v000_%V.####.png
```
The **%V** is a variable representing whatever views are set to render - such as *left* and *right*.

The **####** tells Nuke to auto-increment the frame-number. **%04d** also works, where the number represents the amount of padding.

[Learn more about Rendering Stereoscopic Images in Nuke](https://learn.foundry.com/nuke/8.0/content/user_guide/stereoscopic_films/rendering_stereo_images.html)

Example:
```
./Prerenders/BRZ_D1S4_v003.####.png
```

![Alt text](c1_tools/file_knob.png?raw=true "File knob)

This way, each time you use ***C1 Tools > Version Up*** it will sync with the current version number.

<hr>

## C1 Version Up
Once you have rendered your nuke scene, and don't want to re-render over the existing frames, you can version up. This will duplicate the current Nuke script and creates a new versioned-up folder to work out of.

<hr>

## C1 Submit Shot
When you complete a shot and are ready to submit to the server, click ***C1 Tools > C1 Submit Shot*** from the menu, which will bring up the Shot Submission Dialogue.

![Alt text](c1_tools/submitShot_simple.png?raw=true "Submit Shot")

This dialogue will detect if there are any conflicts in versions(as seen above), and auto-version to the next available number before saving to the server.

There are also a number of other validations that take place when opening this dialogue that you should never encounter if you always use the *Shot Browser*, and *C1 VersionUp* tools.

#### Don't rename your local files or folders in the working directory, or you will encounter validation errors.

<hr>

## Render OU.mp4 (Ffmpeg)

This tool scans the given directory for frame-sequences with **LEFT**, **RIGHT**, or **MONO** suffixes and creates a *Squished Over-Under*(see below) h264 mp4 movie for previewing in headsets.


Naming Convention for frames:
```
<Show Code>_<Shot Name>_v<3-Digit Version-Number>_<LEFT, RIGHT, or MONO>.<4-Digit Frame-Number>.<ext>
```

Example:
```
BRZ_D1S4_v003_LEFT.0001.png, BRZ_D1S4_v003_RIGHT.0001.png
```
or,
```
BRZ_D1S4_v003_MONO.0001.png
```

![Alt text](c1_tools/renderOU.png?raw=true "Render OU.mp4 (Ffmpeg)")

#### Select the directory containing the frames,
And an Ffmpeg *.bat* file will be created in the folder with your Nuke script and begin running. When complete, you'll have an mp4 located next to your Nuke script ready for viewing in a headset. At any time you can double-click the *.bat* file and re-render.

It will look something like this:

![Alt text](c1_tools/squished_ou.png?raw=true "Example of a Squished Over-Under video")

<hr>

## Scan for missing Frames

Must have a write node selected with valid path to the rendered frame output in the * file * knob.

Example:

![Alt text](c1_tools/file_knob.png?raw=true "File knob)

This location will be scanned for missing frames and frame-ranges.

If missing frames were detected, you'll get a dialogue with a list of them like this:

![Alt text](c1_tools/missing_frames.png?raw=true "Missing Frames")

Clicking * Yes * will automatically start a nuke render with those frames input for you.

<hr>
<hr>

## Authors

* **Jacob Martinez** - *Technical Artist* - [Magnetic-Lab](https://www.magnetic-lab.com/)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Condition One(http://conditionone.com/)
* https://www.ffmpeg.org/
