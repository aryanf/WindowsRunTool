## What is WindowsRunTool
I have been using run panel as an easy interface to run different simple or complex tasks for many years.
It became so handy that I thought that can be defined as separate tool, and anyone can enjoy it.
This project aims to maximize run panel functionality in Windows, to ease running customized scripts from run panel.
Follow super simple installation steps to setup the project.
Check /python/p directory which has couple of scripts, a good example is demo.py file.
It has main(), func1() and func2()
Those functions are triggered using run panel like:

p demo => demo.main()

p demo func1 => demo.func1()

p demo func2 => demo.func2()

you can also pass some parameters to these functions like 
a number
2 or 3 strings (3 strings to main() and 2 strings to func1 or func2)
predefined values like:
an env fix value from [dev, staging, prod], help and debug
play around and run demo functions with parameters to see how they are passed to functions as properties of MainCommandMessage and SubCommandMessage

Check structure of these object in python/message.py
There are some other scripts that I found useful example to increase productivity.
Open run panel (WinKey+r) and type 'p help' to check all existing script
Check each functionality by specifying the key command like 'p help demo' or 'p help record'

## Existing scripts

## Installation
pip install -r requirements.txt 

python installer.py
What is does:
1. This add current directory to path env variable (if not added earlier)
2. Create key bat files and their link files (if not created earlier)
3. Create directory for each key (if not created earlier)

So, you can manually do the job, if installer fails to complete the task.

## Add extra key commands
Modify Installer if you want additional key command, by default it only provide ['p', 'i', 'l']
python installer.py


## Add your script
demo.py file is an example script. Add new script file and with couple of functions in p directory.

