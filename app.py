import streamlit as st
import pandas as pd
from services import get_patient_data, summarize_ext_health, summarize_patient_health
from config import load_llm, llm_conversation
from streamlit_chat import message
import sqlite3
from langchain_community.document_loaders import PyPDFLoader, image
from dbops import raw_to_sqlite, df_to_sqlite, get_ext_sum, get_full_sum

# button css
custom_css = """
<style>
div[role="radiogroup"] > label {
    background-color: #00000000;
    padding: 10px 15px;
    border-radius: 20px;
    border: 1px solid #e0e0e0;
    margin-bottom: 20px;
}

div[data-testid="stSidebar"] div[role="radiogroup"] label {
    font-size: 20px; /* Adjust font size as needed */
}

div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child > div {
    background-color: #4CAF50 !important; /* Green background for selected item */
}

div[role="radiogroup"] > label:hover {
    background-color: #373737; /* Lighter grey on hover */
}

/* Hide the default radio button */
div[role="radiogroup"] > label > div:first-child {
    display: none;
}

div[role="radiogroup"] > label[data-baseweb="radio"].st-ae.st-ag.st-ah.st-ai.st-aj.st-ak.st-al.st-am.st-an.st-ao.st-ap.st-aq.st-ar.st-as.st-at.st-au.st-av.st-aw.st-ax.st-ay.st-az.st-b0.st-b1.st-b2.st-b3.st-b4 > div:first-child > div {
    background-color: transparent !important;
    display: inline-block;
}

div[role="radiogroup"] > label[data-baseweb="radio"].st-ae.st-ag.st-ah.st-ai.st-aj.st-ak.st-al.st-am.st-an.st-ao.st-ap.st-aq.st-ar.st-as.st-at.st-au.st-av.st-aw.st-ax.st-ay.st-az.st-b0.st-b1.st-b2.st-b3.st-b4 > div:first-child:after {
    content: "✔";
    color: white;
    font-size: 18px;
    position: absolute;
    left: 6px;
    top: 6px;
}
</style>
"""

st.set_page_config(
    page_title="Patient Record Dashboard",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded"
)

#st.title("IntegraCare Patient Record Dashboard")

# Custom CSS for styling the title banner
st.markdown("""
    <style>
        /* Style the title to make it stand out */
        .title-banner {
            background-color: #222; /* Dark background color */
            color: #fff; /* White text color */
            padding: 30px 0; /* Add padding for spacing */
            font-size: 36px; /* Larger font size */
            font-weight: bold; /* Bold text */
            text-align: center; /* Center align the title */
            margin-bottom: 30px; /* Add margin to separate from content */
            border-bottom: 4px solid #4CAF50; /* Green underline */
        }

        /* Style the page content */
        .content {
            padding: 20px; /* Add padding for content */
            background-color: #333; /* Darker background color */
            color: #fff; /* White text color */
        }
    </style>
""", unsafe_allow_html=True)

# Render the title banner
st.markdown("<div class='title-banner'>IntegraCare Patient Record Dashboard</div>", unsafe_allow_html=True)

# Content area with a dark background
st.markdown("<div class='content'>", unsafe_allow_html=True)

# Your content goes here

# End of content area
st.markdown("</div>", unsafe_allow_html=True)

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

st.markdown(custom_css, unsafe_allow_html=True)

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
    patient_search_query = str(st.text_input(
        "Search by Patient ID: ",
        placeholder = "e.g. 1001",
    ))
    st.text("Or:")
    filtered_patients = {name: pat for name, pat in individual_patients.items() if patient_search_query.lower() in str(name).lower()} if patient_search_query else individual_patients
    selected_patient_name = st.selectbox('Select a patient:', list(filtered_patients.keys()), key="patient_dropdown")
    if st.button('Select'):
        st.session_state['selected_patient_id'] = filtered_patients[selected_patient_name]['id']
        if st.session_state['selected_patient_id']:
            st.subheader('Patient Details')
            selected_patient_details = individual_patients[st.session_state['selected_patient_id']]
            patient_data = {
                'Attribute': ['Name', 'Age', 'Race', 'Phone'],
                'Data': [
                    selected_patient_details['name'],
                    selected_patient_details['age'],
                    selected_patient_details['race'],
                    selected_patient_details['phone']
                ]
            }
            patient_df = pd.DataFrame(patient_data)
            st.markdown("""
                <style>
                    /* Adjust font size and family */
                    table th, table td {
                        font-size: 16px;
                        font-family: Arial, sans-serif;
                        color: white; /* Set text color to white */
                    }
                    /* Set background color for header row */
                    table th {
                        background-color: #333; /* Dark grey */
                        border-bottom: 2px solid #444; /* Darker grey border */
                        padding: 12px;
                        text-align: left;
                    }
                    /* Set background color for even rows */
                    table tr:nth-child(even) {
                        background-color: #222; /* Darker grey */
                    }
                    /* Set background color for odd rows */
                    table tr:nth-child(odd) {
                        background-color: #111; /* Darkest grey */
                    }
                    /* Set hover effect */
                    table tr:hover {
                        background-color: #555; /* Light grey */
                    }
                    /* Add padding to cells */
                    table td {
                        padding: 10px;
                        border-bottom: 1px solid #444; /* Darker grey border */
                    }
                </style>
            """, unsafe_allow_html=True)
            st.table(patient_df)
            #st.write(f"Name: {selected_patient_details['name']}")
            #st.write(f"Age: {selected_patient_details['age']}")
            #st.write(f"Race: {selected_patient_details['race']}")
            #st.write(f"Phone: {selected_patient_details['phone']}")
            #st.write(f"Current Appointment Details: {selected_patient_details['Current Appointment Details']}")
            
            

