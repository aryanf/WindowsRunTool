import urllib.request
import os

def update_portables():
    # Install library dependencies
    print('Updating portable apps files...')
    
    cwd = os.getcwd()
    try:
        #urllib.urlretrieve("https://github.com/aryanf/WindowsRunTool/blob/main/portable_open_source_apps/ShareX/ffmpeg.exe", cwd + "/portable_open_source_apps/ShareX/ffmpeg.exe")
        urllib.request.urlretrieve('https://github.com/aryanf/WindowsRunTool/blob/main/portable_open_source_apps/ShareX/ffmpeg.exe', cwd + '/ffmpeg.exe')  
    except Exception as e:
        print("An error occurred:", e)


if __name__ == '__main__':
    update_portables()