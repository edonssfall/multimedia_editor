from terminal import *
import readline


# Function to autofill
def completer(text, state):
    paths = os.listdir(os.getcwd())
    options = [path for path in paths if path.startswith(text)]
    try:
        return options[state]
    except IndexError:
        return None


if __name__ == '__main__':
    # Make terminal cursor
    bash = Cursor()
    # To exit program just send empty command
    while bash.command != "":
        # Help info
        if bash.command.startswith('-h'):
            print(
                "-vi    To get info from first video\n"
                "-vs    To start compare in this folder\n"
                "/d     Move to connected devices\n"
                "-d     Show list of connected devices\n"
                "-sql   Open SQL terminal\n"
            )
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
        elif bash.command.startswith('-sql'):
            bash.sql_commands()
        # Other bash commands supported by Python_3.10
        else:
            bash.bash_commands()

        # Autofill how in bash
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completer)

        bash.command = input(bash)

