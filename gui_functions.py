from os import listdir, scandir
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from database_handler import DataBaseFunctions
from datetime import datetime

def _grab_data(file, row):
    compound_table_data = [{"table": "compound_main"}]
    motherplate_table_data = [{"table": "mp_plates"}]
    motherplate_batch_data = [{"table": "mp_batch"}]
    compound_mp_table = [{"table": "compound_mp"}]

    all_motherplates = []
    all_motherplate_batch = []
    all_compounds = []
    duplicated_compounds = []

    temp_date = file.name.split("_")[0]

    with file.open() as f:
        lines = f.readlines()

        for line_index, line in enumerate(lines):
            temp_row = row + line_index
            data = line.split(";")
            temp_mp = data[0].strip()
            temp_well = data[1].strip()
            temp_compound = data[2].strip()
            temp_volume = data[3].strip()

            # sort out motherplate data:
            if temp_mp not in all_motherplates:
                temp_mp_batch = temp_mp.split("-")[0]
                all_motherplates.append(temp_mp)
                temp_motherplate_table_data = {
                    "mp_barcode": temp_mp,
                    "raw_data": file.name,
                    "mp_batch": temp_mp_batch,
                    "date": temp_date}
                motherplate_table_data.append(temp_motherplate_table_data)

                if temp_mp_batch not in all_motherplate_batch:
                    all_motherplate_batch.append(temp_mp_batch)
                    temp_motherplate_batch_data = {
                        "mp_batch": temp_mp_batch,
                        "active": 1,
                        "date": temp_date}
                    motherplate_batch_data.append(temp_motherplate_batch_data)

            # sort out compound data:
            if temp_compound not in all_compounds:
                all_compounds.append(temp_compound)
                temp_compound_table_data = {
                    "compound_id": temp_compound,
                    "active": 1}
                temp_compound_mp_table = {
                    "row_counter": temp_row,
                    "mp_barcode": temp_mp,
                    "compound_id": temp_compound,
                    "mp_well": temp_well,
                    "volume": temp_volume,
                    "date": temp_date,
                    "active": 1}
                compound_table_data.append(temp_compound_table_data)
                compound_mp_table.append(temp_compound_mp_table)
            else:
                duplicated_compounds.append(temp_compound)


    all_table_data = [compound_table_data, motherplate_batch_data, motherplate_table_data, compound_mp_table]
    return all_table_data, temp_row


def motherplate_import_controller(config, path):

    # Gets all files in folder and sub folder that ends with .txt
    if type(path) != list:
        all_files = list(Path(path).glob("**/*.txt"))
    else:
        all_files = path

    if not all_files:
        return "Error_0001"

    # Start up the database, and get amount of rows for the compound_mp table.
    dbf = DataBaseFunctions(config)
    table_compound_mp = config["Tables"]["compound_mp_table"]
    row_counter = dbf.number_of_rows(table_compound_mp)
    start_time = datetime.now()
    print(all_files)
    for file_index, files in enumerate(all_files):
        print(file_index)
        temp_start_time = datetime.now()
        all_table_data, row_counter = _grab_data(files, row_counter)
        for table_data in all_table_data:
            for data in table_data:
                try:
                    temp_table = data["table"]
                except KeyError:
                    dbf.add_records_controller(temp_table, data)
        temp_end_time = datetime.now()
        time_taken = temp_end_time - temp_start_time
        print(f"for file {file_index} took: {time_taken}")
    total_time = temp_end_time - start_time
    print(f"for all plates: {total_time}")
    per_plate_time = total_time / file_index
    print(f"Time per plate: {per_plate_time}")



