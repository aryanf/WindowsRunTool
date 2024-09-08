# What is WindowsRunTool
I have been using run panel as an easy interface to run different simple or complex tasks for many years.
It became so handy that I thought that can be defined as separate tool.

This Windows project let you to use run panel to do 5 different things, and you can define your own custom actions:
1. Operation (run script)
2. Open URL (from browser history)
3. Fetch information (from user defined text file)
4. Manage and navigate windows desktops
5. Open file explorer

These are defined by key commands o, u, i, d and e by default. But it is pretty simple to customize them.

Like example below is running shot operation:

![Alt text](images/run_panel.png)

You can pass multiple string arguments and an int argument, and some predefined values like env argument. Those are passed to python function and easy to customize.

Example below to call `demo` script, and pass arguments.

![Alt text](images/demo_main.png)

![Alt text](images/demo_main_code.png)

You can also call specific function in the script

![Alt text](images/demo_func1.png)

![Alt text](images/demo_func1_code.png)

This way you can easily create your own scripts and run them quickly.

Let see example of any of these predefined actions in following section
# 1. Operation Command

![Alt text](images/operation_1.gif)


[more about operation command](docs/OPERATIONS.md)

# 2. Information Command

![Alt text](images/information_1.gif)

[more about information command](docs/INFORMATION.md)

# 3. Url Command

![Alt text](images/url_1.gif)

[more about url command](docs/URLS.md)

# 4. Virtual Desktop Command

![Alt text](images/desktop_1.gif)

# 5. File Explore Command

![Alt text](images/explorer_1.gif)


# Installation
`pip install -r requirements.txt` 

`python installer.py`


What it does:
1. This add current directory to path env variable (if not added earlier)
2. Create key bat files and their link files (if not created earlier)
3. Create directory for each key (if not created earlier)

So, you can manually do the job, if installer fails to complete the task.





# Documents
1. [operations [o ...]](docs/OPERATIONS.md)
2. [existing scripts](docs/EXISTING_SCRIPTS.md)
3. [info [i ...]](docs/INFORMATION.md)
4. [urls [l ...]](docs/URLS.md)
5. [user configuration](docs/USER_CONFIGURATION.md)
6. [add key commands or scripts](docs/HOW_TO_ADD)
2. [debug](docs/DEBUG.md) 

