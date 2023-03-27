from os import listdir, scandir
from pathlib import Path
from database_handler import DataBaseFunctions


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
    all_files = list(Path(path).glob("**/*.txt"))

    if not all_files:
        return "Error_0001"

    # Start up the database, and get amount of rows for the compound_mp table.
    dbf = DataBaseFunctions(config)
    table_compound_mp = config["Tables"]["compound_mp_table"]
    row_counter = dbf.number_of_rows(table_compound_mp)

    for files in list(all_files):
        all_table_data, row_counter = _grab_data(files, row_counter)
        for table_data in all_table_data:
            for data in table_data:
                try:
                    temp_table = data["table"]
                except KeyError:
                    dbf.add_records_controller(temp_table, data)


def compare_data(config, path):

    dbf = DataBaseFunctions(config)

    duplicat_tubes = []

    with path.open() as f:
        lines = f.readlines()
        for line in lines:
            compound_id = line.split(";")[1]
            print(compound_id)
            table = "compound_main"
            headline = "compound_id"
            test_string = f"SELECT rowid, * FROM '{table}' WHERE {headline} = '{compound_id}'"
            record = dbf._fetch(test_string)
            if record:
                duplicat_tubes.append(record[0][0])
        if duplicat_tubes:
            return duplicat_tubes
        else:
            return "No duplicates"


def error_handler(config, sg, error):
    error_msg = config["Error_handler"][error]
    sg.PopupError(f"program stopped du to {error} - {error_msg}")


if __name__ == "__main__":
    folder = Path(r"C:\Users\phch\Desktop\more_data_files\MP Production\NOT ADDED")
    import configparser
    config = configparser.ConfigParser()
    config.read("config.ini")
    path = Path(r"C:\Users\phch\Desktop\more_data_files\TubeRackBarcodes\3000127785.txt")
    print(compare_data(config, path))