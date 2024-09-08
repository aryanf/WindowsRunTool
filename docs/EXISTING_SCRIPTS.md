# Existing scripts examples

Operation commands can be easily added by adding a python script to run a useful tool or process.

There are some existing example to use them right away:

Use `WinKey + r` to open run panel, and then type

- `o compare` => to open WinMerge to compare multiple files.
- `o csv` => to open csv editor. It reads last existing csv file in Download dir by default.
- `o find` => to open Everything tool and search for files
- `o hex` => to open frhed binary and text editor
- `o gif` => to record to gif
- `o note` => to open notepad++
- `o shot` => to screenshot 
- `o record` => to video record your screen (make sure all huge files are cloned in `portable_oepn_source_app/Captura`, some huge files like ffmpeg.exe, ffplay.exe or ffprobe might be missed)
- `o timer` => run a time (run help to see how to pass parameters)
- `o wait` => run a script to prevent your device to sleep
- `o cut` => run a ShareX pin-to-screen to cut an area in your screen and keep it on top
- `o pen` => run ZoomIt tool to enable a pen to draw on screen. Ideal for demo and presentation.


There might be some switches for these commands like `o shot edit`, you can read help documentation for each command by running `o -help`

It is good practice to provide meaningful comments for your functions. You can then use help command to read them easily. 

Commenting the function to see it description while using help flag:

![Alt text](/images/operation_3.gif)

I suggest using additional tools like Ditto to handle clipboard properly and SlickRun to keep history of run commands. (Windows by default keep last 26 commands)