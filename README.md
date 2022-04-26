# scriptmatch
`scriptmatch` is designed to help pair funscripts with their corresponding videos, even if they are not quite named the same.

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
