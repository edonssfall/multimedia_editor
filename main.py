import subprocess
from terminal import *
import readline


def complete(text, state):
    # Get the current line buffer
    line_buffer = readline.get_line_buffer()

    # Split the line buffer by spaces and get the last word
    last_word = line_buffer.split()[-1]

    # Use the "compgen" command to get a list of possible completions
    compgen_command = f"compgen -W '{text}' -- '{last_word}'"
    completions = subprocess.check_output(compgen_command, shell=True).decode().splitlines()

    # Return the next possible completion or None if there are no more completions
    return completions[state] if state < len(completions) else None


if __name__ == '__main__':
    key_tab = 'tab'
    # Make terminal cursor
    bash = Cursor()
    # To exit program just send empty command
    while bash.command != "":
        # Move commands
        if bash.command.startswith('cd'):
            # Move to home directory send just "cd"
            if bash.command == 'cd':
                bash.basic_location()
            # Move to folder
            else:
                bash.move()
        # Show list of connected devices
        elif bash.command.startswith('-d'):
            bash.hard_driver_list()
        # Move to connected device
        elif bash.command.startswith('/d'):
            bash.hard_driver_move()
        # Show data of first video
        elif bash.command.startswith('-v'):
            bash.video_commands()
        # Show data of images
        elif bash.command.startswith('-i'):
            pass
        # Other bash commands supported by Python_3.10
        else:
            bash.bash_commands()
        # Input command
        readline.set_completer(complete)
        # Set the autocompletion function for readline
        bash.command = input(bash)

