# PPC Ads AI Advisor: Agentic Decision Support System
This repository contains the source code for the PPC Ads AI Advisor, an Agentic AI system designed to transform raw marketing data into strategic business intelligence using the ReAct (Reason + Act) framework.

## Project Overview
This tool automates the analysis of Google and Meta Ads campaigns. It utilizes a Text-to-SQL engine to interact with a PostgreSQL database, providing deterministic visualizations and high-level strategic recommendations.

## Tech Stack
Language: Python 3.11

Orchestration: LangChain (ReAct Agent)

LLM Backend: GPT-4o mini (via OpenAI API)

Database: PostgreSQL (with SQLAlchemy ORM)

Frontend: Streamlit & Plotly

## Project Structure
```text
├── api
│   ├── database/            # SQLAlchemy models and DB connection
├── src/
│   ├── prompt_templates/    # ReAct logic and custom prompts
│   ├── database/            # SQLAlchemy models and DB connection
│   ├── harmonize/           # Data harmonization and cleaning scripts         
├── data/                    # Synthetic marketing datasets (CSV)
├── .env.example             # Template for environment variables
├── requirements.txt         # Project dependencies
├── streamlit_app            # Streamlit interface and visualizations

## Setup and Installation
Prerequisites
Python 3.11+

PostgreSQL instance

OpenAI API Key

Installation
Clone the repository:

git clone https://github.com/sarnv9/mvp-ppc-project.git

Create a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt


## Usage
To launch the dashboard and the AI Agent:

streamlit run main.py

## Evaluation Framework
This project was evaluated using the Marketing Agent Benchmark (MAB) across five dimensions:

Task Completion

Business Impact

Compliance (SQL Read-Only & ZDR)

Strategic Reasoning

Efficiency