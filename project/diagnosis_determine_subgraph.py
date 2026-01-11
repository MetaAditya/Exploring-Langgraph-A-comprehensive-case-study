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




#########################


def route_cataract_subgraph(state: PatientState):

    """ Decision Edge:  """

    if state['intermediate_stop']=='yes':
        return "default"



    if state["surgery_status"]=='proceed':

    
        return state["surgery_status"]
    
    elif state["surgery_status"]=='halt':

        return state["surgery_status"]
    
    else:
        return "default"



#########################################
def cataract_diagnosis_start_point(state: PatientState):
    
    """Starting Point of the Cataract diagnosis Subgraph"""
    
    state['sub_graph']='cataract_diagnosis'

    

   
    store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )
    with store as store:
        last_checkpoint=get_from_store(store, state['patient_name'], state['sub_graph'])
        
        
    
    if last_checkpoint==None:
        state['resumption_node']= 'start'
        typewriter(f"\n{white_}---------------Cataract Diagnosis Stage Consists of three steps--------------- \n1)Cataract agent\n2)Retina agent \n3)Neuro Opto Agent\n\n")
        time.sleep(3)
    
    else:
     
        last_checkpoint_value=last_checkpoint.value
      

        if last_checkpoint_value['cataract_consultation']=='completed':
            state['resumption_node']= "cataract_diagnosis_finish_point"
        
        elif last_checkpoint_value['cataract_consultation']=='pending':

            state['resumption_node']= last_checkpoint_value['last_node']


        if state['resumption_node']=="cataract_diagnosis_finish_point":
            typewriter(f"\n{blue_}Cataract diagnosis Start Point:  {white_}You have already completed the consultation process, proceed to next stage\n")
        else:
            
            next_agent=''
            if state['resumption_node']=='cataract_agent':
                next_agent='retina_agent'
            elif state['resumption_node']=='retina_agent':
                next_agent='neuro_opto_agent'

   
            typewriter(f"\n{blue_}Cataract diagnosis Start Point: {white_}Resuming from {state['resumption_node']}  Invoking {next_agent}...  \n")

    return {**default_state, **state}



def route_resume_cataract_subgraph(state: PatientState):

    """Decision Node: If there was a intermediate stop, then resumes from that checkpoint"""

    return state['resumption_node']




#########################################


def cataract_slit_test(user_choice:str)-> Dict:
    """     Performs a slit-lamp examination of each eye to directly inspect the crystalline lens.
    Identifies the presence, laterality (right eye, left eye, or both), type, and severity
    of cataract based on visible lens opacity, loss of transparency, and red reflex changes.
    This test is the primary clinical method used to confirm which eye has cataract.
        """
    
    if user_choice=="1":

        typewriter(f"""{blue_}Slit Test. {white_} Observations ⬇️\n""")
        pprint.pprint(patient_3_slit_lamp_result_inconclusive)
        typewriter(f"""\n{white_} Analysing.........\n""")
        time.sleep(1)

        typewriter(f"{blue_}Slit Lamp Tool: {white_} Slit Lamp Test unable to confirm presence of Cataract \n")
        typewriter(f"""{blue_}Ophthalmologist Agent. {white_} You are being routed to Visual field for further examination\n\n""")



        return patient_3_slit_lamp_result_inconclusive 
    else:

        typewriter(f"""{blue_}Slit Test. {white_} Observations ⬇️\n\n""")
        pprint.pprint(patient_3_slit_lamp_result_conclusive)
        typewriter(f"""\n{white_} Analysing.........\n""")
        time.sleep(1)
      
        typewriter(f"{blue_}Slit Lamp Tool: {white_} Slit Lamp Test confirms presence of Cataract ! \n\n")
        typewriter(f"""{blue_}Ophthalmologist Agent. {white_} You are being routed to Visual field to prove beyond doubt \n\n""")

        return patient_3_slit_lamp_result_conclusive 





