import sqlite3
import pandas as pd

df = pd.read_csv("patientData.csv")
df.to_sql('patients', sqlite3.connect('patients.db'), if_exists='replace', index = False)