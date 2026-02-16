# Agentic Stock Dashboard

A professional Streamlit app powered by LangChain agents and OpenRouter API. Users chat with an intelligent agent to generate stock insights, visualizations, and sentiment analysis in real-time. Modular, extensible, and ready for advanced financial workflows.

## Features

- 💬 **Interactive Chat Interface** - Real-time Q&A for stock queries
- 🤖 **LangChain Agents** - Intelligent agentic workflows for complex analysis
- 📊 **Dynamic Dashboards** - Beautiful visualizations powered by Plotly
- 😊 **Sentiment Analysis** - Real-time sentiment scoring using VADER
- 🔗 **API Integration** - YahooQuery for stock data, OpenRouter for LLM
- 🏗️ **Modular Design** - Easily extensible tools and utilities

## Prerequisites

- Python 3.10+
- OpenRouter API key (for LLM access)
- Virtual environment (stocks venv included)

## Installation

1. **Activate the virtual environment:**
   ```powershell
   .\stocks\Scripts\activate
   ```

2. **Create a `.env` file** in the project root with your API keys:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

3. **Dependencies are pre-installed** in the venv. Core packages include:
   - `langchain` - Agent orchestration
   - `streamlit` - Web interface
   - `yahooquery` - Stock data
   - `plotly` - Visualizations
   - `vaderSentiment` - Sentiment analysis
   - `requests` - HTTP client

## Running the App

```powershell
streamlit run app.py
```

The app will launch at `http://localhost:8501`

## Project Structure

```
agentic_stock_dashboard/
├── app.py              # Main Streamlit application
├── agents.py           # LangChain agent configuration
├── tools.py            # Custom tools for stock analysis
├── utils.py            # Helper functions and utilities
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

### Key Files

- **app.py**: Main Streamlit entry point. Handles chat UI and agent orchestration
- **agents.py**: LangChain agent setup with tool bindings
- **tools.py**: Custom tools for stock analysis, data retrieval, and dashboard generation
- **utils.py**: Utility functions for data processing and formatting

## Usage

1. Start the app with `streamlit run app.py`
2. Enter queries about stocks, sectors, or market insights
3. The agent will analyze your query and return:
   - Text-based insights and analysis
   - Interactive dashboard visualizations
   - Sentiment analysis results

## Agents & Tools

### Core Agent: `stock_agent(query)`
The main LangChain agent that orchestrates all tools. It:
1. Parses user queries to extract stock symbols and analysis type
2. Suggests relevant stocks for sector queries using LLM
3. Fetches data and generates comprehensive insights
4. Returns formatted analysis with visualizations

### Tools Used by the Agent

#### 1. **get_stock_metrics(symbol)**
Fetches fundamental and valuation metrics for a stock using YahooQuery API.

**Returns:**
- Price, Market Cap, Enterprise Value
- PE Ratios (Trailing & Forward)
- Valuation ratios (Price/Sales, Price/Book, EV/Revenue, EV/Earnings)
- Profitability margins (Profit Margin, Operating Margin)
- Financial data (Revenue, Gross Profit, Debt, Debt/Equity)
- Ownership metrics (Insider %, Institution %, Payout Ratio, Dividend Yield)

#### 2. **get_sector_top_stocks(sector)**
Retrieves top stocks within a given sector. Used to identify leading companies in industry sectors when users query broad categories.

**Usage:** When user asks about sectors (e.g., "AI stocks", "Tech companies")

#### 3. **get_sentiment(symbol)**
Performs sentiment analysis on stock symbols using VADER (Valence Aware Dictionary and sEntiment Reasoner) from vaderSentiment library.

**Returns:** Sentiment scores indicating positive/negative/neutral sentiment around a stock

#### 4. **get_deepseek_insight(query)**
Placeholder for AI-powered insights (currently returns template response). Can be extended to call external insight APIs.

#### 5. **plot_stock_dashboard(stocks_data)**
Creates interactive visualizations for stock data using Plotly.

**Visualizations Generated:**
- **Key Metrics Table** - Formatted display of all stock metrics with appropriate units ($, %, decimals)
- **Valuation Radar Chart** - 5-axis radar chart comparing:
  - Dividend Yield (ideal: 5%+)
  - Operating Margin (ideal: 15-25%)
  - PE Ratio (ideal: 15-25)
  - Profit Margin (ideal: 15-25%)
  - Institution Ownership (ideal: 33-34%)

**Chart Features:**
- Mobile-optimized (350px height, responsive margins)
- Color-coded for visual appeal
- Real-world metric ranges for accurate scoring

## Example Queries

- "What are today's top performing stocks?"
- "Give me a technical analysis of AAPL"
- "What's the sentiment around Tesla stock?"
- "Compare NVIDIA vs AMD performance"

## Environment Variables

Create a `.env` file with:
- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)

**Note:** The `.env` file is in `.gitignore` to protect your API keys

## License

MIT License - Feel free to use and modify as needed
