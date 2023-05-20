import concurrent.futures


def run_command(command):
    command[0].slice_video(command[1])


class FFMpegThreads:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def add_message(self, message):
        future = self.executor.submit(run_command, message)
        self.futures.append(future)

    def wait_for_complete(self):
        for future in concurrent.futures.as_completed(self.futures):
            print(f'Future {future} finished.')
        print('All commands finished.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)
