import os
from langchain_openai import ChatOpenAI
from tools import get_stock_metrics, get_sector_top_stocks, get_sentiment, get_deepseek_insight
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key-here")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")

# Set up OpenRouter LLM
llm = ChatOpenAI(
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    model_name=OPENROUTER_MODEL,
    temperature=0.7,
    extra_body={"reasoning_effort": "high"}
)

print(f"[DEBUG AGENT INIT] LLM model: {OPENROUTER_MODEL}")

def stock_agent(query):
    print(f"\n[DEBUG] stock_agent called with query: {query}")
    try:
        # Step 1: Use LLM to understand and extract what stocks/sectors user wants
        parse_prompt = f"""You are a financial analyst. Parse this user query and determine:
1. What stocks or sectors the user is asking about
2. What type of analysis they want (metrics, comparison, sentiment, etc.)

User query: "{query}"

Respond in JSON format:
{{
    "stocks": ["SYMBOL1", "SYMBOL2"],  # specific stock symbols if mentioned
    "sectors": ["sector1", "sector2"],  # sectors/industries mentioned
    "analysis_type": "metrics|comparison|sentiment|analysis",
    "interpretation": "brief description of what user wants"
}}

Be flexible - if they say "AI stocks", include relevant AI companies like NVDA, MSFT, GOOGL, etc.
If they say "compare tech stocks", extract multiple tech companies.
"""
        
        response = llm.invoke([
            {"role": "system", "content": "You are a financial analyst. Extract stocks and analysis type from user queries. Always respond with valid JSON."},
            {"role": "user", "content": parse_prompt}
        ])
        
        print(f"[DEBUG] LLM parse response: {response.content}")
        
        # Try to parse JSON from response
        try:
            # Extract JSON from response (might have extra text)
            json_str = response.content
            if '{' in json_str:
                json_str = json_str[json_str.index('{'):json_str.rindex('}')+1]
            parsed = json.loads(json_str)
        except:
            print(f"[DEBUG] Failed to parse JSON, using fallback")
            parsed = {"stocks": [], "sectors": [], "analysis_type": "metrics", "interpretation": "unknown"}
        
        stocks_to_fetch = parsed.get("stocks", [])
        sectors = parsed.get("sectors", [])
        analysis_type = parsed.get("analysis_type", "metrics")
        
        print(f"[DEBUG] Parsed - stocks: {stocks_to_fetch}, sectors: {sectors}, analysis: {analysis_type}")
        
        # Step 2: If sectors mentioned but no stocks, use LLM to suggest relevant stocks for those sectors
        if sectors and not stocks_to_fetch:
            sector_prompt = f"""What are the top 5 most relevant publicly traded stocks in these sectors: {', '.join(sectors)}?
Return ONLY stock symbols separated by commas, like: NVDA,MSFT,GOOGL,AMZN,META"""
            
            sector_response = llm.invoke([
                {"role": "user", "content": sector_prompt}
            ])
            
            sector_stocks = [s.strip().upper() for s in sector_response.content.split(',')]
            stocks_to_fetch.extend(sector_stocks)
            print(f"[DEBUG] LLM suggested stocks for sectors: {stocks_to_fetch}")
        
        # Step 3: Fetch data for all stocks
        stock_data_list = []
        summary = ""
        
        if stocks_to_fetch:
            for symbol in stocks_to_fetch[:5]:  # Limit to 5 stocks
                try:
                    symbol = symbol.strip().upper()
                    if not symbol:
                        continue
                    print(f"[DEBUG] Fetching metrics for {symbol}...")
                    metrics = get_stock_metrics(symbol)
                    if metrics:
                        stock_data_list.append(metrics)
                        print(f"[DEBUG] Got metrics for {symbol}")
                except Exception as e:
                    print(f"[DEBUG] Error fetching {symbol}: {e}")
            
            # Create a summary with the real data
            if stock_data_list:
                symbols = [s.get('Symbol', 'N/A') for s in stock_data_list]
                summary = f"Real-time stock data for {', '.join(symbols)}:\n\n"
                for data in stock_data_list:
                    if isinstance(data, dict):
                        symbol = data.get('Symbol', 'N/A')
                        summary += f"**{symbol}** ({data.get('Sector', 'N/A')})\n"
                        summary += f"- Price: ${data.get('Price', 'N/A')}\n"
                        if isinstance(data.get('Market Cap'), (int, float)):
                            summary += f"- Market Cap: ${data.get('Market Cap'):,.0f}\n"
                        summary += f"- Trailing PE: {data.get('Trailing PE', 'N/A')}\n"
                        summary += f"- Profit Margin: {data.get('Profit Margin', 'N/A')}\n"
                        summary += f"- Debt/Equity: {data.get('Debt/Equity', 'N/A')}\n\n"
            else:
                summary = "Could not fetch stock data. Please check your OpenRouter API key."
        else:
            summary = "Could not determine stocks from your query. Try asking about specific stocks (e.g., 'AAPL', 'MSFT') or sectors (e.g., 'AI stocks', 'tech companies')."
        
        print(f"[DEBUG] Final response: {summary}")
        return summary, stock_data_list if stock_data_list else None
    except Exception as e:
        print(f"[DEBUG] Error in stock_agent: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        return None, None
