import sqlite3


class DataBaseFunctions:
    def __init__(self, config):
        self.conn = None
        self.cursor = None
        self.database = config["Database"]["database"]

    def __str__(self):
        """Control all database function, as sqlite3 is terrible for writing to and from"""

    def create_connection(self):
        """
        Create a connection to the database

        :return: A connection to the database
        :
        """
        self.conn = sqlite3.connect(self.database)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.conn.cursor()
        return self.conn

    def submit_update(self, data):
        """
        Connect to the database, Updates the database and closes the connection

        :param data: Data that needs  to be updated
        :type data: str
        :return: commits updates to the database
        """
        self.create_connection()
        try:
            self.cursor.execute(data)
        except sqlite3.IntegrityError:
            pass
        # self.cursor.execute(data)


        self.conn.commit()
        self.cursor.close()

    @staticmethod
    def _list_columns(data):
        """
        Genera a list of headlines/keys from a dict.

        :param data: A dict over the data
        :type data: dict
        :return: a list of headlines/keys from dict
        :rtype: list
        """
        return [clm for clm in data]

    @staticmethod
    def _add_place_holders(columns):
        """
        make a string of "?" depending on how many columns/headlines/keys a dict have.

        :param columns: list of columns/headlines/keys
        :type columns: list
        :return: A string of "?" for SQlite3 to use for adding values
        :rtype: str
        """
        return ",".join("?" for _ in columns)

    @staticmethod
    def _add_layout(table_name, place_holders):
        """
        Makes a string that SQlite3 can use to add data

        :param table_name: name of table
        :type table_name: str
        :param place_holders: String of "?" one "?" per headline the table has
        :type place_holders: str
        :return: A string for SQlite to use.
        :type: str
        """
        return f"INSERT INTO {table_name} VALUES({place_holders})"

    @staticmethod
    def _data_layout(data, column_names):
        """
        Formatting a list for SQlite3 to add to the database

        :param data: The data that needs to be added
        :type data: dict
        :param column_names: List of column names
        :type column_names: list
        :return: List of data and values.
        :rtype: list
        """
        return [data[name] for name in column_names]

    def _add_data_to_table(self, layout, data):
        """
        Function that adds data to the database

        :param layout: String with table name, and "?" for each value that needs to be added
        :type layout: str
        :param data: List of values that needs to be added
        :type data: list
        :return: Data added to a table
        """
        try:
            self.cursor.execute(layout, data)
        except sqlite3.IntegrityError:
            pass
            #print("ERROR") # NEEDS TO WRITE REPORT OVER ERRORS TO SEE WHY DATA WAS NOT ADDED!!!
            # EITHER DUE TO DUPLICATES OR MISSING REFERENCE(FOREIGN KEY)
        # self.cursor.execute(layout, data)
        self.conn.commit()
        self.cursor.close()

    def add_records_controller(self, table_name, data):
        """
        Adds data to the database

        :param table_name: Name of the table where the data needs to be added
        :type table_name: str
        :param data: The data, in dicts form, that needs to be added to the database
        :type data: dict
        :return: Data added to the database
        """
        self.create_connection()
        list_columns = self._list_columns(data)
        place_holder = self._add_place_holders(list_columns)
        layout = self._add_layout(table_name, place_holder)
        data_layout = self._data_layout(data, list_columns)
        self._add_data_to_table(layout, data_layout)

    def _fetch(self, data):
        """
        Create a connection to the database, execute the search and gets data out of  the database

        :param data: The data the user is looking for
        :type data: str
        :return: all records that fits the data
        :rtype: dict
        """
        self.create_connection()
        self.cursor.execute(data)
        records = self.cursor.fetchall()
        self.cursor.close()
        return records

    def find_data(self, table, barcode, id_number, barcode_name, id_name):
        """
        Finds data in the database

        :param table: What table the data should be in
        :type table: str
        :param barcode: Barcode of the plate
        :type barcode: str
        :param id_number: Compound ID
        :type id_number: int
        :param barcode_name: Headline of the plate-column in the table
        :type barcode_name: str
        :param id_name: Headline for the compound id in the table
        :type id_name: str
        :return: Data from the database
        :rtype: dict
        """
        find = f"SELECT rowid, * FROM '{table}' WHERE {barcode_name} = '{barcode}' AND {id_name} = '{id_number}'"
        return self._fetch(find)

    def number_of_rows(self, table):
        """
        Counts rows in database.
        Missing to check for active samples

        :param table: Table name
        :type table: str
        :return: number of rows in table.
        :rtype: int
        """
        number = f"SELECT COUNT(*) from {table}"
        self.create_connection()
        self.cursor.execute(number)
        return self.cursor.fetchone()[0]