def cataract_visual_field_test(user_choice:str) -> Dict:
    """         Performs a visual field (perimetry) assessment of each eye to evaluate peripheral
    and central visual sensitivity. This test helps identify visual field defects
    suggestive of optic nerve, retinal, or neurological conditions (e.g., glaucoma).
    It is not used to diagnose cataract or determine which eye has cataract, but
    may be used to rule out non-lens causes of vision loss.
        """
    
    if user_choice=="1":
    
        typewriter(f"""{blue_}Visual Field Test. {white_} Observations ⬇️\n""")
        pprint.pprint(patient_3_visual_field_result_inconclusive)
        typewriter(f"""\n{white_} Analysing.........\n""")
        time.sleep(1)

        typewriter(f"{blue_}Visual Field Tool: {white_} Visual Field Test unable to confirm presence of Cataract \n\n")
        

        return patient_3_visual_field_result_inconclusive 
    
    else:

        typewriter(f"""{blue_}Visual Field Test. {white_} Observations ⬇️\n""")
        pprint.pprint(patient_3_visual_field_result_conclusive)
        typewriter(f"""\n{white_} Analysing.........\n""")
        time.sleep(1)

        typewriter(f"{blue_}Visual Field Tool: {white_} Visual field Test confirms presence of Cataract ! \n\n")
        

        return patient_3_visual_field_result_conclusive 

    
    


cataract_prompt_ = """
You are a cataract specialist agent. 
Your task is to determine whether a patient has cataract, which eye is affected, 
and whether lens opacity fully explains their vision loss. 

You have access to the following tools:

1. slit_lamp_test:
   - Performs a slit-lamp examination of each eye to inspect the crystalline lens.
   - Identifies cataract presence, type, laterality, and severity.
   - Use this tool to **determine if cataract is present and which eye is affected**.

2. visual_field_test:
   - Performs a visual field assessment to evaluate peripheral and central vision.
   - Helps rule out optic nerve, retinal, or neurological causes.
   - Use this tool when the cataract finding is inconclusive, or to confirm vision loss is lens-related.



"""



########################################


cataract_specialist_agent=create_agent(

    model=llm,
    tools=[],
    system_prompt=cataract_prompt_
)


#########################################3




def cataract_agent_function(state: PatientState) -> None:
    """In here we examine the patient step by step , firstly the slit lamp test and then the visual field test
       The two results shall establish cataract to be or not be the cause of vision loss    
    """

    ## First Perform the Slit Lamp Test
    ##In here I am invoking the tools directly
 
    
    print(f"{blue_}Cataract Agent: {white_} Choose either '1' or '2' \n 1. Slit Lamp Report that does not confirm cataract \n 2. Slit Lamp Report that confirms cataract  \n")
    slit_user_choice=input(f"{red_}User: {green_} ").strip()




    slit_lamp_response = cataract_slit_test(slit_user_choice)


       
    time.sleep(1)
    clinical_mismatch_status=slit_lamp_response.get('clinical_mismatch', 'YES')
    if clinical_mismatch_status=='YES':
        
        state['slit_test_status']='uncertain'
        
    else:
               
        state['slit_test_status']='certain'
        
        

    ## Then Perform the Visual field Test
    print(f"{blue_}Cataract Agent: {white_} Choose either '1' or '2' \n 1. Visual Field Report that does not confirm cataract \n 2. Visual Field Report that confirms cataract  \n")
    visual_user_choice=input(f"{red_}User: {green_} ").strip()

    time.sleep(1)
    visual_field_response =cataract_visual_field_test(visual_user_choice)
    visual_field_status= visual_field_response.get("cataract_effect_likely", "NO")


    if visual_field_status=='NO':
        
        state['visual_test_status']='uncertain'
        
        
        
    else:
               
        state['visual_test_status']='certain'
        


    if 'certain' in [state['slit_test_status'], state['visual_test_status']]:
        state['surgery_status']='proceed'
        state['cataract_consultation']='completed'
        typewriter(f"{blue_}Cataract Agent: {white_} Cataract being the causative factor is CERTAIN, Routing to Finish Point ! \n")

    else:
        state['surgery_status']='halt'
        typewriter(f"{blue_}Cataract Agent: {white_} Cataract being the causative factor is UNCERTAIN, Routing to Retina Specialist \n")

        print(f"{blue_}Cataract Agent: {white_} Choose either '1' or '2' \n 1. Continue \n 2. End  \n")
        user_choice=input(f"{red_}User: {green_} ").strip()

        if user_choice=='2':
            state["intermediate_stop"]='yes'
            typewriter(f"{blue_}Cataract Agent: {white_} Alright! Ending the Consultation ! Have a Good Day 😀 \n ")

        else:
            typewriter(f"{blue_}Cataract Agent: {white_} Proceeding to Retina Specialist\n")



    #Checkpointing
    store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )
    with store as store:
        write_to_store(store, state['patient_name'], state['sub_graph'],
                    {'last_node': state["_current_node"], 'cataract_consultation':'pending', })



    return {**default_state, **state}






