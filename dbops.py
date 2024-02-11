import sqlite3
import pandas as pd

def df_to_sqlite():
    with sqlite3.connect ("patients.db") as conn:
        df = pd.read_csv("patientData.csv")
        df.to_sql('patients', conn, if_exists='replace', index = False)


def raw_to_sqlite(raw_text, target_id):
    with sqlite3.connect ("patients.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT EXT_RAW FROM patients WHERE "Patient ID" = ?''', (int(target_id),))
        cursor.execute('''UPDATE patients SET EXT_RAW = COALESCE(EXT_RAW, '') || ? WHERE "Patient ID" = ?''', (raw_text, int(target_id)))
        if cursor.rowcount == 0:
            print(f"No patient found with ID {target_id}. No update performed.")
        else:
            print(f"Patient with ID {target_id} was updated successfully.")
            conn.commit()
            print(cursor.execute('''SELECT EXT_RAW FROM patients WHERE "Patient ID" = ?''', (int(target_id),)).fetchone())


def get_raw_ext_data(target_id):
    with sqlite3.connect ("patients.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT EXT_RAW FROM patients WHERE "Patient ID" = ?''', (int(target_id),))
        return cursor.fetchone()
    
def get_all_history(target_id):
    with sqlite3.connect ("patients.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT "Family History", "Medical History", "EXT_SUM" FROM patients WHERE "Patient ID" = ?''', (int(target_id),))
        result = cursor.fetchone()  
        if result is not None:
            # Concatenate the 'Family History' and 'Medical History' into one string
            combined_string = f"{result[0]} {result[1]} {result[2]}"
        else:
            combined_string = "No data found for the specified patient ID."
        print(combined_string)
        return combined_string

def get_ext_sum(target_id):
    with sqlite3.connect ("patients.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT EXT_SUM FROM patients WHERE "Patient ID" = ?''', (int(target_id),))
        return cursor.fetchone()
def get_full_sum(target_id):
    with sqlite3.connect ("patients.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT FINAL_SUM FROM patients WHERE "Patient ID" = ?''', (int(target_id),))
        return cursor.fetchone()
    

def upload_ext_summary(summary, target_id):
    with sqlite3.connect ("patients.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE patients SET EXT_SUM = ? WHERE "Patient ID" = ?''', (summary, int(target_id)))
        conn.commit()
        print(cursor.execute('''SELECT EXT_SUM FROM patients WHERE "Patient ID" = ?''', (int(target_id),)).fetchone())

def upload_full_summary(summary, target_id):
    with sqlite3.connect ("patients.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE patients SET FINAL_SUM = ? WHERE "Patient ID" = ?''', (summary, int(target_id)))
        conn.commit()
        print(cursor.execute('''SELECT FINAL_SUM FROM patients WHERE "Patient ID" = ?''', (int(target_id),)).fetchone())




if __name__ == "__main__":
    df_to_sqlite()