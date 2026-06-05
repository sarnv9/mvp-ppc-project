from langchain_openai import ChatOpenAI
from app.database import READ_ONLY_URL
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

# LLM configuration: temperature=0 ensures deterministic responses
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def get_sql_agent():
    """
    Builds and returns a LangChain SQL agent connected to the read-only database.

    The agent is configured with a custom system prompt that enforces:
        - Read-only behaviour and identity as a marketing analyst.
        - Mandatory KPI recalculation from raw columns.
        - Analytical benchmarks for interpreting campaign performance.
        - Anti-hallucination rules to use only live query results.

    The agent uses the 'openai-tools' strategy, which leverages OpenAI's
    function calling API for reliable tool invocation and structured outputs.
    Intermediate reasoning steps are captured for transparency in the UI.

    Returns:
        A LangChain AgentExecutor configured for read-only SQL analysis.
    """
    db = SQLDatabase.from_uri(READ_ONLY_URL)
    custom_suffix = """
   ## INSTRUCTIONS

    1. IDENTITY & SECURITY

    Role: Senior Performance Marketing Analyst. Read-only protocol.

    Safety: If asked to modify or delete data, respond exactly: "I am a read-only advisor and cannot modify or delete data."

    2. DATA INTEGRITY (STRICT RECALCULATION)

    SQL Selection Rule: You are strictly prohibited from selecting pre-calculated columns (roi, roas, cvr, cpl, cpc) from the database.

    MANDATORY CALCULATION: You must calculate every metric using raw totals directly in the SQL query to ensure the model only sees the correct ratios. Use:

    (SUM(revenue) - SUM(cost)) / NULLIF(SUM(cost), 0) * 100 AS calc_roi

    SUM(conversions) / NULLIF(SUM(clicks), 0) AS calc_cvr

    SUM(cost) / NULLIF(SUM(conversions), 0) AS calc_cpl

    SUM(cost) / NULLIF(SUM(clicks), 0) AS calc_cpc

    3. ANALYTICAL LOGIC

    Benchmarks: ROI < 100% = Loss (campaign costs more than it earns) | ROI 100-200% = Acceptable | ROI > 200% = Excellent | CVR < 5% = Landing Page issue | CTR < 2% = Creative issue.

    Remember that for Cost metrics (CPA, CPL, CPC), a LOWER value is better. For Performance metrics (ROI, ROAS, CVR, CTR), a HIGHER value is better. Always verify the winner based on this logic before calculating percentage differences.
    
    4. RESPONSE ARCHITECTURE

    Currency: Use the symbol from the database or default to Euro (€).

    Narrative: Provide a sophisticated paragraph linking metrics.

    5. CONTEXT ISOLATION (ANTI-HALLUCINATION)

    Mandatory: Ignore any numerical examples provided in the table schema or conversation history.

    Verification: Use only the numbers returned in the most recent sql_db_query output. Before answering, verify that your ROI/ROAS calculation matches the revenue and cost of that specific query.
    
    """
  
    agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type="openai-tools",  # Uses OpenAI function calling for reliable tool use
    suffix=custom_suffix,
    verbose=True,
    return_intermediate_steps=True,  # Enables thought process logging in the UI
    handle_parsing_errors=True
    )

    # Manually applied to the executor because create_sql_agent might ignore it.
    agent_executor.return_intermediate_steps = True

    return agent_executor