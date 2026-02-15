1.2.9
 - Add CloudWatch Log Group, EC2, Load Balancer, Security Group, CloudFormation, and Secrets Manager support to browser title extension
 - Enhance Lambda function name extraction with path-style hash support
 - Add ECS and title element observation to prevent AWS console title override
 - Add AutoHotkey shortcuts: Alt+D for DoubleCmd, Alt+X for cut toggle, Alt+F for fix
 - Add browser-specific Alt+Down shortcuts (minimize on Chrome/Edge, pass-through on VS Code)
 - Replace win10toast with windows-toasts for modern Windows 11 notifications
 - Add Windows toast notifications for git branch, mouse position, and host file cleanup
 - Improve URL parsing with AWS service extraction and smart display (SQS, DynamoDB, S3, Lambda, ECS, etc.)
 - Add indexed output and duplicate removal for browser history URLs
 - Add page reload cache control parameter
 - Reduce debug output in window utility functions
 - Add O365, msgraph-core, msal, and Pillow dependencies

1.2.8
 - Update grep, zip, unzip and xml

1.2.7
 - Add grep function
 - Get top file explorer directory path and selected file, and pass to other apps

1.2.6
 - Update documentation
 
1.2.5
 - Support Opera
 - Code clean up and performance refactor

1.2.4
 - Let notepad++ to open a new instance
 - Add e key command to open explorer in predefined location using q-dir
 - Add d key command to manage virtual desktops

1.2.3
 - info.lnk can be used instead of info.diff. link object should refer to info.diff.

1.2.2
 - Fix for csv and json to open latest from Download dir.
 - Minor fix for web history command.
 - Installer look at directories under python and crate key env variable that can be called by run panel.

1.2.1
 - Update gitignore.
 - Add aws utils and command to get aws credential by mapping env to profile
 - Refactoring helper, message, run files and couple of commands

1.2.0
 - Info fetch is enabled by i key command.

1.1.0
 - Url reading from browser history database.

1.0.0
 - Basic run from python directory.