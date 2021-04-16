import io
import json
import logging
import os
import re
import requests
import ntpath
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# Append parent directory to PYTHON_PATH so we can import utils.py
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from setup import setup, teardown, file_mask_context_name, file_search_context_name
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget, FileTarget, NullTarget

context = json.dumps({
            "fileSearchContextName": file_search_context_name,
            "fileMaskContextName": file_mask_context_name
        })
url = 'http://localhost:8080/api/darkshield/files/fileSearchContext.mask'
s=requests.Session()

def mask(filename):
     basename=ntpath.basename(filename)
     process_files = [(filename, 'masked')]
     for file_name, masked_folder in process_files:
        files = {'file': open(file_name, 'rb'), 'context': context}
        os.makedirs(masked_folder, exist_ok=True)
        logging.info(f"POST: sending '{file_name}' to {url}")
        with s.post(url, files=files, stream=True) as r:
            if r.status_code >= 300:
                raise Exception(f"Failed with status {r.status_code}:\n\n{r.json()}")
            logging.info(f"Extracting 'masked_{basename}' and 'masked_{basename}_results.json' into {masked_folder}.")
            parser = StreamingFormDataParser(headers=r.headers)
            parser.register('file', FileTarget(f'{masked_folder}/masked_{basename}'))
            parser.register('results', FileTarget(f'{masked_folder}/masked_{basename}_results.json'))
            for chunk in r.iter_content(4096):
                parser.data_received(chunk)
class OnMyWatch:
    # Set the directory on watch
    watchDirectory = os.getenv('USERPROFILE')+"\\Downloads"
  
    def __init__(self):
        self.observer = Observer()
  
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")
  
        self.observer.join()
  
class Handler(FileSystemEventHandler):
  
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            print("directory, no action taken.")
            return None
        elif event.event_type == 'created' or event.event_type == 'modified':
            # Event is created, you can process it now
            print("Watchdog received {} event - {}.".format(event.event_type,event.src_path))
            time.sleep(1)
            mask(event.src_path)
  

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    try:
        setup(s)
        watch = OnMyWatch()
        watch.run()
    finally:
        teardown(s)
