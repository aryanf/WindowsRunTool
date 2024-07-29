import subprocess

def update_dependencies():
    # Install library dependencies
    print('Updating package dependencies...')
    command = 'pip install -r requirements.txt'
    # Execute the command
    try:
        subprocess.check_call(command, shell=True)
        print("Package installed successfully!")
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)


if __name__ == '__main__':
    update_dependencies()