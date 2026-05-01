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

# why_template = PromptTemplate(
#     input_variables=["campaign", "roi", "roas", "cvr", "cpc"],
#     template="""You are a performance marketing expert. Your goal is to maximize ROI.
# Campaign: {campaign}
# Metrics: ROI {roi}%, ROAS {roas}x, CVR {cvr}%, CPC ${cpc}

# Explain in 2-3 sentences why this campaign is performing this way.
# Be specific about which metric is driving the result."""
# )

# next_steps_template = PromptTemplate(
#     input_variables=["campaign", "why", "roi", "roas", "cvr", "cpc"],
#     template="""You are a performance marketing expert.
# Campaign: {campaign}
# Metrics: ROI {roi}%, ROAS {roas}x, CVR {cvr}%, CPC ${cpc}
# Analysis: {why}

# Give 2-3 specific actions starting with action verbs (Increase, Reduce, Pause, Test, Shift)."""
# )

# why_chain        = why_template        | llm | StrOutputParser()
# next_steps_chain = next_steps_template | llm | StrOutputParser()

# # Chatbot
# chat_template = ChatPromptTemplate.from_messages([
#     ("system", """You are a performance marketing expert. 
# You have access to:
# 1. STRATEGIC OVERVIEW: {strategic_advice}
# 2. CAMPAIGN DATA: Detailed metrics for top and bottom campaigns. 

# {df_summary}

# Rules:
# - Only answer based on the data provided above
# - If asked about something not in the data, say "I don't have that data available"
# - Be specific — reference actual campaign names and numbers
# - Keep answers concise and actionable
# - If asked about budget reallocation, reference ROI and ROAS differences between campaigns"""),
#     ("human", "{question}")
# ])

# chat_chain = chat_template | llm | StrOutputParser()


# def df_to_summary(df: pd.DataFrame) -> str:
#     """
#     Converts the harmonized dataframe into a text summary
#     the LLM can reason over without hallucinating numbers.
#     """
#     lines = ["CAMPAIGN PERFORMANCE DATA:\n"]

#     for _, row in df.iterrows():
#         lines.append(
#             f"- {row['campaign']} ({row.get('platform', 'unknown')}): "
#             f"ROI {round(float(row['roi']), 2)}%, "
#             f"ROAS {round(float(row['roas']), 2)}x, "
#             f"CVR {round(float(row['cvr']), 2)}%, "
#             f"CPC ${round(float(row['cpc']), 2)}, "
#             f"Spend ${round(float(row['cost']), 2)}, "
#             f"Revenue ${round(float(row['revenue']), 2)}"
#         )

#     return "\n".join(lines)


# def ask_agent(question: str, df: pd.DataFrame, strategic_advice: str) -> str:
#     """
#     Takes a user question and the harmonized dataframe.
#     Takes the strategic advice from the analysis and the dataframe summary as 
#     context for the agent to answer the question.
#     """
#     df_summary = df_to_summary(df)

#     full_context = f"STRATEGIC OVERVIEW: {strategic_advice}\n\n{df_summary}"

#     return chat_chain.invoke({
#         "strategic_advice": strategic_advice,
#         "df_summary":      df_summary,
#         "question":        question,
#     })


# def generate_explanation(campaign: dict) -> dict:
#     metrics = {
#         "campaign": campaign["campaign"],
#         "roi":      round(float(campaign["roi"]),  2),
#         "roas":     round(float(campaign["roas"]), 2),
#         "cvr":      round(float(campaign["cvr"]),  2),
#         "cpc":      round(float(campaign["cpc"]),  2),
#     }

#     why        = why_chain.invoke(metrics)
#     next_steps = next_steps_chain.invoke({**metrics, "why": why})

#     return {
#         "campaign":   campaign["campaign"],
#         "roi":        campaign["roi"],
#         "why":        why,
#         "next_steps": next_steps,
#     }


# def generate_all_explanations(result: dict) -> list:
#     """
#     Accepts the result dict from run_analysis() directly.
#     Generates explanations only for top 3 and bottom 3 performing campaigns to avoid too many API calls.
#     """
#     # Get unique campaigns from top and bottom performers
#     top_campaigns = result["top_roi"].head(3).to_dict(orient="records")
#     bottom_campaigns = result["bottom_roi"].head(3).to_dict(orient="records")
    
#     # Combine and deduplicate by campaign name
#     all_campaigns = top_campaigns + bottom_campaigns
#     seen = set()
#     unique_campaigns = []
#     for camp in all_campaigns:
#         key = (camp["campaign"], camp["platform"])
#         if key not in seen:
#             seen.add(key)
#             unique_campaigns.append(camp)
    
#     explanations = []

#     for campaign in unique_campaigns:
#         print(f"Generating explanation for {campaign['campaign']} ({campaign['platform']})...")
#         explanations.append(generate_explanation(campaign))

#     return explanations

    # 3. Crear el Agente ReAct especializado en SQL
def get_sql_agent():
    db = SQLDatabase.from_uri(URL_DATABASE)
    custom_suffix = """
        IMPORTANT RULES FOR STRATEGIC ANALYSIS:
    
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
    # Este agente incluye herramientas como sql_db_query, sql_db_schema, etc.
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools", # Recomendado para modelos de OpenAI modernos
        verbose=True # Para que veas el Thought/Action/Observation en la terminal
    )
    return agent_executor