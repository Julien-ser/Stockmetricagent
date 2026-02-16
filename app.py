import streamlit as st
from agents import stock_agent
from tools import plot_stock_dashboard

st.set_page_config(page_title="Agentic Stock Dashboard", layout="wide")
st.title("Agentic Stock Dashboard")

st.write("Chat with the agent to generate stock insights, visualizations, and sentiment analysis. Ask about a specific stock, sector, or top stocks.")

user_query = st.chat_input("Ask about a stock, sector, or top stocks...")

if user_query:
    with st.spinner("Analyzing..."):
        try:
            print(f"\n[APP DEBUG] User query: {user_query}")
            agent_response, dashboard_data = stock_agent(user_query)
            print(f"[APP DEBUG] Agent response: {agent_response}")
            print(f"[APP DEBUG] Dashboard data: {dashboard_data}")
            if agent_response:
                st.markdown(f"**Agent:** {agent_response}")
            else:
                st.warning("No response from agent. Please check your OpenRouter API key in .env")
            if dashboard_data:
                plot_stock_dashboard(dashboard_data)
        except Exception as e:
            print(f"[APP DEBUG] Error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            st.error(f"Error: {str(e)}")
            st.write(f"Check your .env file and OpenRouter API key.")
