import PySimpleGUI as sg
from pathlib import Path
import threading
import time

from gui_layout import main_layout, popup_duplicate_table
from gui_functions import motherplate_import_controller, error_handler, compare_data, listening_table_controller, \
    scan_for_mp_files
from helper_func import config_writer
from listening_handler import listening_controller


def main(config):
    """
    The main GUI setup and control for the whole program
    The while loop, is listening for button presses (Events) and will call different functions depending on
    what have been pushed.
    :param config: The config handler, with all the default information in the config file.
    :type config: configparser.ConfigParser
    :return:
    """

    window = main_layout()
    try:
        mp_folder = Path(config["Folder"]["mp"])
    except KeyError:
        mp_folder = sg.PopupGetFolder("Please select a folder MP raw data")
        config_dict = {"mp": mp_folder}
        config_writer(config, "Folder", config_dict)
    missing_files, missing_files_names = scan_for_mp_files(config, mp_folder)

    if type(missing_files) == list and missing_files:
        check = sg.PopupYesNo(f"Following files are not in the Database for MP's: {missing_files_names} "
                              f"Would you like to add them? - WARNING This takes around 1 min per file")
        if check == "Yes":
            motherplate_import_controller(config, missing_files)

    while True:

        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "-CLOSE-":
            break

        if event == "Import MPs":
            import_data = sg.PopupGetFile("Please select a File with produced MotherPlate's")
            try:
                import_data = Path(import_data)
            except TypeError:
                pass
            else:
                test_string = motherplate_import_controller(config, import_data)

            if "error" in test_string:
                error_handler(config, sg, test_string)

        if event == "-COMPARE-":
            raw_data = sg.PopupGetFile("Please select a file")
            if not raw_data:
                continue
            else:
                raw_data = Path(raw_data)
                test_string = compare_data(config, raw_data)
            if type(test_string) == str:
                sg.Popup(test_string)
            elif type(test_string) == dict:
                check = sg.PopupYesNo(f"There are {test_string['dup_count']} duplicates out of "
                                      f"{test_string['tube_count']}-Tubes."
                                      f"Do you wish to see a list and there placements?")
                if check == "Yes":
                    popup_duplicate_table(test_string["dup_table_data"], test_string["headlines"])
            else:
                error_handler(config, sg, test_string)

        if event == "-LISTEN-":
            Path("duplicat_compounds.txt").write_text()
            window["-KILL-"].update(value=False)
            window["-DUP_TUBE_COUNTER-"].update(value=0)
            window["-RACK_COUNTER-"].update(value=0)

            if not Path(config["Folder"]["in"]):
                folder_in = sg.PopupGetFolder("Please select the folder you would like to listen to")
                config_heading = "Folder"
                sub_heading = "in"
                data_dict = {sub_heading: folder_in}
                config_writer(config, config_heading, data_dict)

            if not Path(config["Folder"]["out"]):
                folder_out = sg.PopupGetFolder("Please select the folder where your reports ends up")
                config_heading = "Folder"
                sub_heading = "out"
                data_dict = {sub_heading: folder_out}
                config_writer(config, config_heading, data_dict)

            threading.Thread(target=listening_controller, args=(config, True, window,), daemon=True).start()
            threading.Thread(target=progressbar, args=(config, True, window,), daemon=True).start()

        if event == "-ANALYSE_LISTENING_DATA-":
            headlines, table_data = listening_table_controller()
            popup_duplicate_table(table_data, headlines)

        if event == "-KILL_BUTTON-":
            window["-KILL-"].update(value=True)

        # Extra section
        if event == "In":
            config_heading = "Folder"
            sub_heading = "in"
            new_folder = sg.PopupGetFolder(f"Current folder: {config[config_heading][sub_heading]}", "Data Folder")
            if new_folder:
                data_dict = {sub_heading: new_folder}
                config_writer(config, config_heading, data_dict)

        if event == "Out":
            config_heading = "Folder"
            sub_heading = "out"
            new_folder = sg.PopupGetFolder(f"Current folder: {config[config_heading][sub_heading]}", "Data Folder")
            if new_folder:
                data_dict = {sub_heading: new_folder}
                config_writer(config, config_heading, data_dict)

        if event == "MP":
            config_heading = "Folder"
            sub_heading = "mp"
            new_folder = sg.PopupGetFolder(f"Current folder: {config[config_heading][sub_heading]}", "Data Folder")
            if new_folder:
                data_dict = {sub_heading: new_folder}
                config_writer(config, config_heading, data_dict)

        if event == "Info":
            with open("README.txt") as file:
                info = file.read()

                sg.Popup(info)

        if event == "About":
            sg.Popup("This is a program for comparing files from a 2D barcode scanner (traxer) with MotherPlates "
                     "files produced by PlateButler - Programmed by Charlie, for DTU SCore")


def progressbar(config, run, window):
    """
    The progress bar, that shows the program working
    :param run: If the bar needs to be running or not
    :type run: bool
    :param window: Where the bar is displayed
    :type window: PySimpleGUI.PySimpleGUI.Window
    :return:
    """
    min_timer = 0
    max_timer = 100
    counter = 0

    while run:
        if counter == min_timer:
            runner = "pos"
        elif counter == max_timer:
            runner = "neg"

        if runner == "pos":
            counter += 10
        elif runner == "neg":
            counter -= 10

        window["-BAR-"].update(counter)

        time.sleep(0.1)
        if window["-KILL-"].get():
            run = False




if __name__ == "__main__":
    import configparser
    config = configparser.ConfigParser()
    config.read("config.ini")
    main(config)
