import streamlit as st
from config import load_llm
import re
import time 
import pandas as pd 


def get_patient_data(data):    
    data_list = {
        "id": data['Patient ID'],
        "name": data['Name'],
        "age": data['Age'],
        "race": data['Race'],
        "phone": data['Contact'],
        "medical_history": data['Medical History'],
        "Current Appointment Details" : data["Current Appointment Details"],
        "Prescription" : data["Prescription"],
        "Other Notes" : data["Other Notes"]
    }

    return data_list