def compare_data(config, path):

    dbf = DataBaseFunctions(config)

    duplicat_tubes = []
    duplicat_tubes_headlines = []
    duplicat_counter = 0
    tube_counter = 0
    with path.open() as f:
        lines = f.readlines()
        for line_index, line in enumerate(lines):

            line_data = line.split(";")
            if len(line_data) == 1:
                line_data = line.split(",")
            if line_index == 0:
                for date in line_data:
                    duplicat_tubes_headlines.append(date.strip())
            else:
                compound_id = line_data[1]
                table = "compound_main"
                headline = "compound_id"
                test_string = f"SELECT rowid, * FROM '{table}' WHERE {headline} = '{compound_id}'"
                record = dbf._fetch(test_string)
                tube_counter += 1
                if record:
                    temp_data = []
                    for data in line_data:
                        temp_data.append(data.strip())
                    duplicat_counter += 1

                    duplicat_tubes.append(temp_data)
        if duplicat_tubes:
            duplicat_dict = {"dup_table_data": duplicat_tubes, "headlines": duplicat_tubes_headlines,
                             "dup_count": duplicat_counter, "tube_count": tube_counter}
            return duplicat_dict
        else:
            return "No duplicates"


def _sort_table_data(final_headlines, all_data):

    table_data = []

    for counter in all_data:
        if len(all_data[counter]["headlines"]) < len(final_headlines):
            missing_headlines_index = []
            current_headlines_index = []

            for headlines_index, headlines in enumerate(final_headlines):
                if headlines not in all_data[counter]["headlines"]:
                    missing_headlines_index.append(headlines_index)
                else:
                    current_headlines_index.append(headlines_index)

            for data in all_data[counter]["data"]:
                if data:
                    temp_headline = []
                    for headline_index in range(len(final_headlines)):

                        if headline_index in current_headlines_index:
                            temp_value = current_headlines_index.index(headline_index)
                            print(temp_value)
                            temp_data = data[temp_value]
                            temp_headline.append(temp_data)
                        else:
                            temp_headline.append("Missing data")
                    table_data.append(temp_headline)

        else:
            for data in all_data[counter]["data"]:
                table_data.append(data)

    return table_data


def _grab_data_from_txt(path):

    final_headlines = ""
    all_data = {}
    with path.open() as file:
        lines = file.readlines()

        for line_index, line in enumerate(lines):
            all_data[line_index] = {}

            line_data = line.split(":")
            temp_headlines = line_data[0].split(",")[:-1]
            temp_data_list = line_data[1].split(";")

            # check how long the headline is, and makes sure that the final headline is the longest
            if len(temp_headlines) > len(final_headlines):
                final_headlines = temp_headlines
            all_data[line_index]["headlines"] = temp_headlines
            # add data into one big list
            all_data[line_index]["data"] = []
            for data in temp_data_list:
                temp_data = data.split(",")[:-1]

                all_data[line_index]["data"].append(temp_data)

    return final_headlines, all_data


def listening_table_controller():
    path = Path("duplicat_compounds.txt")
    final_headlines, all_data = _grab_data_from_txt(path)
    table_data = _sort_table_data(final_headlines, all_data)
    return final_headlines, table_data


def scan_for_mp_files(config, mp_folder):

    missing_files = []
    missing_files_names = []
    all_files = list(Path(mp_folder).glob("**/*.txt"))
    if not all_files:
        return "Error_0001"

    dbf = DataBaseFunctions(config)
    table = "mp_plates"
    barcode_name = "raw_data"

    for file_name in all_files:
        barcode = file_name.name
        temp_data = dbf.find_data(table, barcode_name, barcode)
        if not temp_data:
            missing_files_names.append(barcode)
            missing_files.append(file_name)

    return missing_files, missing_files_names


def error_handler(config, sg, error):
    error_msg = config["Error_handler"][error]
    sg.PopupError(f"program stopped du to {error} - {error_msg}")



if __name__ == "__main__":
    # folder = Path(r"C:\Users\phch\Desktop\more_data_files\MP Production\NOT ADDED")
    # import configparser
    # config = configparser.ConfigParser()
    # config.read("config.ini")
    # path = Path(r"C:\Users\phch\Desktop\more_data_files\TubeRackBarcodes\3000127785.txt")
    # print(compare_data(config, path))
    listening_table_controller()