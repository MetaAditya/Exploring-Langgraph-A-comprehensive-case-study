from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import argparse
import json,ast
import operator
import math
import boto3
import operator
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage, BaseMessage

from langgraph.graph import StateGraph, END, START
from langchain_aws import ChatBedrock
from langchain_classic.agents import create_openai_tools_agent
from langchain_classic.agents import AgentExecutor
from langchain_classic.tools import tool

from langchain.agents import create_agent
from patient_data import *
import os, pprint
from langchain_openai import ChatOpenAI
from state_models import *
from langgraph.types import interrupt
from langgraph.checkpoint.postgres import PostgresSaver

from langgraph.store.postgres import PostgresStore
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig





############# Physician Agent ##########################################3

physician_prompt_="""

You are a physician at a multi-speciality hospital.

You will receive patient information as a Python dictionary, and you also have access to session memory under the key "heart_visit_count", which stores how many times the patient previously came with heart-related issues.

Your tasks:

1. Read all symptom data from the provided Python dictionary.

2. Identify the most likely medical condition and place it in "condition".

3. Recommend suitable home remedies in "remedies".

4. Suggest safe, commonly used medications in "medication".

5. Provide a short explanation in "reason".


Your output must be valid JSON using exactly this structure:

{
  "phy_condition": "<diagnosed illness or disorder>",
  "remedies": "<recommended home remedies>",
  "medication": "<recommended medications>",
  "reason": "<short explanation>",
  "severity": "<LOW / MODERATE / HIGH / NA>"
}

Do NOT output anything outside the JSON.


    """



# assistant_response=physician_agent(f"User data: {patient_1}")

physician_agent = create_agent(

    model=llm,
    tools=[],
    system_prompt=physician_prompt_
)


def physician_agent_function(state: PatientState) ->str:


    patient_condition=state.get('patient_condition',{})
    result = physician_agent.invoke(
        {"messages": [HumanMessage(f"{patient_condition}")]}
    )

    

    final_response=result['messages'][1].content[0]['text'].replace("\n","")
    final_response=ast.literal_eval(final_response)

    typewriter(f"""{blue_}Physician Agent. {white_} Observations ⬇️ \n\n""")
    pprint.pprint(final_response)

    
    return {**default_state, **state}



############################# Nephrologist Agent ##############################3
nephrologist_prompt_="""

You are a Nephrologist at a multi-speciality hospital.

Your task is to analyze patient information provided as a Python dictionary and return a diagnosis and guidance in strict JSON format.

Instructions:

1. Read and interpret all symptom data from the provided Python dictionary.

2. Identify the most likely medical condition based on the symptoms and place it in the "condition" field.

3. Suggest appropriate home remedies in the "remedies" field.

4. Suggest suitable medications in the "medication" field. 
   (Only include commonly used, safe, over-the-counter or first-line medications.)

5. Provide a concise explanation for your conclusions in the "reason" field.

6. Your final output MUST be valid JSON in exactly the following structure:

{
  "neph_condition": "<diagnosed illness or disorder>",
  "remedies": "<recommended home remedies>",
  "medication": "<recommended medications>",
  "reason": "<short explanation>"
}

Do NOT output anything outside the JSON.

    """


nephro_agent = create_agent(

    model=llm,
    tools=[],
    system_prompt=nephrologist_prompt_
)


def nephro_agent_function(state: PatientState) ->str:

    patient_condition=state.get('patient_condition',{})
    result = physician_agent.invoke(
        {"messages": [HumanMessage(f"{patient_condition}")]}
    )

    final_response=result['messages'][1].content[0]['text'].replace("\n","")
    final_response=ast.literal_eval(final_response)

    typewriter(f"""{blue_}Nephrologist Agent.{white_} Observations ⬇️  \n\n""")
    pprint.pprint(final_response)

    
    
    return {**default_state, **state}





####################################################################################3

