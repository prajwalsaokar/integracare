import time
import streamlit as st
import pandas as pd
from .config import load_llm

st.title("Patient Record Dashboard")
patient_data = st.file_uploader("patientData.csv", type=['csv'])





model = load_llm()

def get_patient_data(patient_id):
    return {
        'name': 'John Doe',
        'age': '30',
        'race': 'Caucasian',
        'phone': '123-456-7890',
        'medical_history': 'Medical history details here.'
    }

patient_list = {
    'Patient 1': {'id': 1},
    'Patient 2': {'id': 2},
    'Patient 3': {'id': 3},
    'Patient 4': {'id': 4},
}

if 'selected_patient_id' not in st.session_state:
    st.session_state['selected_patient_id'] = None

pages = {
    "Search Patients": "search_patients",
    "Patient Details": "patient_details"
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

if selection == "Search Patients":
    st.subheader('Search Patients')
    patient_search_query = st.text_input('')
    filtered_patients = {name: pat for name, pat in patient_list.items() if patient_search_query.lower() in name.lower()} if patient_search_query else patient_list
    selected_patient_name = st.radio('Select a patient:', list(filtered_patients.keys()))
    if st.button('Show Details'):
        st.session_state['selected_patient_id'] = filtered_patients[selected_patient_name]['id']
        st.experimental_rerun()

elif selection == "Patient Details":
    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.subheader('Patient Details')
        if st.session_state['selected_patient_id']:
            patient_data = get_patient_data(st.session_state['selected_patient_id'])
            st.write(f"Name: {patient_data['name']}")
            st.write(f"Age: {patient_data['age']}")
            st.write(f"Race: {patient_data['race']}")
            st.write(f"Phone: {patient_data['phone']}")
    with col2:
        if st.session_state['selected_patient_id']:
            st.subheader('Medical History')
            patient_data = get_patient_data(st.session_state['selected_patient_id'])
            st.write(patient_data['medical_history'])
    with col3:
        st.title("Your Assistant")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask something..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                result = model.predict(input=prompt)

                # Simulate stream of response with milliseconds delay
                for chunk in result.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
