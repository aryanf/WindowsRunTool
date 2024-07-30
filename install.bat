@echo off

echo:
echo Updating dependencies...
python update_dependencies.py

echo:
echo Updating env variables...
python update_env_variables.py

echo:
echo Updating key commands links...
python update_key_commands_links.py