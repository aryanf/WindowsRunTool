Operation commands can be easily added by adding a python script to run a useful tool or process.

There are some existing example to use them right away:
get `WinKey + r` to open run panel, and then type

- `o compare` => to open WinMerge to compare multiple files.
- `o csv` => to open csv editor. It reads last existing csv file in Download dir by default.
- `o find` => to open Everything tool and search for files
- `o hex` => to open frhed binary and text editor
- `o gif` => to run search record to gif
- `o note` => to open notepad++
- `o shot` => to screenshot 
- `o record` => to video record your screen (make sure all huge files are cloned in `portable_oepn_source_app/Captura`, some huge files like ffmpeg.exe, ffplay.exe or ffprobe might be missed)
- `o timer` => run a time (run help to see how to pass parameters)
- `o wait` => run a script to prevent your device to sleep



There might be some switches for these commands like `o shot edit`, you can read help documentation for each command by running `o -help`

It is good practice to provide meaningful comments for your functions. You can then use help command to read them easily. 

