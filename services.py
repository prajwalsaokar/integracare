import streamlit as st
from config import load_llm
import re
import time 
import pandas as pd 
from config import load_llm
from dbops import get_raw_ext_data, upload_ext_summary

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
        "Other Notes" : data["Other Notes"],
        "Family History" : data["Family History"],
    }

    return data_list

def summarize_ext_health(rowid):
    raw_ext = get_raw_ext_data(rowid)
    print(rowid)
    prompt = """I am going to give you some raw data and information about a patient's health. I want you to summarize the information for me 
    by extracting the insights that are most valuable for the patient as concisely as possible. Here is the raw data: """
    if raw_ext is not None:
        prompt = prompt + raw_ext[0]
        llm = load_llm()
        response = llm(prompt)
        upload_ext_summary(response, rowid)
    else:
        return "No data available"
    
def summarize_patient_health(rowid):
    raw_ext = get_raw_ext_data(rowid) 
    print(rowid)
    prompt = """I am going to give you some raw data and information about a patient's health. I want you to summarize the information for me 
    by extracting the insights that are most valuable for the patient as concisely as possible. Here is the raw data: """
    if raw_ext is not None:
        prompt = prompt + raw_ext[0]
        llm = load_llm()
        response = llm(prompt)
        upload_ext_summary(response, rowid)

    else:
        return "No data available"
    