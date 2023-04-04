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
        ["&Settings", ["Change Folder", ["In", "Out", "MP"]]],
        ["&Info", ["Info", "About"]],
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
            [sg.T("Duplicates:", size=8),
             sg.Input(0, key="-DUP_TUBE_COUNTER-", size=3, tooltip="Counts how many duplicated tubes there are, "
                                                                   "while listening is active"),
             sg.T("Racks:", size=5),
             sg.Input(0, key="-RACK_COUNTER-", size=3, tooltip="Counts how many racks have been scanned,"
                                                               "while listening is active"),
             sg.Button("Analyse", key="-ANALYSE_LISTENING_DATA-",
                       tooltip="Will show a table of all the data that have been gather while listening was active")],
            [sg.Button("Listen", key="-LISTEN-", expand_x=True,
                       tooltip="Start listening to folders for new files. "
                               "All previous data collected by listening will be deleted"),
             sg.Button("Kill", key="-KILL_BUTTON-", expand_x=True,
                       tooltip="stops the program that listen to the folder for files")],
            [sg.Button("Compare", key="-COMPARE-", expand_x=True,
                       tooltip="Compares a file from the 2D scanner with previous "
                               "MotherPlates to see if there are any duplicated"),
             sg.Button("Close", key="-CLOSE-", expand_x=True,
                       tooltip="Closes the whole program")],


        ]),
    ]]),

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


def _gui_popup_duplicate_table(data, headings):

    col = sg.Frame("Table", [[
        sg.Column([
            [sg.Table(headings=headings, values=data, key="-TABLE-")],
            [sg.Button("close", key="-TABLE_CLOSE-")]
        ])
    ]])

    layout = [[col]]

    return sg.Window("Table", layout, finalize=True, resizable=True)


def popup_duplicate_table(data, headlines):
    """
    A popup menu
    :param data: The data that needs to be displayed
    :type data: list
    :param config: The config handler, with all the default information in the config file.
    :type config: configparser.ConfigParser
    :param headlines: The headings of the table where the data is displayed
    :type headlines: list
    :return:
    """
    print(headlines)
    window = _gui_popup_duplicate_table(data, headlines)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "-TABLE_CLOSE-":
            window.close()
            break


