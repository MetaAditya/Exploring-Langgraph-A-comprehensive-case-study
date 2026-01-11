###Create Virtual Environment ###########
python3 -m venv venv
pip install -r requirements.txt

###################

#################Database configuration

1) You need to install Potgresql on your machine 
    sudo apt install postgresql-17


2) Follow the below steps to configure the database
   
      
CREATE ROLE langgraph_user WITH LOGIN PASSWORD 'langgraph_password';
ALTER ROLE langgraph_user CREATEDB;



psql -U langgraph_user -d langgraph_DB -h 127.0.0.1 -W
langgraph_password

CREATE DATABASE "langgraph_DB";
ALTER DATABASE "langgraph_DB" OWNER TO langgraph_user;



-- Delete the table if it already exists
DROP TABLE IF EXISTS store;

-- Recreate the table with the correct schema
CREATE TABLE store (
    prefix TEXT NOT NULL,
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    ttl_minutes INTEGER,
    PRIMARY KEY (prefix, key)
);

--------------------------------------------------------------
In here I have created using the following details
user_name='langgraph_user'
user_password='langgraph_password'
database_DB='langgraph_DB'

If you use different nomenclature, make necessary changes in project/state_models.py



################LLM Related Changes ###################3

In the file project/state_models.py , I have used AWS Nova Pro LLM.
If you want to use OpenAI (ChatOpenAI) , just make changes here by using model of your choice and providing api key
However if you want to ahead with AWS LLM, you need to do 'aws configure' on your terminal too.


#########Launch the application ################
python3 graph_agent.py




###############################################################################################################################################################
Project Details

1)
The project has three distinct components
a) Main graph (graph_agent.py)
b) Cataract Diagnosis Subgraph (diagnosis_determine_subgraph.py)
c) Post Diagnosis Subgraph (post_diagnosis_subgraph.py)

2) For the Main graph agent definitions are in misc_agents.py

3) The necessary data to simulate responses are in patient_data.py

4) The global variable definitions are in state_models.py