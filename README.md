Been practising writing Python scripts to be added to OBS software.

Anything in a directory (e.g. FE7-stream) is specifically for my own stream [DNKabs](https://www.twitch.tv/dnkabs).
For scripts outside any directroy, I've tried to make them for generic use.
Feel free to use any of it, though I can't guarantee performance.

I've been using the following:
OBS 26.1.1
Windows 10 64-bit
Python 3.6.8

## Initial setup
OBS specifically requires Python 3.6.
Python 3.6.8 seems to be the latest version available for Windows, which you can get [here](https://www.python.org/downloads/release/python-368/) (download the executable installer relevant to your OS).
After installing Python, go to OBS and then `Tools > Scripts > Python Settings` and provide the Python install path. If you're unsure, open the `Python 3.6` app run the following:
```
>>> import os
>>> import sys
>>> os.path.dirname(sys.executable)
```

Once the install path has been added, go to the `Scripts` tab, add whatever script you'd like and enjoy!
