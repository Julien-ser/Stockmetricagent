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

def get_stock_metrics(symbol):
    try:
        ticker = yahooquery.Ticker(symbol)
        summary = ticker.summary_detail.get(symbol, {})
        profile = ticker.asset_profile.get(symbol, {})
        financial = ticker.financial_data.get(symbol, {})
        stats = ticker.key_stats.get(symbol, {})
        data = {
            'Symbol': symbol.upper(),
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
        return filtered_data
    except Exception as e:
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
                    # Invert PE: lower is better, so 1/PE scaled to 0-100
                    if isinstance(val, (int, float)) and val is not None and val > 0:
                        radar_values.append(min(100 / val, 100))
                    else:
                        radar_values.append(0)
                elif metric == 'Institution %':
                    # Bell curve: sweet spot 10-30%, lower outside this range
                    if isinstance(val, (int, float)) and val is not None:
                        pct = val * 100 if val < 1 else val
                        if 10 <= pct <= 30:
                            score = 100
                        elif pct < 10:
                            score = (pct / 10) * 100
                        else:  # pct > 30
                            score = max(0, 100 * (1 - (pct - 30) / 70))
                        radar_values.append(score)
                    else:
                        radar_values.append(0)
                #if the metric is dividend yield, make 10% the higher amount since they don't go to high
                elif metric == 'Dividend Yield':
                    if isinstance(val, (int, float)) and val is not None and val > 0:
                        radar_values.append(min(val * 1000, 100))
                    else:
                        radar_values.append(0)
                else:
                    # Operating Margin, Profit Margin
                    if isinstance(val, (int, float)) and val is not None and val > 0:
                        radar_values.append(min(val * 100, 100))
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
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()

