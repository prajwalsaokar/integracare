import sqlite3
import pandas as pd

def to_sqlite():
    with sqlite3.connect ("patients.db") as conn:
        df = pd.read_csv("patientData.csv")
        df.to_sql('patients', conn, if_exists='replace', index = False)

def pdf_to_sqlite(pdf_text):
    with sqlite3.connect ("patients.db") as conn:




if __name__ == "__main__":
    to_sqlite()