opto_prompt_="""

You are a cardiologist at a multi-speciality hospital.

Your task is to analyze patient information provided as a Python dictionary and return a diagnosis and guidance in strict JSON format.

Instructions:

1. Read and interpret all symptom data from the provided Python dictionary.

2. Identify the most likely medical condition based on the symptoms and place it in the "condition" field.

3. Suggest appropriate home remedies in the "remedies" field.

4. Suggest suitable medications in the "medication" field. 
   (Only include commonly used, safe, over-the-counter or first-line medications.)

5. Provide a concise explanation for your conclusions in the "reason" field.

6. Your final output MUST be valid JSON in exactly the following structure:



{
  "opto_condition": "<diagnosed illness or disorder>",
  "remedies": "<recommended home remedies>",
  "medication": "<recommended medications>",
  "reason": "<short explanation>"
}

Do NOT output anything outside the JSON.

    """




opto_agent = create_agent(

    model=llm,
    tools=[],
    system_prompt=opto_prompt_
)

def opto_agent_function(state: PatientState) ->str:

    # print("Opto triggered")
    patient_condition=state.get('patient_condition',{})
    result = opto_agent.invoke(
        {"messages": [HumanMessage(f"{patient_condition}")]}
    )

    

    final_response=result['messages'][1].content[0]['text'].replace("\n","")
    final_response=ast.literal_eval(final_response)

    typewriter(f"""{blue_}Ophthalmologist Agent. {white_} Observations ⬇️  \n\n""")
    pprint.pprint(final_response)
    typewriter(f"""{blue_}Ophthalmologist Agent. {white_} You are being routed to Cataract Department for further examination ⬇️  \n\n""")


    return {**default_state, **state}





######################################################################################

current_date="12/17/2025"
receptionist_prompt_="""

You are a medical triage assistant.

Your role is to analyze patient information provided as a Python dictionary and return a recommendation in strict JSON format.

Instructions:

1. Analyze the user's information provided as a Python dictionary.
.

2. Check the last appointment date:
   - Date will be in the form mm/dd/yy
   - If the last appointment was more than 60 days ago from {current_date}, then:
       * Set "suggestion" to "Renew Appointment"
       * Set "reason" to a short explanation
     Do NOT analyze symptoms in this case.

3. If the last appointment is within 60 days:
   - Analyze the symptoms in the dictionary.
   - Recommend ONE doctor from this list only:
       1) Physician
       2) Ophthalmologist
       3) Nephrologist

4. Provide a short and clear explanation in the "reason" field.

5. Your output MUST be valid JSON in exactly this structure:

{
  "suggestion": "<doctor name or 'Renew Appointment'>",
  "reason": "<short explanation>"
}

Do NOT output anything outside the JSON.



    """




recipient_agent = create_agent(

    model=llm,
    tools=[],
    system_prompt=receptionist_prompt_
)


def recipient_agent_function(state: PatientState) ->str:


    ##Chcek for last resuming point, if found jump to that point
    store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )
    with store as store:
        last_checkpoint=get_from_store(store, state['patient_name'], state['sub_graph'])
        # last_checkpoint=get_from_store(store, 'Youhali', state['sub_graph'])
        

    if last_checkpoint!=None:
        last_checkpoint_value=last_checkpoint.value

        state["resume"]=True
        
        return {**default_state, **state}


        
    #Else no chcekpoint found, process the request
    if last_checkpoint==None:

    
        patient_condition=state.get('patient_condition',{})
        result = recipient_agent.invoke(
            {"messages": [HumanMessage(f"{patient_condition}")]}

            


        )
        final_response=result['messages'][1].content[0]['text'].replace("\n","")
        final_response=ast.literal_eval(final_response)

        suggestion=final_response.get("suggestion","")
        state['suggestion']=suggestion

        typewriter(f"""\n{blue_}Reception Agent: {white_} You are being routed to {suggestion} \n\n""")

        
        
        
        
        return {**default_state, **state}
    
    
        




    




###############################################################