elif selection == "Patient Details":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader('Patient Details')
        if st.session_state['selected_patient_id']:
            patient_details = individual_patients[st.session_state['selected_patient_id']]
            with st.expander("Show Patient Details"):
                st.markdown("""
                    <style>
                        /* Adjust font size and family */
                        .expanderContent > div > div > div > div > div {
                            font-size: 16px;
                            font-family: Arial, sans-serif;
                            color: white; /* Set text color to white */
                        }
                        /* Set background color for expander header */
                        .expanderContainer > div > div > div {
                            background-color: #333; /* Dark grey */
                            border-bottom: 2px solid #444; /* Darker grey border */
                            padding: 12px;
                        }
                        /* Set background color for expander content */
                        .expanderContent > div > div {
                            background-color: #222; /* Darker grey */
                            padding: 12px;
                        }
                        /* Set divider between items */
                        .expanderContent > div > div > div > div {
                            border-bottom: 1px solid #444; /* Darker grey border */
                            padding-bottom: 8px;
                            margin-bottom: 8px;
                        }
                    </style>
                """, unsafe_allow_html=True)
                st.write(f"Name: {patient_details['name']}")
                st.write(f"Age: {patient_details['age']}")
                st.write(f"Race: {patient_details['race']}")
                st.write(f"Phone: {patient_details['phone']}")
    
    with col2:
        st.subheader('Full Medical History')
        if st.session_state['selected_patient_id']:
            patient_details = individual_patients[st.session_state['selected_patient_id']]
            with st.expander("Show Full Medical History"):
                st.markdown("""
                    <style>
                        /* Adjust font size and family */
                        .expanderContent > div > div > div > div > div {
                            font-size: 16px;
                            font-family: Arial, sans-serif;
                            color: white; /* Set text color to white */
                        }
                        /* Set background color for expander header */
                        .expanderContainer > div > div > div {
                            background-color: #333; /* Dark grey */
                            border-bottom: 2px solid #444; /* Darker grey border */
                            padding: 12px;
                        }
                        /* Set background color for expander content */
                        .expanderContent > div > div {
                            background-color: #222; /* Darker grey */
                            padding: 12px;
                        }
                        /* Set divider between items */
                        .expanderContent > div > div > div > div {
                            border-bottom: 1px solid #444; /* Darker grey border */
                            padding-bottom: 8px;
                            margin-bottom: 8px;
                        }
                    </style>
                """, unsafe_allow_html=True)
                st.write(f"Medical History: {patient_details['medical_history']}")
                st.write(f"Family History: {patient_details['Family History']}")
                out_of_network_info = get_ext_sum(st.session_state['selected_patient_id'])[0]
                st.write(f"Out of Network Information: {out_of_network_info}")
         
    with col3:
        st.subheader("Ask Your Assistant")
        if "history" not in st.session_state:
            st.session_state.history = []

        input_text = st.chat_input("Ask me anything", key="chat_input")
        sum = ""
        if "selected_patient_id" in st.session_state:
            sum = get_full_sum(st.session_state['selected_patient_id'])
        if input_text:
            chat_response = llm_conversation(input_text=input_text, full_summary= sum)
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
                st.markdown("""
                    <style>
                        /* Adjust font size and family */
                        .expanderContent > div > div > div > div > div {
                            font-size: 16px;
                            font-family: Arial, sans-serif;
                            color: white; /* Set text color to white */
                        }
                        /* Set background color for expander header */
                        .expanderContainer > div > div > div {
                            background-color: #333; /* Dark grey */
                            border-bottom: 2px solid #444; /* Darker grey border */
                            padding: 12px;
                        }
                        /* Set background color for expander content */
                        .expanderContent > div > div {
                            background-color: #222; /* Darker grey */
                            padding: 12px;
                        }
                        /* Set divider between items */
                        .expanderContent > div > div > div > div {
                            border-bottom: 1px solid #444; /* Darker grey border */
                            padding-bottom: 8px;
                            margin-bottom: 8px;
                        }
                    </style>
                """, unsafe_allow_html=True)
                st.write(f"Name: {patient_details['name']}")
                st.write(f"Age: {patient_details['age']}")
                st.write(f"Race: {patient_details['race']}")
                st.write(f"Phone: {patient_details['phone']}")

    with col2:
        st.subheader('Appointment Details')
        if st.session_state['selected_patient_id']:
            patient_details = individual_patients[st.session_state['selected_patient_id']]
            with st.expander("Show Appointment Details"):
                st.markdown("""
                    <style>
                        /* Adjust font size and family */
                        .expanderContent > div > div > div > div > div {
                            font-size: 16px;
                            font-family: Arial, sans-serif;
                            color: white; /* Set text color to white */
                        }
                        /* Set background color for expander header */
                        .expanderContainer > div > div > div {
                            background-color: #333; /* Dark grey */
                            border-bottom: 2px solid #444; /* Darker grey border */
                            padding: 12px;
                        }
                        /* Set background color for expander content */
                        .expanderContent > div > div {
                            background-color: #222; /* Darker grey */
                            padding: 12px;
                        }
                        /* Set divider between items */
                        .expanderContent > div > div > div > div {
                            border-bottom: 1px solid #444; /* Darker grey border */
                            padding-bottom: 8px;
                            margin-bottom: 8px;
                        }
                    </style>
                """, unsafe_allow_html=True)
                st.write(f"Prescription: {patient_details['Prescription']}")
                other_notes = st.text_area("Other Notes", patient_details['Other Notes'])
                individual_patients[st.session_state['selected_patient_id']]['Other Notes'] = other_notes
                
    with col3:
        st.subheader("Ask Your Assistant")
        if "history" not in st.session_state:
            st.session_state.history = []

        input_text = st.chat_input("Ask me anything", key="chat_input")
        sum = ""
        if "selected_patient_id" in st.session_state:
            sum = get_full_sum(st.session_state['selected_patient_id'])
        if input_text:
            chat_response = llm_conversation(input_text=input_text, full_summary= sum)
            new_user_message = {"role": "user", "text": input_text}
            new_chat_response = {"role": "assistant", "text": chat_response}
            st.session_state.history.insert(0, new_chat_response)
            st.session_state.history.insert(0, new_user_message)

        for message in st.session_state.history:
            with st.chat_message(message["role"]):
                st.markdown(message["text"])


