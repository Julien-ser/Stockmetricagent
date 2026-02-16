import yahooquery
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
import streamlit as st
import plotly.graph_objects as go

# Key indicators to preserve
INDICATORS = [
    'Symbol', 'Price', 'Sector', 'Market Cap', 'Enterprise Value', 'Dividend Yield',
    'Trailing PE', 'Forward PE', 'Price/Sales', 'Price/Book', 'EV/Revenue', 'EV/Earnings',
    'Profit Margin', 'Operating Margin', 'Revenue', 'Gross Profit', 'Debt', 'Debt/Equity',
    'Insider %', 'Institution %', 'Payout Ratio'
]

# Regional stock suffixes
REGIONAL_SUFFIXES = [
    '.TO',  # Toronto Stock Exchange (Canada)
    '.V',   # TSX Venture Exchange (Canada)
    '.NS',  # NSE (India)
    '.BO',  # BSE (India)
    '.L',   # London Stock Exchange (UK)
    '.HK',  # Hong Kong Stock Exchange
    '.TW',  # Taiwan Stock Exchange
    '.ST',  # Nasdaq Stockholm (Sweden)
    '.AX',  # Australian Securities Exchange
    '.NZ',  # New Zealand Stock Exchange
    '.SG',  # Singapore Exchange
    '.KL',  # Bursa Malaysia
]

def resolve_regional_stock_symbol(symbol):
    """
    Attempts to resolve a stock symbol by trying regional suffixes.
    Returns the resolved symbol if found, otherwise returns the original symbol.
    Also returns whether it was auto-resolved for UI feedback.
    """
    symbol = symbol.strip().upper()
    
    # First, check if the symbol as entered works
    try:
        ticker = yahooquery.Ticker(symbol)
        financial = ticker.financial_data.get(symbol, {})
        # Check if we actually got valid data (dict with keys, not empty or string)
        if isinstance(financial, dict) and financial and 'currentPrice' in financial:
            return symbol, False  # Symbol found as-is
    except Exception as e:
        print(f"[DEBUG RESOLVE] Failed to resolve {symbol} as-is: {e}")
        pass
    
    # Try adding regional suffixes
    for suffix in REGIONAL_SUFFIXES:
        try:
            test_symbol = symbol + suffix
            ticker = yahooquery.Ticker(test_symbol)
            financial = ticker.financial_data.get(test_symbol, {})
            # Check if we actually got valid data (dict with keys, not empty or string)
            if isinstance(financial, dict) and financial and 'currentPrice' in financial:
                print(f"[DEBUG RESOLVE] Found {test_symbol} with suffix {suffix}")
                return test_symbol, True  # Symbol found with suffix
        except Exception as e:
            print(f"[DEBUG RESOLVE] Failed to resolve {symbol}{suffix}: {e}")
            continue
    
    # If no regional variant found, return the original symbol
    print(f"[DEBUG RESOLVE] Could not resolve {symbol} with any suffix, returning original")
    return symbol, False

def get_stock_metrics(symbol):
    try:
        # Resolve regional stock symbol
        resolved_symbol, was_auto_resolved = resolve_regional_stock_symbol(symbol)
        print(f"[DEBUG GET_METRICS] Using symbol: {resolved_symbol}, auto_resolved: {was_auto_resolved}")
        
        ticker = yahooquery.Ticker(resolved_symbol)
        summary = ticker.summary_detail.get(resolved_symbol, {})
        profile = ticker.asset_profile.get(resolved_symbol, {})
        financial = ticker.financial_data.get(resolved_symbol, {})
        stats = ticker.key_stats.get(resolved_symbol, {})
        
        # Validate data types
        if not isinstance(summary, dict):
            summary = {}
        if not isinstance(profile, dict):
            profile = {}
        if not isinstance(financial, dict):
            financial = {}
        if not isinstance(stats, dict):
            stats = {}
        
        print(f"[DEBUG GET_METRICS] Got data - summary: {bool(summary)}, profile: {bool(profile)}, financial: {bool(financial)}")
        
        data = {
            'Symbol': resolved_symbol.upper(),
            'Price': financial.get('currentPrice'),
            'Sector': profile.get('sector', 'N/A'),
            'Market Cap': summary.get('marketCap'),
            'Enterprise Value': stats.get('enterpriseValue'),
            'Trailing PE': summary.get('trailingPE'),
            'Forward PE': summary.get('forwardPE'),
            'Price/Sales': summary.get('priceToSalesTrailing12Months'),
            'Price/Book': stats.get('bookValue'),
            'EV/Revenue': stats.get('enterpriseValue')/financial.get('totalRevenue') if financial.get('totalRevenue') else None,
            'EV/Earnings': stats.get('enterpriseValue')/financial.get('ebitda') if financial.get('ebitda') else None,
            'Profit Margin': financial.get('profitMargins'),
            'Operating Margin': financial.get('operatingMargins'),
            'Revenue': financial.get('totalRevenue'),
            'Gross Profit': financial.get('grossProfits'),
            'Debt': financial.get('totalDebt'),
            'Debt/Equity': financial.get('debtToEquity'),
            'Insider %': stats.get('heldPercentInsiders'),
            'Institution %': stats.get('heldPercentInstitutions'),
            'Payout Ratio': summary.get('payoutRatio'),
            'Dividend Yield': summary.get('dividendYield')
        }
        filtered_data = {k: data.get(k) for k in INDICATORS}
        print(f"[DEBUG GET_METRICS] Returning data for {resolved_symbol}")
        return filtered_data
    except Exception as e:
        print(f"[DEBUG TOOLS] Error in get_stock_metrics for {symbol}: {str(e)}")
        import traceback
        print(f"[DEBUG TOOLS] Traceback: {traceback.format_exc()}")
        return None

