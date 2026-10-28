import zipfile            # built-in module for opening .zip files
import sqlite3            # built-in module for SQLite databases (nothing to download)
from pathlib import Path  # built-in module for handling file paths cleanly

import pandas as pd       # reads CSV files into tables (installed with pip)

ZIP_PATH = Path("data/SCDB_2026_01_caseCentered_Citation.csv.zip")
EXTRACT_DIR = Path("data/raw")                  # folder where the unzipped CSV will go
DB_PATH = Path("data/scdb.sqlite")              # the SQLite database file this script creates
TABLE_NAME = "cases"                            # name of the table inside the database

EXTRACT_DIR.mkdir(parents=True, exist_ok=True)  # create the folder if it doesn't exist yet

with zipfile.ZipFile(ZIP_PATH) as z:            # open the zip file
    z.extractall(EXTRACT_DIR)                   # unzip everything into the raw folder

csv_files = list(EXTRACT_DIR.glob("*.csv"))     # find every CSV file that came out of the zip
print("Found CSV files:", csv_files)

csv_path = csv_files[0]                         # use the first CSV (change the index if there are several)

df = pd.read_csv(csv_path, encoding="latin-1", low_memory=False)
# read the CSV into a table in memory
# encoding="latin-1": SCDB files are not UTF-8, and the default would raise an error
# low_memory=False: read whole columns at once so types are guessed consistently

print("Rows:", len(df), "Columns:", len(df.columns))  # sanity check on the size

conn = sqlite3.connect(DB_PATH)                 # open (or create) the SQLite database file

df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
# write the table into SQLite
# if_exists="replace": rerunning the script rebuilds the table instead of failing
# index=False: don't add an extra column for pandas' row numbers

conn.commit()                                   # save the changes to disk

count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
# run a SQL query that counts the rows, then take the first value of the first result row
print("Rows in database:", count)               # should match the Rows number printed above

conn.close()                                    # close the connection so the file is released