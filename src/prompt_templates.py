from langchain_openai import ChatOpenAI
import pandas as pd
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.database import URL_DATABASE
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)


def get_sql_agent():
    db = SQLDatabase.from_uri(URL_DATABASE)
    custom_suffix = """You are NOT a SQL assistant. You are a STRATEGIC MARKETING ADVISOR. 
    Never just show a query. Your workflow MUST be:
    1. Search the database for the relevant data.
    2. Analyze the results using your OPTIMIZATION LOGIC.
    3. Provide a final answer in natural language with specific recommendations.
    
    1. MATHEMATICAL RIGOR:
       - Never use SUM(roi) or SUM(roas). Always use AVG(roi) or AVG(roas) to evaluate performance at a granular level.
       - To calculate Global ROI: (SUM(revenue) - SUM(cost)) / SUM(cost) * 100.
    
    2. STATISTICAL SIGNIFICANCE:
       - When asked for 'the best' or 'the worst' campaigns, always filter for campaigns with more than 10 conversions to avoid outliers.
    
    3. CROSS-PLATFORM COMPARISON (The Comparator):
       - When comparing Google vs Meta, group by the 'platform' column.
       - Always calculate the percentage difference between their CPAs or ROIs.
       - Example output: "Google's CPA is 15% lower than Meta's, but Meta's ROI is 10% higher."
    
    4. OPTIMIZATION LOGIC:
       - 'Budget savings' = Identify campaigns with high 'cost' and low 'roi'.
       - 'Scaling opportunities' = Identify campaigns with low 'cost' and high 'roi' (potential winners).
    """
  
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools", 
        verbose=True )
    return agent_executor