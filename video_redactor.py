import PIL

class Video_redactor:

    def __int__(self, name=str):
        self.name = name

    def open_video(self):
        with self.name as video:
            print(video)