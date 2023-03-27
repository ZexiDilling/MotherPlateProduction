import PySimpleGUI as sg
import configparser


def _menu():
    """
    Top menu of the gui
    :return: The top menu
    :rtype: list
    """
    menu_top_def = [
        # ["&File", ["&Open    Ctrl-O", "&Save    Ctrl-S", "---", '&Properties', "&Exit", ]],
        ["&Help", ["Info", "About"]],
        ["&Extra", ["Import Folder", "Import MPs"]]
    ]
    layout = [[sg.Menu(menu_top_def)]]
    return layout


def _gui_main_layout():
    """
    The main layout for the gui
    :return: The main layout for the gui
    :rtype: list
    """

    main = sg.Frame("Listening", [[
        sg.Column([
            [sg.ProgressBar(100, key="-BAR-", size=(25, 5), expand_x=True),
             sg.Checkbox("KILL", visible=False, key="-KILL-")],
            # [sg.FolderBrowse("Import", key="-IMPORT-",
            #                  tooltip="Choose a folder with all completed MotherPlate files. Duplicates are ignored."),
            [sg.Button("Compare", key="-COMPARE-",
                           tooltip="Compares a file from the 2D scanner with previous "
                                   "MotherPlates to see if there are any duplicated"),
             sg.Button("Listen", key="-LISTEN-", expand_x=True, tooltip="Start listening to folders for new files"),
             sg.Button("Close", key="-CLOSE-", expand_x=True,
                       tooltip="Closes the whole program")],

        ]),
    ]])

    layout = [[main]]

    return layout


def main_layout():
    """
    The main setup for the layout for the gui
    :return: The setup and layout for the gui
    :rtype: sg.Window
    """

    # sg.theme()
    top_menu = _menu()

    layout = [[
        top_menu,
        _gui_main_layout()
    ]]

    return sg.Window("MotherPlate Production", layout, finalize=True, resizable=True)