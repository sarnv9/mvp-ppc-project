# PPC Ads AI Advisor
This repository contains the source code for the PPC Ads AI Advisor, an Agentic AI system designed to transform raw marketing data into strategic business intelligence using the ReAct (Reason + Act) framework.

## Project Overview
This tool automates the analysis of Google and Meta Ads campaigns. It utilizes a Text-to-SQL engine to interact with a PostgreSQL database, providing deterministic visualizations and high-level strategic recommendations.

## Tech Stack
* **Language:** Python 3.11+
* **Orchestration:** LangChain (ReAct Agent Executor)
* **LLM Backend:** GPT-4o mini (via OpenAI API)
* **Database:** PostgreSQL (with SQLAlchemy ORM)
* **API Layer:** FastAPI
* **Frontend:** Streamlit & Plotly

## Project Structure
```text
├── app/
│   ├── api.py               # FastAPI backend endpoints
│   ├── schemas.py           # Pydantic data models for API validation
│   └── database/            # Database connection and engine setup
├── src/
│   ├── prompt_templates.py  # ReAct agent logic and tool configuration
│   └── harmonize/           # Data harmonization, types casting (Float/Int), and ETL scripts
├── data/                    # Marketing datasets (CSV)
├── .env.example             # Template for environment variables (DB URLs, API Keys)
├── requirements.txt         # Project dependencies (pip freeze)
├── streamlit_app.py         # Streamlit interface and dynamic chat UI
└── README.md                # Project documentation
```

## Setup and Installation
Prerequisites
Python 3.11+

PostgreSQL instance

OpenAI API Key

## Installation
### Clone the repository:  

git clone https://github.com/sarnv9/mvp-ppc-project.git  

### Create a virtual environment:  

python -m venv venv  

source venv/bin/activate  # On Windows: venv\Scripts\activate  

### Install dependencies:  

pip install -r requirements.txt  

### Environment Variables Configuration:  

Duplicate the .env.example file, rename it to .env, and populate it with your local credentials:  

ADMIN_DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@localhost:5432/your_database_name  

READ_ONLY_DATABASE_URL=postgresql://your_readonly_user:your_readonly_password@localhost:5432/your_database_name  

OPENAI_API_KEY=your_openai_api_key_here  

API_URL=http://127.0.0.1:8000  

## Usage
Launch the Backend (FastAPI)

uvicorn app.api:app --reload

Launch the Frontend (Streamlit)

streamlit run main.py

## Evaluation Framework
This project was evaluated using the Marketing Agent Benchmark (MAB) across five dimensions:

Task Completion

Business Impact

Compliance (SQL Read-Only & ZDR)

Strategic Reasoning

Efficiency