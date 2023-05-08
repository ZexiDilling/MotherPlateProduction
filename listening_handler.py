import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import date, datetime, timedelta
import time
from pathlib import Path

from gui_functions import compare_data
from gui_layout import popup_duplicate_table


class MyEventHandler(FileSystemEventHandler):
    def __str__(self):
        """This is a standard class for watchdog.
        This is the class that is listening for files being created, moved or deleted.
        ATM the system only react to newly created files"""

    def __init__(self, window):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.window = window
        self.table_data = []
        self.table_headings = ["Position", "Tube ID", "test_1", "Status", "test_2", "Error Count", "Rack ID", "Date"]

    def on_created(self, event):
        """
        This event is triggered when a new file appears in the target folder
        It checks the file in the event for missing transferees, if there are any, it sends an E-mail.
        :param event: The full event, including the path to the file that have been created
        """
        rack_counter = int(self.window["-RACK_COUNTER-"].get())
        dup_counter = int(self.window["-DUP_TUBE_COUNTER-"].get())
        file = Path(event.src_path)
        # plate list:

        # checks if path is a file
        if file.is_file():      # ToDo add gaurd for other types of file, and other text files... Nice to have, not need to have
            # Sleeps to make sure that the file is done being created
            time.sleep(0.2)

            # Updates the amount of racks that have been scanned
            self.window["-RACK_COUNTER-"].update(value=rack_counter + 1)

            # Check if there are any duplicates in the scanned rack
            test_string = compare_data(self.config, file)
            print(test_string)

            # Write all the data into a doc, that can be used to create a table
            temp_doc = Path("duplicat_compounds.txt")
            if type(test_string) == dict:
                self.window["-DUP_TUBE_COUNTER-"].update(value=dup_counter + 1)
                with temp_doc.open("a") as file:
                    # write headlines into doc:
                    for headlines in test_string["headlines"]:
                        file.write(f"{headlines},")

                    # Writes a splitter
                    file.write(":")

                    # Write data
                    for data_list in test_string["dup_table_data"]:
                        for data in data_list:
                            file.write(f"{data},")
                        file.write(";")

                    file.write("\n")




        # if it is not a file, it is assumed it is a folder
        else:
            print(event.src_path)
            print(f"{datetime.now()} - folder is created")


    # def on_deleted(self, event):
    #     """
    #     This event is triggered when a file is removed from the folder, either by deletion or moved.
    #     :param event:
    #     :return:
    #     """
    #     print("delet")
    #     print(event)

    # def on_modified(self, event):
    #     """
    #     This event is triggered when a file is modified.
    #     :param event:
    #     :return:
    #     """
    #     print("mod")
    #     print(event)



def listening_controller(config, run, window):
    """
    main controller for listening for files.
    :param config: The config handler, with all the default information in the config file.
    :type config: configparser.ConfigParser
    :param run: A state to tell if the listening is active or not
    :type run: bool
    :param window: The window where the activation of the listening is.
    :type window: PySimpleGUI.PySimpleGUI.Window
    :return:
    """

    path = config["Folder"]["in"]

    event_handler = MyEventHandler(window)

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while run:
            time.sleep(1)
            if window["-KILL-"].get():
                run = False

    finally:
        observer.stop()
        observer.join()
        print(f"{datetime.now()} - done")