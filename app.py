import streamlit as st
import pandas as pd
from services import get_patient_data
from config import load_llm, llm_conversation
from streamlit_chat import message
import sqlite3

st.title("Patient Record Dashboard")

# Data loading
file = pd.read_sql("SELECT * FROM patients", sqlite3.connect("patients.db"))
data_list = get_patient_data(file)
individual_patients = {}

num_patients = len(data_list['id'])
for i in range(num_patients):
    patient_id = data_list['id'][i]
    individual_patients[patient_id] = {
    "id" : data_list['id'][i],
    "name": data_list['name'][i],
    "age": data_list['age'][i],
    "race": data_list['race'][i],
    "phone": data_list['phone'][i],
    "medical_history": data_list['medical_history'][i],
    "Current Appointment Details": data_list['Current Appointment Details'][i],
    "Prescription": data_list['Prescription'][i],
    "Other Notes": data_list['Other Notes'][i],
    "Family History": data_list['Family History'][i]
}

    
if 'selected_patient_id' not in st.session_state:
    st.session_state['selected_patient_id'] = None

pages = {
    "Search Patients": "search_patients",
    "Patient Data Manager": "data_management",
    "Patient Details": "patient_details",
    "Appointment Details" : "appointment_details"
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

if selection == "Search Patients":
    st.subheader('Search Patients')
    patient_search_query = str(st.text_input(''))
    filtered_patients = {name: pat for name, pat in individual_patients.items() if patient_search_query.lower() in str(name).lower()} if patient_search_query else individual_patients
    selected_patient_name = st.selectbox('Select a patient:', list(filtered_patients.keys()), key="patient_dropdown")
    if st.button('Select'):
        st.session_state['selected_patient_id'] = filtered_patients[selected_patient_name]['id']
        if st.session_state['selected_patient_id']:
            st.subheader('Patient Details')
            selected_patient_details = individual_patients[st.session_state['selected_patient_id']]
            st.write(f"Name: {selected_patient_details['name']}")
            st.write(f"Age: {selected_patient_details['age']}")
            st.write(f"Race: {selected_patient_details['race']}")
            st.write(f"Phone: {selected_patient_details['phone']}")
            st.write(f"Current Appointment Details: {selected_patient_details['Current Appointment Details']}")

elif selection == "Patient Details":
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.subheader('Patient Details')
        if st.session_state['selected_patient_id']:
            patient_details = individual_patients[st.session_state['selected_patient_id']]
            with st.expander("Show Patient Details"):
                st.write(f"Name: {patient_details['name']}")
                st.write(f"Age: {patient_details['age']}")
                st.write(f"Race: {patient_details['race']}")
                st.write(f"Phone: {patient_details['phone']}")
    with col2:
        if st.session_state['selected_patient_id']:
            st.subheader('Medical History')
            patient_details = individual_patients[st.session_state['selected_patient_id']]
            st.write(patient_details['medical_history'])
            

    with col3:
        st.title("Ask Your Assistant")
        if "history" not in st.session_state:
            st.session_state.history = []

        input_text = st.chat_input("Ask me anything", key="chat_input")

        if input_text:
            chat_response = llm_conversation(input_text=input_text)
            new_user_message = {"role": "user", "text": input_text}
            new_chat_response = {"role": "assistant", "text": chat_response}
            st.session_state.history.insert(0, new_chat_response)
            st.session_state.history.insert(0, new_user_message)

        for message in st.session_state.history:
            with st.chat_message(message["role"]):
                st.markdown(message["text"])
        

elif selection == "Appointment Details":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader('Patient Details')
        if st.session_state['selected_patient_id']:
            patient_details = individual_patients[st.session_state['selected_patient_id']]
            with st.expander("Show Patient Details"):
                st.write(f"Name: {patient_details['name']}")
                st.write(f"Age: {patient_details['age']}")
                st.write(f"Race: {patient_details['race']}")
                st.write(f"Phone: {patient_details['phone']}")

    with col2:
        st.subheader('Appointment Details')
        if st.session_state['selected_patient_id']:
            patient_details = individual_patients[st.session_state['selected_patient_id']]
            with st.expander("Show Appointment Details"):
                st.write(f"Prescription: {patient_details['Prescription']}")
                other_notes = st.text_area("Other Notes", patient_details['Other Notes'])
                individual_patients[st.session_state['selected_patient_id']]['Other Notes'] = other_notes

    with col3:
        st.title("Ask Your Assistant")
        if "history" not in st.session_state:
            st.session_state.history = []
        for message in st.session_state.history:
            with st.chat_message(message["role"]):
                st.markdown(message["text"])
        input_text = st.chat_input("Ask me anything")
        if input_text:
            with st.chat_message("user"):
                st.markdown(input_text)
            st.session_state.history.append({"role": "user", "text": input_text})
            chat_response = llm_conversation(input_text = input_text)
            with st.chat_message("assistant"):
                st.markdown(chat_response)
            st.session_state.history.append({"role": "assistant", "text": chat_response})


elif selection == "Patient Data Manager":
    st.subheader("Patient Data Manager")
    if st.session_state['selected_patient_id'] is not None:
        st.markdown(f"<h4>Patient: {st.session_state['selected_patient_id']}<h4>", unsafe_allow_html=True)
    else:
        st.markdown("<h4>No patient selected<h4>", unsafe_allow_html=True)
    patient_data = st.file_uploader("Upload Spreadsheet Records", type=['csv'])
    patient_pdf = st.file_uploader("Upload PDF Records", type=['pdf'])
    patient_image = st.file_uploader("Upload Screenshot of Records", type=['png'])


    data_list = {}
    individual_patients = {}
    model = load_llm()

    if patient_data is not None:
        file = pd.read_csv(patient_data)
        data_list = get_patient_data(file)
        
        individual_patients = {}
        
        num_patients = len(data_list['id'])
        for i in range(num_patients):
            patient_id = data_list['id'][i]
            individual_patients[patient_id] = {
            "id" : data_list['id'][i],
            "name": data_list['name'][i],
            "age": data_list['age'][i],
            "race": data_list['race'][i],
            "phone": data_list['phone'][i],
            "medical_history": data_list['medical_history'][i],
            "Current Appointment Details": data_list['Current Appointment Details'][i],
            "Prescription": data_list['Prescription'][i],
            "Other Notes": data_list['Other Notes'][i]
        }
            

