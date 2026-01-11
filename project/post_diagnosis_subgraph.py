from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from bedrock_agentcore.runtime import BedrockAgentCoreApp
import argparse
import json
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
import os
from langchain_openai import ChatOpenAI
from state_models import *
from misc_agents import *
import asyncio
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
import time, ast, pprint
from langchain_core.messages import ToolMessage
import threading, time, pprint


###########################################
user_name='langgraph_user'
user_password='langgraph_password'
database_DB='langgraph_DB'
store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )

###########################################################

def route_counselling_subgraph(state: PatientState):
    
    """Decision Node: Decides whether to proceed to Surgery phase or keep looping in Insuraance Q&A"""

    return state['surgery_route_status']
    
    

############################################################


re_physician_prompt_ = """

You are a routing agent.

Your task is to select and invoke exactly ONE appropriate tool
based on the input data provided.

Available tools:
- blood_test: use ONLY if blood test data is present
- ecg_test: use ONLY if ECG data is present

Rules:
- You MUST call one tool.
- Do NOT analyze, interpret, or explain results.
- Do NOT modify the input data in any way.
- Pass the relevant data to the tool exactly as received.
- Return ONLY the tool’s output.
- Do NOT generate any text outside the tool call.

Decision rules:
- If blood test data exists, call blood_test.
- Else if ECG data exists, call ecg_test.
- If both exist, prefer blood_test.

"""



@tool("blood_test")
def blood_test_tool(patient_blood_info: Dict) -> str:
    " Tool that examines the blood test data of the patient and returns the report. "

    blood_report_status='normal'
    
    if (patient_blood_info['hemoglobin'] < 13.5) or (patient_blood_info['hemoglobin'] > 17.5):
        
        blood_report_status='abnormal'


    if (patient_blood_info['rbc'] < 4.7) or (patient_blood_info['rbc'] > 6.1):
        blood_report_status='abnormal'
        

    if (patient_blood_info['creatinine'] < 0.7):
        blood_report_status='abnormal'
        



    return blood_report_status



    
@tool("ECG_test")
def ECG_test_tool(patient_ecg_info: Dict) -> str:
    " Tool that examines the ECG data of the patient and returns the report. "


    ecg_report_status='normal'
    if patient_ecg_info['heart_rate'] < 60 or patient_ecg_info['heart_rate'] > 100:
        ecg_report_status='abnormal'

   

    return ecg_report_status

      




re_physician_agent=create_agent(

    model=llm,
    tools=[blood_test_tool, ECG_test_tool],
    system_prompt=re_physician_prompt_ 
)


def re_physician_agent_function(state:PatientState) -> Dict:

    """Function that performs post-diagnostic analysis and determines the patient’s readiness for surgery."""

    typewriter(f"\n{white_}---------------Post Diagnosis Stage Consists of three steps------------------------------- \n1)Physician Checkup\n2)Insurance Counselling \n3)Appointment scheduling\n\n")
    time.sleep(3)
    tool_instruction="Analyse the test data"


    print(f"{blue_}Physician Agent {white_} Choose either '1' or '2' \n 1. Normal blood test report \n 2. Abnormal blood test report  \n")
    blood_test_chosen=input(f"{red_}User: {green_} ").strip()

    if blood_test_chosen=='1':
        blood_test_report=patient_3_normal_blood_test
    else:
        blood_test_report=patient_3_abnormal_blood_test

    print(f"{white_}Blood Test Report is ⬇️")
    pprint.pprint(blood_test_report)

    typewriter(f"\nAnalysing the report ..........\n")
    result = re_physician_agent.invoke(
        {"messages": [HumanMessage(f" {tool_instruction} {blood_test_report}")]}
    )

    

    
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):

            final_response=msg.content
            state['blood_test_status']=final_response
         
            
            typewriter(f"{blue_}Physician Agent: {white_}Blood test report are found to be  {final_response.upper()} \n\n")





    print(f"{blue_}Physician Agent: {white_} Choose either '1' or '2' \n 1. Normal ECG report \n 2. Abnormal ECG report  \n")
    ecg_test_chosen=input(f"{red_}User: {green_} ").strip()

    if ecg_test_chosen=='1':
        ecg_test_report=patient_3_normal_ecg
    else:
        ecg_test_report=patient_3_abnormal_ecg


    print(f"{white_}ECG Test Report is ⬇️")
    pprint.pprint(ecg_test_report)
    typewriter(f"\nAnalysing the report ..........\n")
    result = re_physician_agent.invoke(
        {"messages": [HumanMessage(f" {tool_instruction} {ecg_test_report}")]}
    )

    


    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):

            final_response=msg.content
            state['ecg_test_status']=final_response
         
            
            typewriter(f"{blue_}Physician Agent: {white_}ECG test report are found to be  {final_response.upper()} \n\n")

    

    if (state['blood_test_status']=='abnormal') or (state['ecg_test_status']=='abnormal'):
        state['final_status']='abnormal'
        typewriter(f"{red_}Final Post Diagnosis: {white_} Physician assesment is ABNORMAL, LASER aided surgery is recommended. \n")
        typewriter(f"{red_}Final Post Diagnosis: {white_} Routing to Counselling Stage \n\n")

    else:
        state['final_status']='normal'
        typewriter(f"{green_}Final Post Diagnosis: {white_} Physician assesment is NORMAL, Patient is fit for SICS surgery. \n")
        typewriter(f"{green_}Final Post Diagnosis: {white_} Routing to Counselling Stage \n\n")




    # print("State is ", state)


    time.sleep(2)
    return {**default_state, **state}
            

    
 