############################################
retina_prompt_ ="""

You are a Retina Specialist Agent.

Your role is to evaluate whether a patient’s visual symptoms are caused by retinal or optic nerve pathology.

You have access to the following tool:

1. retina_scan_test
   - Performs a retinal imaging examination (e.g., OCT / fundus scan).
   - Assesses the retina, macula, optic disc, and retinal nerve fiber layer.
   - Identifies retinal or neuro-retinal abnormalities, laterality, and severity.

             """




@tool("retina_scan_test")
def cataract_retina_test()-> Dict:
    """  Performs a retinal examination of each eye to assess the retina, macula, optic disc, and retinal vessels.
         Identifies retinal or optic nerve pathology, laterality, and severity based on structural abnormalities.
         Used to determine whether vision loss is retinal/neural in origin and to rule out non-lens 
         causes when cataract findings are inconclusive.
        """
    


    return patient_3_retina_conclusive 




retina_specialist_agent=create_agent(

    model=llm,
    tools=[cataract_retina_test],
    system_prompt=retina_prompt_
)



def retina_agent_function(state:PatientState):
    """
    Function that wraps the retina specialist agent   
    
    """
    time.sleep(2)
    retina_scan_response = cataract_retina_test.invoke({})
    retina_scan_status=retina_scan_response.get("retina_causative_of_vision_loss", "YES")

    if retina_scan_status=='NO':
        state['retina_scan_status']='normal'
        state['surgery_status']='halt'

        typewriter(f"""{blue_}Retina Agent. {white_} Observations ⬇️\n""")
        pprint.pprint(patient_3_retina_conclusive) 
        typewriter(f"""\n{white_} Analysing.........\n""")
        time.sleep(1)
                       
        typewriter(f"{blue_}Retina Agent: {white_} Retina Scans are normal, Routing to Neuro Opthamo Agent to diagnose nerve related issues  \n")

        print(f"{blue_}Retina Agent: {white_} Choose either '1' or '2' \n 1. Continue \n 2. End  \n")
        user_choice=input(f"{red_}User: {green_} ").strip()

        if user_choice=='2':
            state["intermediate_stop"]='yes'

            typewriter(f"{blue_}Retina Agent: {white_} Alright! Ending the Consultation ! Have a Good Day 😀 \n ")

        else:
            typewriter(f"{blue_}Retina Agent: {white_} Proceeding to Neuro Opto Specialist \n")



    else:
        state['retina_scan_status']='abnormal'
        
        
    #Checkpointing
    store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )
    with store as  store:
        write_to_store(store, state['patient_name'], state['sub_graph'],
                    {'last_node': state["_current_node"], 'cataract_consultation':'pending'})
   

    
    
   
    

    return {**default_state, **state}




######################################Neuro Optic Test#######3
neuro_opt_prompt_ ="""

You are a Neuro-Ophthalmology Specialist Agent.

Your role is to evaluate whether a patient’s visual symptoms are caused by optic nerve
or neuro-retinal pathology rather than lens or purely retinal disease.

You have access to the following tool:

1. oct_test
   - Performs Optical Coherence Tomography (OCT) imaging.
   - Assesses the optic nerve head, retinal nerve fiber layer (RNFL),
     ganglion cell layer (GCL), and macular structure.
   - Identifies neuro-retinal abnormalities, laterality (right eye, left eye, or both),
     and severity.

             """


@tool("oct_test")
def cataract_oct_test()-> Dict:
    """  Performs Optical Coherence Tomography (OCT) imaging of each eye to assess the retina, macula, optic disc, and retinal nerve fiber layer.
         Identifies retinal and optic nerve pathology, laterality, and severity based on high-resolution structural abnormalities.
         Used to determine whether vision loss is retinal or neuro-ophthalmic in origin and to rule out non-lens causes when cataract findings are inconclusive.
        """
    
    return patient_3_OCT_conclusive 



neuro_specialist_agent=create_agent(

    model=llm,
    tools=[cataract_oct_test],
    system_prompt=neuro_opt_prompt_
)