elif selection == "Patient Data Manager":
    st.subheader("Patient Data Manager")
    if st.session_state['selected_patient_id'] is not None:
        st.markdown(f"<h4>Patient: {st.session_state['selected_patient_id']}<h4>", unsafe_allow_html=True)
    else:
        st.markdown("<h4>No patient selected<h4>", unsafe_allow_html=True)
        
    with st.expander("Upload Patient Records", expanded=True):
        patient_data = st.file_uploader("Upload Spreadsheet Records", type=['csv'])
        patient_pdf = st.file_uploader("Upload PDF Records", type=['pdf'])
        patient_image = st.file_uploader("Upload Screenshot of Records", type=['png'])

    if (patient_data or patient_pdf or patient_image) is not None:
        st.success("File uploaded successfully!")
    else: 
        st.warning("Please upload a file!")

    if patient_pdf is not None:
        pdf_loader = PyPDFLoader(patient_pdf.name)
        page = pdf_loader.load()[0].page_content
        if st.session_state['selected_patient_id'] is not None:
            raw_to_sqlite(page, st.session_state['selected_patient_id'])
            summarize_ext_health(st.session_state['selected_patient_id'])
            summarize_patient_health(st.session_state['selected_patient_id'])

    if patient_data is not None:
        if st.session_state['selected_patient_id'] is not None:
            df_to_sqlite(patient_data, st.session_state['selected_patient_id'])
    
    if patient_image is not None:
        if st.session_state['selected_patient_id'] is not None:
            image_loader = image.UnstructuredImageLoader(patient_image)
            image_data = image_loader.load()[0].page_content
            raw_to_sqlite(image_data, st.session_state['selected_patient_id'])
            summarize_ext_health(st.session_state['selected_patient_id'])
            summarize_patient_health(st.session_state['selected_patient_id'])




    
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
            

