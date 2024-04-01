## How to debug
Use your IDE (vscode is a good choice), and run integrated terminal from root directory of project, where link files exist.
If running vscode, a configuration like below can help to debug a target command

    "configurations": [
        {
            "name": "i",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/python/run.py",
            "console": "integratedTerminal",
            "args": "o note my_fav_food"
        }
    ]

Instead of running command in run panel, try to run it in a terminal at root of this project.