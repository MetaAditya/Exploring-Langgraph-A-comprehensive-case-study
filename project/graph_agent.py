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
import time
from diagnosis_determine_subgraph import cataract_diagnosis_subgraph
from post_diagnosis_subgraph import compiled_post_diagnosis_subgraph


###########################################################
def route_decision(state: PatientState) -> Dict:

    """Decision Node: If the Cataract Diagnosis subgraph was pending, then resume from the point where it was intermediately stopped"""

    if state["resume"]:
         state['suggestion']='cataract_diagnosis_subgraph'
         typewriter(f"""\n{blue_}Reception Agent: {white_} Resuming cataract diagnosis... \n\n""")
         return state['suggestion']
    

    return state["suggestion"]



def route_decision_between_subgraphs(state: PatientState) -> Dict:

    """Decision Node: Handles control flow between Cataract diagnosis subgraph and Post diagnosis subgraph"""

    if state["intermediate_stop"]=='yes':
         state['suggestion']='main_graph_finish_point'
         return state['suggestion']
    else:
        state['suggestion']='post_diagnosis_subgraph'
         
        return state["suggestion"]



def main_graph_finish_point(state: PatientState) -> None:

    """ End of Line for main graph """

    if state['intermediate_stop']!='yes':
         
        typewriter(f"{blue_}Reception Agent: {white_} The patient has completed all consultations 😄😄 \n\n")

        store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )

        ###clearing the state, ready for the new execution
        with store as store:
            store.delete(state['patient_name'], "cataract_diagnosis")


        return None



######################### Graph #####################
graph = StateGraph(PatientState)

graph.add_node("receptionist",  with_node_name("receptionist", recipient_agent_function))
graph.add_node("physician", with_node_name("physician", physician_agent_function))
graph.add_node("nephrologist", with_node_name("nephrologist", nephro_agent_function))
graph.add_node("ophthalmologist",with_node_name("ophthalmologist", opto_agent_function))

graph.add_node("cataract_diagnosis_subgraph",cataract_diagnosis_subgraph)
graph.add_node("post_diagnosis_subgraph",compiled_post_diagnosis_subgraph)
graph.add_node("main_graph_finish_point",with_node_name("main_graph_finish_point", main_graph_finish_point))



graph.set_entry_point("receptionist")


graph.add_conditional_edges(
    "receptionist",
    route_decision,
    {
        "Physician": "physician",
        "Ophthalmologist": "ophthalmologist",
        "Nephrologist": "nephrologist",
        "cataract_diagnosis_subgraph":"cataract_diagnosis_subgraph"

    }
)



graph.add_edge("ophthalmologist", "cataract_diagnosis_subgraph")


graph.add_conditional_edges(
    "cataract_diagnosis_subgraph",
    route_decision_between_subgraphs,
    {
        "main_graph_finish_point": "main_graph_finish_point",
        "post_diagnosis_subgraph": "post_diagnosis_subgraph",
        
       

    }
)


graph.add_edge("physician", "main_graph_finish_point")
graph.add_edge("nephrologist", "main_graph_finish_point")
graph.add_edge("post_diagnosis_subgraph", "main_graph_finish_point")



graph.set_finish_point("main_graph_finish_point")



hospital_graph = graph.compile()


################################  #####################################3

def invoke_main_graph(state:PatientState) -> PatientState:


    """Main Graph Function"""
   
    
    typewriter(f"{blue_}Reception Agent:{white_}Welcome to our hospital \nPlease choose (Enter the numerals) the patient among the following  \n")
    print("""
            1) Patient 1 (routes to physician)
            2) Patient 2 (routes to nephrologist)
            3) Patient 3 (routes to ophthalmologist - cataract)

        """)
    
    patient_name = input(f"{red_}User: {green_} ").strip()
    typewriter(f"{blue_}Reception Agent:{white_} Alright!! \n")

    if patient_name == '1':
        patient=patient_1
    elif patient_name == '2':
        patient=patient_2
    elif patient_name == '3':
        patient=patient_3
    else:
        patient=patient_3


    state['patient_name'] = patient['patient_name']

    state['patient_condition']=patient


    for event in hospital_graph.stream(
        
        state,
        stream_mode="messages" ,
        
            
        ):
            print(event)






invoke_main_graph(state=default_state)


####################################################


