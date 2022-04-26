# scriptmatch
`scriptmatch` is designed to help pair funscripts with their corresponding videos, even if they are not quite named the same.

## Installation

1. Create a python virtual environment (not required, but highly recommended)
2. Clone the repo
3. Install the dependencies with `pip -r requirements.txt`

## General Usage
Provide one or more paths to files or folders containing source videos and scripts that you would like to pair, followed by a destination path to put the paired videos and scripts.

**Example**: You have a downloads folder at `D:\MyUnsortedVideosAndScripts\` that contains many unsorted files.  You woud like matches placed in `D:\Sorted\`.
```bash
python scriptmatch.py D:\MyUnsortedVideosAndScripts\ D:\Sorted\
```

**Example**: You have multiple locations that contain videos and scripts.  You would like matches placed in `D:\Sorted\`.
```bash
python scriptmatch.py D:\MySourceVideos1 D:\MySourceScripts1 D:\MoreVideosAndScripts D:\Sorted\
```

**Example**: You have a particular video file that you would like to match to any of your scripts.  If matched, you would liek them placed in `D:\Sorted\`
```bash
python scriptmatch.py D:\SomePlace\my_cool_video1.mp4 D:\MyScripts D:\Sorted\
```

## A Little More Detail
### File Types
Video files are expected to have one of the following filename extensions:
- `.mp4`
- `.mkv`
- `.wmv`

Scripts are expected to have one of the following filename extensions:
- `.funscript`

Additional filename extensions may be added via the script.

### Matched Pairs
Once a matching video and script pair have been identified, the video and script will both be *hardlinked* to the given destination folder.  The hardlinked script will be renamed to match the video's base filename (but using the `.funscript` filename extension).

**Example**: The following source files were identified as a match:

- `D:\MySourceVideos\cool_vid_01.mp4`
- `D:\MySourceVideos\scriptsIfound\cool-vid01-script.funscript`

These will be hardlinked to:

- `D:\Destination\cool_vid_01.mp4`
- `D:\Destination\cool_vid_01.funscript`

*Note:* Because hardlinking is used, the destination folder must exist on the same volume as the source files.

*Note:* Because hardlinking is used, the matched pairs will not occupy *additional* space on the volume.
