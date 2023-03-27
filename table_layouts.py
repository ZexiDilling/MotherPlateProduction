

compound_main = """ CREATE TABLE IF NOT EXISTS compound_main( 
            compound_id INTEGER PRIMARY KEY, 
            active TEXT NOT NULL
            ); """


motherplate_batch = """ CREATE TABLE IF NOT EXISTS mp_batch(
            mp_batch TEXT PRIMARY KEY,
            active INTEGER NOT NULL,
            date REAL NOT NULL
            ); """


motherplate_table = """ CREATE TABLE IF NOT EXISTS mp_plates(
            mp_barcode TEXT PRIMARY KEY,
            mp_batch TEXT NOT NULL,
            date REAL NOT NULL,
            FOREIGN KEY (mp_batch) REFERENCES mp_batch(mp_batch)
            ); """

compound_mp_table = """ CREATE TABLE IF NOT EXISTS compound_mp( 
            row_counter INTEGER PRIMARY KEY,
            mp_barcode TEXT NOT NULL,
            compound_id INTEGER NOT NULL,
            mp_well TEXT NOT NULL,
            volume REAL NOT NULL,
            date REAL NOT NULL,
            active INTEGER NOT NULL,
            FOREIGN KEY (mp_barcode) REFERENCES mp_plates(mp_barcode),
            FOREIGN KEY (compound_id) REFERENCES compound_main(compound_id)
            ); """