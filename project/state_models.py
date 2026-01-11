from typing import *
from langchain_aws import ChatBedrock
from langgraph.checkpoint.postgres import PostgresSaver

from langgraph.store.postgres import PostgresStore
from langgraph.store.base import BaseStore
from typing import *



################


user_name='langgraph_user'
user_password='langgraph_password'
database_DB='langgraph_DB'

###############


class PatientState(TypedDict):

    patient_name:str
    suggestion:str
    


    #fields related to Cataract Subgraph
    
    slit_test_status:Literal["certain", "uncertain"]
    visual_test_status:Literal["certain", "uncertain"]
    retina_scan_status:Literal["normal", "abnormal"]
    neuro_opto_status:Literal["normal", "abnormal"]
    surgery_status:Literal["proceed", "halt", 'default']

    
    sub_graph:str
    cataract_consultation:Literal["pending", "completed"]
    intermediate_stop:Literal['yes', 'no']
    resumption_node:str

    _current_node:str


    ### Fields realted to Post Diagnosis Subgraph
    blood_test_status:Literal["normal", "abnormal"]
    ecg_test_status:Literal["normal", "abnormal"]
    final_status:Literal["normal", "abnormal"]
    surgery_route_status:Literal["yes", "no"]
    surgery_recommendation:Literal["normal", "abnormal"]

    

    counselling_agent_flag:Literal["0", "1"]

    patient_condition:Dict
    resume:bool

    


  



default_state={

    'patient_name':'',
    'suggestion':"Ophthalmologist",
    
    
    "slit_test_status":"uncertain",
    "visual_test_status":"uncertain",
    "retina_scan_status":"normal",
    "neuro_opto_status":"normal",
    'surgery_status':"halt",

    
    'sub_graph':'cataract_diagnosis',
    "cataract_consultation":'completed',
    'intermediate_stop':'no',
    'resumption_node':'cataract_agent',
    

    "_current_node":'',


    'blood_test_status':'normal',
    'ecg_test_status':'normal',
    'final_status':'normal',
    'surgery_route_status':'no',
    'surgery_recommendation':'normal',

    'counselling_agent_flag':'0',
    
    

    'patient_condition':{},
    'resume':False

    
}
    

##############################
llm = ChatBedrock(
    model_id="amazon.nova-pro-v1:0",
    
)

"""

For OpenAI, set API key in terminal and then use the below syntax

llm = ChatOpenAI(
    model="gpt-4.1-mini",   
    temperature=0.7
)

"""


####################
def with_node_name(node_name, fn):
    def wrapper(state, *args, **kwargs):
        state["_current_node"] = node_name
        return fn(state, *args, **kwargs)
    return wrapper




#########################
import sys
import time

def typewriter(text, delay=0.025):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)


def typewriter_fast(text, delay=0.005):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)


############### Command line colors #######################
# blue_ = "\033[34m"
blue_ = "\033[94m"
red_ = "\033[91m"
white_="\033[97m"
green_="\033[92m"