def neuro_opto_agent_function(state: PatientState):
    """
    Function that wraps the Neuro Opthamo specialist agent   
    
    """

    

    time.sleep(2)
    oct_response = cataract_oct_test.invoke({})
    oct_status=oct_response.get("nerve_pathology_suspected", "NO")
    

    if oct_status=="NO":
        state['neuro_opto_status']='normal'
        state['cataract_consultation']='completed'

        typewriter(f"""{blue_}Neuro Opto Agent. {white_} Observations ⬇️\n""")
        pprint.pprint(patient_3_OCT_conclusive ) 
        typewriter(f"""\n{white_} Analysing.........\n""")
        time.sleep(1)
        print(f"{blue_}Neuro Opto Agent: {white_} OCT Scan Test indicate NO Nerve related issues, routing to Finish Point \n")
        
    else:
        state['neuro_opto_status']='abnormal'
        

    #Checkpointing
    store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )
    with store as store:
        write_to_store(store, state['patient_name'], state['sub_graph'],
                    {'last_node': state["_current_node"], 'cataract_consultation':'completed'})

    
 

    return {**default_state, **state}
    
    

###########################################
def cataract_diagnosis_finish_point_function(state:PatientState):

    "Endnode of the Cataract Diagnosis Subgraph"
    
    time.sleep(2)
    #Final evaluation 
    

    if state['intermediate_stop']=='yes':

        typewriter(f"{green_}Cataract Diagnosis Finish Point: {white_} Your cataract consultation is Pending, Please complete the consultation to arrive at conclusion definitively \n")

       
        return None
    
    else:

        if (state['cataract_consultation']=='completed'):


   
            if state['surgery_status']=='halt':

                if (state['retina_scan_status']=='normal') and (state['neuro_opto_status']=='normal'):

                    state['surgery_status']='proceed'


            
            if state['surgery_status']=='proceed':
                typewriter(f"{green_}Cataract Diagnosis Finish Point: {white_} Cataract being the cause for Vision loss is confirmed, Proceed to Surgery!\n ")
                typewriter(f"{green_}Cataract Diagnosis Finish Point: {white_} Routing to Post Diagnosis stage\n\n")
                #Checkpointing
                store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )
                with store as store:
                    write_to_store(store, state['patient_name'], state['sub_graph'],
                            {'last_node': state["_current_node"], 'cataract_consultation':'completed'})


            
            else:
 

                print(f"{green_}Cataract Diagnosis Finish Point: {white_}Cataract being the cause or sole cause for Vision loss is NOT confirmed, Subsequent treatments are necesssary \n")


        
        return {**default_state, **state}





################build and Compile the Graph##################
diagnosis_subgraph = StateGraph(PatientState)


diagnosis_subgraph.add_node("cataract_diagnosis_start_point",  with_node_name("cataract_diagnosis_start_point", cataract_diagnosis_start_point))
diagnosis_subgraph.add_node("cataract_agent",  with_node_name("cataract_agent", cataract_agent_function))
diagnosis_subgraph.add_node("retina_agent",  with_node_name("retina_agent", retina_agent_function))
diagnosis_subgraph.add_node("neuro_opto_agent",  with_node_name("neuro_opto_agent", neuro_opto_agent_function))
diagnosis_subgraph.add_node("cataract_diagnosis_finish_point",  with_node_name("cataract_diagnosis_finish_point", cataract_diagnosis_finish_point_function))


diagnosis_subgraph.set_entry_point("cataract_diagnosis_start_point")

diagnosis_subgraph.add_conditional_edges(
    "cataract_diagnosis_start_point",
    route_resume_cataract_subgraph,
    {
        "start":"cataract_agent",
        "cataract_agent":"retina_agent",
        "retina_agent":"neuro_opto_agent",
        "neuro_opto_agent":"cataract_diagnosis_finish_point",
        "cataract_diagnosis_finish_point":"cataract_diagnosis_finish_point"

        
        
        

    }
)



diagnosis_subgraph.add_conditional_edges(
    "cataract_agent",
    route_cataract_subgraph,
    {
        
        "default":"cataract_diagnosis_finish_point",
        "proceed":"cataract_diagnosis_finish_point",
        "halt":"retina_agent"
        
        

    }
)


diagnosis_subgraph.add_conditional_edges(
    "retina_agent",
    route_cataract_subgraph,
    {
        
        "default":"cataract_diagnosis_finish_point",
        "proceed":"cataract_diagnosis_finish_point",
        "halt":"neuro_opto_agent"
        
        

    }
)



diagnosis_subgraph.add_edge("neuro_opto_agent", "cataract_diagnosis_finish_point")

diagnosis_subgraph.set_finish_point("cataract_diagnosis_finish_point")

cataract_diagnosis_subgraph= diagnosis_subgraph.compile()














    


     

    






