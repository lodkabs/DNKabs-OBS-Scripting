Been practising writing Python scripts to be added to OBS software.

Anything in a directory (e.g. FE_GBA-stream) is specifically for my own stream [DNKabs](https://www.twitch.tv/dnkabs).<br />
For scripts outside any directroy, I've tried to make them for generic use.<br />
Feel free to use any of it, though I can't guarantee performance.<br />
The Python scripting documentation can be found [here](https://obsproject.com/docs/scripting.html)

I've been using the following for the OBS python scripts:
- OBS 26.1.1
- Windows 10 64-bit
- Python 3.6.8

## Initial setup
OBS specifically requires Python 3.6.<br />
Python 3.6.8 seems to be the latest version available for Windows, which you can get [here](https://www.python.org/downloads/release/python-368/) (download the executable installer relevant to your OS).<br />
After installing Python, go to OBS and then `Tools > Scripts > Python Settings` and provide the Python install path. If you're unsure, open the `Python 3.6` app run the following:
```
>>> import os
>>> import sys
>>> os.path.dirname(sys.executable)
```

Once the install path has been added, go to the `Scripts` tab, add whatever script you'd like and enjoy!

---
### window_title.py
This script allows you to show the title of a selected window on stream.<br />
This was inspired by wanting to show YouTube music being played whilst streaming.<br />
Select a Text source to show the title, and the window title to show. There's also an option to remove initial bracketed numbers, for example, the `(n)` for notifications.

---
### text_wipe.py
This script will "type out" each line of a text source.<br />
The speed of the wipe and the length of the pause between each line can be controlled.

---
### scroll_with_pauses.py
*Currently in progress*<br />
OBS supports text scrolling, but doesn't support periodic pauses between lines.<br />
This would give the viewer some time to read each line before moving on to the next.

---
## KabsBot
I followed [this tutorial](https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8) to create a bot for the channel (with some help from [this video](https://www.youtube.com/watch?v=gYT51WoGBJc)).<br />
Not quite sure what it'll do yet...I'll keep you posted.
