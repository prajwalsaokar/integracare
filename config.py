import boto3
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import LLMChain
import json
import streamlit as st
import re


session = boto3.Session(
    profile_name='default',
    region_name='us-east-1'
)

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

system_prompt = """ You are a medical assistant that is helping a doctor with understanding his patients' data. 
"""



@st.cache_resource
def load_llm():
    llm = Bedrock(client=bedrock_runtime, model_id="amazon.titan-text-express-v1")
    return llm



def llm_conversation(input_text):
    chat_llm = load_llm()
    chat_prompt = ChatPromptTemplate(
        messages = 
        [
            SystemMessagePromptTemplate.from_template(template = system_prompt),
            HumanMessagePromptTemplate.from_template("{request}")

        ]
    )
    llm_chain = load_llm()
    conversation = LLMChain(llm = chat_llm, verbose = True, prompt = chat_prompt)
    reply = conversation({"request": input_text})
    formatted_reply = reply['text'].strip()
    return formatted_reply