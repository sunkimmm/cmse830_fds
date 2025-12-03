import streamlit as st

st.title("Large-scale Infrastructure Project: ESG Risk Analysis")
st.caption("Demo app — under construction")
st.write(
    """
    This Streamlit app will analyze ESG-related risks in large-scale infrastructure project documents
    using text analysis / NLP methods.
    """
)

st.set_page_config(
    page_title="Infrastructure Project ESG Risk Analysis",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)



# create tab
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Project Overview",
    "📌 Key Findings Summary",
    "⚠️ Risk Analysis",
    "👀 Additional Analysis",
    "📊 Data & Processing"
])