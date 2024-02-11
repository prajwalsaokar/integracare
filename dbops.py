import sqlite3
import pandas as pd
def to_sqlite():
    df = pd.read_csv("patientData.csv")
    df.to_sql('patients', sqlite3.connect('patients.db'), if_exists='replace', index = False)

if __name__ == "__main__":
    to_sqlite()