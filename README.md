# Agentic Stock Dashboard

A professional Streamlit app powered by LangChain agents. Users chat with an agent to generate stock insights, visualizations, and sentiment analysis. Modular, extensible, and ready for advanced workflows.

## Features
- Chat interface for stock queries
- Agentic workflows (LangChain)
- Dashboard insights and visualizations
- Sentiment analysis
- API integration (YahooQuery, DeepSeek, etc.)

## Setup
1. Activate the `stocks` venv
2. Install dependencies:
   - langchain
   - streamlit
   - yahooquery
   - plotly
   - vaderSentiment
   - requests

## Run
```
streamlit run app.py
```

## Structure
- app.py: Main Streamlit app
- agents.py: LangChain agent setup
- tools.py: Custom tools for stock analysis
- utils.py: Helper functions
