from terminal import *
from video_redactor import *


if __name__ == '__main__':
    bash = Cursor()
    while bash.command != "":
        if bash.command.startswith('cd'):
            if bash.command == 'cd':
                bash.basic_location()
            else:
                bash.move()
        elif bash.command.startswith('-d'):
            bash.hard_driver_list()
        elif bash.command.startswith('/d'):
            bash.hard_driver_move()
        elif bash.command.startswith('/v'):
            pass
        else:
            bash.bash_commands()
        bash.command = input(bash)
