import PySimpleGUI as sg
from pathlib import Path

from gui_layout import main_layout
from gui_functions import motherplate_import_controller, error_handler, compare_data

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

    while True:

        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "-CLOSE-":
            break

        if event == "-IMPORT-" or event == "Import Folder":
            if event == "-IMPORT-":
                import_data = Path(sg.PopupGetFile("Please select a File with produced MotherPlate's"))
            else:
                import_data = Path(sg.PopupGetFolder("Please select a Folder with produced MotherPlate's"))

            test_string = motherplate_import_controller(config, import_data)

            if "error" in test_string:
                error_handler(config, sg, test_string)

        if event == "-COMPARE-":
            raw_data = Path(sg.PopupGetFile("Please select a file"))
            test_string = compare_data(config, raw_data)

            if type(test_string) == str:
                sg.Popup(test_string)
            elif type(test_string) == list:
                sg.Popup(test_string)
            else:
                error_handler(config, sg, test_string)

        if event == "-LISTEN-":
            pass

        # Extra section
        if event == "Info":
            with open("README.txt") as file:
                info = file.read()

                sg.Popup(info)

        if event == "About":
            sg.Popup("This is a program for comparing files from a 2D barcode scanner (traxer) with MotherPlates "
                     "files produced by PlateButler - Programmed by Charlie, for DTU SCore")




if __name__ == "__main__":
    import configparser
    config = configparser.ConfigParser()
    config.read("config.ini")
    main(config)