def get_sector_top_stocks(sector):
    try:
        # Return formatted string about sector
        return f"Top stocks in {sector} sector: This would require a sector screener. Common {sector.lower()} stocks include industry leaders in that sector."  
    except Exception as e:
        return f"Error fetching sector data: {str(e)}"

def get_sentiment(symbol):
    try:
        analyzer = SentimentIntensityAnalyzer()
        sentiment_result = analyzer.polarity_scores(symbol)
        return f"Sentiment analysis for {symbol}: {sentiment_result}"  
    except Exception as e:
        return f"Error analyzing sentiment: {str(e)}"

def get_deepseek_insight(query):
    try:
        # Placeholder: call DeepSeek API
        return f"Insight for {query}: Based on the data available, this shows market conditions. Use the stock metrics tool for detailed analysis."  
    except Exception as e:
        return f"Error generating insight: {str(e)}"

def plot_stock_dashboard(stocks_data):
    if not stocks_data:
        st.warning("No stock data to display")
        return
    
    if isinstance(stocks_data, dict):
        stocks_data = [stocks_data]
    
    for stock in stocks_data:
        if not stock:
            continue
        
        st.subheader(f"{stock.get('Symbol', 'N/A')} - {stock.get('Sector', 'N/A')}")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**Key Metrics**")
            display_data = {}
            for k, v in stock.items():
                if v is None:
                    display_data[k] = 'N/A'
                elif isinstance(v, float):
                    if k in ['Price', 'Market Cap', 'Enterprise Value', 'Revenue', 'Gross Profit', 'Debt']:
                        display_data[k] = f"${v:,.0f}" if v > 1000 else f"${v:.2f}"
                    elif k in ['Profit Margin', 'Operating Margin', 'Dividend Yield', 'Insider %', 'Institution %', 'Payout Ratio']:
                        display_data[k] = f"{v:.2%}"
                    else:
                        display_data[k] = f"{v:.2f}"
                else:
                    display_data[k] = v
            st.table(display_data)
        
        with col2:
            st.write("**Valuation Radar**")
            radar_metrics = ['Dividend Yield', 'Operating Margin', 'Trailing PE', 'Profit Margin', 'Institution %']
            radar_display = ['Dividend Yield', 'Operating Margin', 'PE Ratio', 'Profit Margin', 'Institution %']
            radar_values = []
            
            for metric in radar_metrics:
                val = stock.get(metric)
                
                if metric == 'Trailing PE':
                    # PE Ratio: lower is better, use inverse ratio 10/PE
                    if isinstance(val, (int, float)) and val is not None and val > 0:
                        score = min((10 / val) * 100, 100)
                        radar_values.append(score)
                    else:
                        radar_values.append(0)
                elif metric == 'Institution %':
                    # Institution ownership: optimal 33-34%, real range 0-95%
                    if isinstance(val, (int, float)) and val is not None:
                        pct = val * 100 if val < 1 else val
                        if pct < 33:
                            score = (pct / 33) * 100  # 0-33% maps to 0-100
                        elif pct <= 34:
                            score = 100  # 33-34% is optimal
                        else:  # pct > 34
                            score = max(0, 100 - ((pct - 34) / 61) * 100)  # 34-95% declining
                        radar_values.append(score)
                    else:
                        radar_values.append(0)
                elif metric == 'Dividend Yield':
                    # Dividend Yield: over 5% is optimal (100), scales down from there
                    if isinstance(val, (int, float)) and val is not None and val >= 0:
                        dividend_pct = val * 100 if val < 1 else val
                        if dividend_pct >= 5:
                            score = 100  # Over 5% is ideal
                        else:  # 0-5%
                            score = (dividend_pct / 5) * 100  # scales from 0 to 100
                        radar_values.append(score)
                    else:
                        radar_values.append(0)
                else:
                    # Operating Margin & Profit Margin: optimal 15-25%, realistic 5-35%
                    if isinstance(val, (int, float)) and val is not None and val > 0:
                        margin_pct = val * 100 if val < 1 else val
                        if margin_pct <= 15:
                            score = (margin_pct / 15) * 100
                        elif margin_pct <= 25:
                            score = 100
                        else:  # 25-35%
                            score = max(0, 100 - ((margin_pct - 25) / 10) * 20)
                        radar_values.append(score)
                    else:
                        radar_values.append(0)
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=radar_values,
                theta=radar_display,
                fill='toself',
                name=stock.get('Symbol', 'Stock'),
                line_color='rgb(0, 100, 200)',
                fillcolor='rgba(0, 100, 200, 0.3)'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                title=f"Radar - {stock.get('Symbol', 'N/A')}",
                height=350,
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()