##############################################

surgery_counselling_prompt_= f"""
You are a Patient Counselling Agent at a multi-speciality eye hospital.

Your role is to explain insurance coverage clearly and answer patient questions
using ONLY the information provided below.

Insurance Information:
{surgery_counselling_data}

Instructions:
- Answer strictly based on the insurance information provided.
- Do NOT add assumptions, medical opinions, or external information.
- If a question cannot be answered using the given information, politely say so.
- Use simple, patient-friendly language.
- Be calm, clear, and reassuring.
- Do NOT output JSON, lists, or bullet points unless required by the question.
- Your final output MUST be a plain string.

Now answer the patient's question.
"""


counselling_agent=create_agent(

    model=llm,
    tools=[],
    system_prompt=surgery_counselling_prompt_
)

def surgery_counselling_agent_function(state: PatientState) -> Dict:

    """Function that performs surgery counselling based on patient questions."""


    ##For the first turn
    if state['counselling_agent_flag']!='1':

        
        

        typewriter(f"{blue_}Counselling Agent: {white_} I will be assisting you with the insurance process,\na)Cashless claim procedures,\nb)Pre-authorization timelines\nc)Reimbursement options.\nI will also explain what is covered, what isn't, and help ensure the process goes as smoothly as possible for you.\n")
        time.sleep(1)
        typewriter_fast(f"-------------{white_} Insurance details are---------\n {surgery_counselling_data}\n")

        state['counselling_agent_flag']='1'

        time.sleep(3)
        print(f"{blue_}Counselling Agent {white_} Choose either '1' or '2' \n 1. Do you have any questions? \n 2. Proceed to Surgery appointment  \n")
        option_chosen=input(f"{red_}User: {green_} ").strip()
        

        if option_chosen=='1':
            state['surgery_route_status']='no'

            typewriter(f"{blue_}Counselling Agent: {white_} Please ask your questions. \n\n")
            patient_question=input(f"{red_}User: {green_} ").strip()
            result = counselling_agent.invoke(
                {"messages": [HumanMessage(f" Patient question: {patient_question} ")]}
            )

            final_response=result['messages'][1].content[0]['text']
            typewriter(f"{blue_}Counselling Agent Response: {white_} {final_response} \n\n")

            print(f"{blue_}Counselling Agent {white_} Choose either '1' or '2' \n 1. Do you have any questions? \n 2. Proceed to Surgery appointment  \n")
            option_chosen=input(f"{red_}User: {green_} ").strip()

            if option_chosen=='1':
                state['surgery_route_status']='no'
            else:
                typewriter(f"{blue_}Counselling Agent: {white_} Sure routing to Appointment node \n\n")
                state['surgery_route_status']='yes'

        else:
            typewriter(f"{blue_}Counselling Agent: {white_} Sure routing to Appointment node \n\n")
            state['surgery_route_status']='yes'




    #Second turn onwards
    else:
        if state['surgery_route_status']=='no':

            typewriter(f"{blue_}Counselling Agent:{white_} Please ask your questions. \n\n")
            patient_question=input(f"{red_}User: {green_} ").strip()
            result = counselling_agent.invoke(
                {"messages": [HumanMessage(f" Patient question: {patient_question} ")]}
            )

            final_response=result['messages'][1].content[0]['text']
            typewriter(f"{blue_}Counselling Agent Response:{white_} {final_response} \n\n")

            print(f"{blue_}Counselling Agent {white_} Choose either '1' or '2' \n 1. Do you have any questions? \n 2. Proceed to Surgery appointment  \n")
            option_chosen=input(f"{red_}User: {green_} ").strip()

            if option_chosen=='1':
                state['surgery_route_status']='no'
            else:
                state['surgery_route_status']='yes'

        
    

    return {**default_state, **state}








