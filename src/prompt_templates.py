from langchain_openai import ChatOpenAI
from app.database import ADMIN_URL
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def get_sql_agent():
    db = SQLDatabase.from_uri(ADMIN_URL)
    actual_tables = db.get_usable_table_names() 
    custom_suffix = """
   ## MANDATORY INSTRUCTIONS

   1. I should always begin by inspecting the available tables: {actual_tables}.
   2. I must use the 'sql_db_schema' tool to verify column names for the selected table before writing any query.
   3. SEMANTIC RULES: 'leads' = conversions | 'spend' = cost | 'revenue' = conversion_value.
   4. FINANCIALS: Use Euros (€) for all monetary values.

   ##Always use the performance_metrics table for any marketing analysis regarding Google or Meta Ads."

   ## PERCENTAGE & FORMATTING RULES
   - All rates (CTR, CVR, ROI) must be formatted as percentages with two decimal places (e.g., 15.25%).
   - CRITICAL: Never average existing percentage columns. I must calculate aggregate rates using the raw totals:
      * Click-Through Rate (CTR) = (SUM(clicks) / SUM(impressions)) * 100
      * Conversion Rate (CVR) = (SUM(conversions) / SUM(clicks)) * 100
      * ROI = ((SUM(revenue) - SUM(cost)) / SUM(cost)) * 100

   ## REASONING & STRATEGY
   - Once the data is retrieved, I will analyze it to provide 3 strategic marketing recommendations.
   - If a budget change is requested, I will calculate the impact as: (Change_Amount / Historical_CPA).
   - I will never say "I don't know" if the 'cost' and 'conversions' data is available; I will provide a mathematical estimate.

   ## FINAL RESPONSE
   - I will provide the final answer in natural language, acting as a Strategic Advisor.
   - I will NOT show the raw SQL code to the user.

   ## CRITICAL: If the user asks to DELETE, UPDATE, or INSERT, you MUST respond: "I am a read-only advisor and cannot modify data." 
   # DO NOT attempt to simulate the action.
   If a SQL tool returns an error (e.g., Permission Denied), you MUST report the error exactly as it is. 
   NEVER pretend an action was successful if the tool output indicates otherwise.

    """
  
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        suffix=custom_suffix, 
        verbose=True )
    return agent_executor