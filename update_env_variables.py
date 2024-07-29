import os
from python.env_var_utils import prepend_env

def update_env_variable():
    print('Updating environment variable...')
    current_dir = os.getcwd()
    # This is going to add current directory to path env var
    # If you face a problem here, comment this code and add it manually
    prepend_env('Path', [
        current_dir
        ])
    print('Successfully added current directory to path env var.')


if __name__ == '__main__':
    update_env_variable()