# # surgery_counselling_agent_function(state)


###############################Appointment Agent ##############################

def appointment_node_function(state:PatientState) -> Dict:
    """ The node that fixes the appointment """

    typewriter(f"""{blue_}Appointment node: {white_}Please provide me the insurance related documents 
                  \nI will proceed with scheduling the surgery appointment, initiating the insurance claim process, and arranging medication counselling in Parallel  \n\n"""
                   )
    
    time.sleep(2)

    # return None

    return {**default_state, **state}




def insurance_claim_node_function(state:PatientState)-> None:

    """ The node that initiates the insurance claim through the cashless method. """

    

    print(f"""{blue_}Insurance claim node {white_} 
                    I have submitted the insurance claim through the cashless method. \n
                    Pre-approval generally takes 48 hours\n
                    Final approval shall be obtained post surgery only\n
                    You are required to deposit the balance amount to proceed to discharge \n
                    
                    {green_}{time.strftime('%X')}] Insurance Claim Node START | thread={threading.get_ident()}
                    {time.strftime('%X')}] Insurance Claim Node END | thread={threading.get_ident()}


                   """)
    


    return None
    




def surgery_schedule_node_function(state:PatientState)-> None:

    """ The node that schedules the surgery. """
  

    print(f"""{blue_}Surgery schedule node {white_} 
                    I have scheduled the surgery for you. \n
                    Please ensure all pre-operative instructions are followed.\n
                    You are required to deposit the balance amount to proceed to discharge \n
                    {green_}{time.strftime('%X')}] Surgery Schedule Node START | thread={threading.get_ident()}
                    {time.strftime('%X')}] Surgery Schedule Node END | thread={threading.get_ident()}


                   """)
    
   
    return None
    


def medication_node_function(state:PatientState)-> None:

    """ The node that advises the pre-surgery medication . """

    

    print(f"""{blue_}Medication node {white_} 
                    Please apply the drops at mentioned intervals \n
                    Avoid dying of hair, exposure to irritants.\n
                    Please do not develop any other medical complications like cough/cold as they shall affect the surgical procedure.\n\n
                    {green_}{time.strftime('%X')}] Medication Node START | thread={threading.get_ident()}
                    {time.strftime('%X')}] Medication Node END | thread={threading.get_ident()}
                   """)
    
    return None

    



def graph_finish_point(state:PatientState) -> Dict:
    """ The end node of the Post Diagnosis Subgraph. """

    typewriter(f"""{green_}Post Diagnosis Finish Point: {white_}Post Diagnosis Subgraph has been completed successfully. {white_} \n\n""")
    
    return {**default_state, **state}



#######################3 Construct the Graph ########################
post_diagnosis_subgraph = StateGraph(PatientState)

post_diagnosis_subgraph.add_node("re_physician_agent_node", with_node_name("re_physician_agent_node", re_physician_agent_function))
post_diagnosis_subgraph.add_node("surgery_counselling_node", with_node_name("surgery_counselling_node", surgery_counselling_agent_function))
post_diagnosis_subgraph.add_node("appointment_node", with_node_name("appointment_node", appointment_node_function))
post_diagnosis_subgraph.add_node("insurance_claim_node", with_node_name("insurance_claim_node", insurance_claim_node_function))
post_diagnosis_subgraph.add_node("surgery_schedule_node", with_node_name("surgery_schedule_node", surgery_schedule_node_function))
post_diagnosis_subgraph.add_node("medication_node", with_node_name("medication_node", medication_node_function))
post_diagnosis_subgraph.add_node("graph_finish_point", with_node_name("graph_finish_point", graph_finish_point))


post_diagnosis_subgraph.set_entry_point("re_physician_agent_node")

post_diagnosis_subgraph.add_edge("re_physician_agent_node", "surgery_counselling_node")

post_diagnosis_subgraph.add_conditional_edges(
              "surgery_counselling_node",
              route_counselling_subgraph,
              {
                  "yes": "appointment_node",
                  "no": "surgery_counselling_node"

              }

      
)

post_diagnosis_subgraph.add_edge("appointment_node", "insurance_claim_node",)
post_diagnosis_subgraph.add_edge("appointment_node", "surgery_schedule_node")
post_diagnosis_subgraph.add_edge("appointment_node", "medication_node")


post_diagnosis_subgraph.add_edge("insurance_claim_node", "graph_finish_point") 
post_diagnosis_subgraph.add_edge("surgery_schedule_node", "graph_finish_point")
post_diagnosis_subgraph.add_edge("medication_node", "graph_finish_point")


post_diagnosis_subgraph.set_finish_point("graph_finish_point")

compiled_post_diagnosis_subgraph = post_diagnosis_subgraph.compile()


############################

