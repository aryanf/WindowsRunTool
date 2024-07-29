@echo off

echo Updating dependencies...
python update_dependencies.py

echo Updating env variables...
python update_env_variables.py

echo Updating key commands links...
python update_key_commands_links.py