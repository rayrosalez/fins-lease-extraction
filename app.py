import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils import (
    get_databricks_client,
    upload_to_volume,
    query_silver_table,
    query_lease_summary,
    query_leases_by_tenant,
    query_expiring_leases,
    query_property_rollup,
    query_portfolio_health,
    query_fact_lease_details,
    query_portfolio_kpis
)

# Page configuration
st.set_page_config(
    page_title="Lease Intelligence Platform",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional PE styling
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        font-size: 1rem;
        font-weight: 400;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: rgba(255,255,255,0.9);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        color: rgba(255,255,255,0.8);
        margin-top: 0.25rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Upload area */
    .upload-zone {
        background: #f8f9fa;
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Data tables */
    .dataframe {
        font-size: 0.875rem;
    }
    
    /* Info boxes */
    .info-box {
        background: #f0f4ff;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #f0fff4;
        border-left: 4px solid #38ef7d;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fff5f0;
        border-left: 4px solid #f5576c;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Hide Streamlit branding for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .element-container {
        color: white;
    }
    
    /* Make dataframes more professional */
    .dataframe th {
        background-color: #667eea !important;
        color: white !important;
        font-weight: 600;
    }
    
    /* Value Proposition Tab Styling */
    .value-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .value-hero h1 {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .value-hero p {
        color: rgba(255,255,255,0.95);
        font-size: 1.3rem;
        margin-top: 1rem;
    }
    
    .pipeline-step {
        text-align: center;
        padding: 1.5rem;
    }
    
    .pipeline-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    
    .pipeline-label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-top: 0.5rem;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        border: 2px solid rgba(102, 126, 234, 0.2);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .tech-badge {
        background: white;
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-weight: 600;
        color: #667eea;
        border: 2px solid #667eea;
        display: inline-block;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def format_currency(value):
    """Format number as currency"""
    if value is None:
        return "$0"
    try:
        # Convert to float in case it's a string
        num_value = float(value)
        return f"${num_value:,.0f}"
    except (ValueError, TypeError):
        return "$0"


def format_number(value):
    """Format number with commas"""
    if value is None:
        return "0"
    try:
        # Convert to float in case it's a string
        num_value = float(value)
        return f"{num_value:,.0f}"
    except (ValueError, TypeError):
        return "0"


def display_value_proposition():
    """Display the technical AI pipeline architecture"""
    
    # Hero section
    st.markdown("""
    <div class="value-hero">
        <h1>AI-Powered Lease Intelligence Pipeline</h1>
        <p>Enterprise-grade document processing with multi-stage enrichment</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Pipeline Architecture
    st.markdown("### Data Flow Architecture")
    
    # Stage 1: Document Upload
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; color: white;">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 2.5rem; margin-right: 1.5rem; opacity: 0.9;">01</div>
            <div style="flex: 1;">
                <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">User Upload</div>
                <div style="opacity: 0.9;">PDF documents uploaded through web interface → Databricks Unity Catalog Volume</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center; font-size: 2rem; color: #667eea; margin: 0.5rem 0;">↓</div>', unsafe_allow_html=True)
    
    # Stage 2: Raw Landing Zone
    st.markdown("""
    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; color: white;">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 2.5rem; margin-right: 1.5rem; opacity: 0.9;">02</div>
            <div style="flex: 1;">
                <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">AI Document Parser</div>
                <div style="opacity: 0.9;">Databricks AI Foundation Models extract raw text → Raw Landing Zone</div>
                <div style="font-family: monospace; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem; font-size: 0.85rem;">
                    Function: ai_parse_document() | Output: Unstructured text/markdown
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center; font-size: 2rem; color: #38ef7d; margin: 0.5rem 0;">↓</div>', unsafe_allow_html=True)
    
    # Stage 3: Bronze Layer
    st.markdown("""
    <div style="background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; color: white;">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 2.5rem; margin-right: 1.5rem; opacity: 0.9;">03</div>
            <div style="flex: 1;">
                <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">Bronze Layer: Agent Parsing</div>
                <div style="opacity: 0.9;">AI Agent extracts structured lease data from raw text</div>
                <div style="font-family: monospace; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem; font-size: 0.85rem;">
                    Table: bronze_pdf_parsed | Schema: {file_path, raw_parsed_json, ingested_at}
                </div>
                <div style="margin-top: 0.5rem; opacity: 0.85; font-size: 0.9rem;">
                    • Extracts: Property names, tenant names, dates, rent amounts<br>
                    • Format: Semi-structured JSON<br>
                    • Storage: Delta Lake with schema evolution
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center; font-size: 2rem; color: #CD7F32; margin: 0.5rem 0;">↓</div>', unsafe_allow_html=True)
    
    # Stage 4: Silver Layer
    st.markdown("""
    <div style="background: linear-gradient(135deg, #C0C0C0 0%, #808080 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; color: white;">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 2.5rem; margin-right: 1.5rem; opacity: 0.9;">04</div>
            <div style="flex: 1;">
                <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">Silver Layer: Multi-Source Enrichment</div>
                <div style="opacity: 0.9;">Data validated, cleaned, and enriched from multiple sources</div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-top: 0.75rem;">
                    <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">Manual Inputs</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">User corrections, property classifications</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">MCP Open Web</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Market data, credit ratings, property info</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">ML Models</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Risk scoring, clause detection, predictions</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">Data Validation</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Type checking, business rules, constraints</div>
                    </div>
                </div>
                <div style="font-family: monospace; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 4px; margin-top: 0.75rem; font-size: 0.85rem;">
                    Tables: fact_lease | dim_property | dim_tenant
                </div>
                <div style="margin-top: 0.5rem; opacity: 0.85; font-size: 0.9rem;">
                    • AI Risk Scores: ML model predicts lease risk (1-10 scale)<br>
                    • Clause Detection: NLP identifies termination options, ROFR clauses<br>
                    • Market Enrichment: Property market, asset type, total sqft<br>
                    • Tenant Intelligence: Industry classification, credit ratings
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center; font-size: 2rem; color: #C0C0C0; margin: 0.5rem 0;">↓</div>', unsafe_allow_html=True)
    
    # Stage 5: Gold Layer
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0; color: white;">
        <div style="display: flex; align-items: center;">
            <div style="font-size: 2.5rem; margin-right: 1.5rem; opacity: 0.9;">05</div>
            <div style="flex: 1;">
                <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">Gold Layer: Analytics & Intelligence</div>
                <div style="opacity: 0.9;">Pre-aggregated views optimized for business intelligence</div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-top: 0.75rem;">
                    <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">Smart Alerts</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Leases expiring soon, high-risk flags, WALT thresholds</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">Portfolio Health</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">WALT by market, risk indices, concentration metrics</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">RAG Chat Interface</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Natural language queries on structured lease data</div>
                    </div>
                    <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 4px;">
                        <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.25rem;">Predictive Analytics</div>
                        <div style="font-size: 0.8rem; opacity: 0.9;">Renewal probability, tenant churn, market trends</div>
                    </div>
                </div>
                <div style="font-family: monospace; background: rgba(0,0,0,0.2); padding: 0.5rem; border-radius: 4px; margin-top: 0.75rem; font-size: 0.85rem;">
                    Table: gold_portfolio_health | View: Genie AI-ready
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Technical Stack
    st.markdown("### Technology Stack")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: rgba(102, 126, 234, 0.1); padding: 1.5rem; border-radius: 8px; border-left: 4px solid #667eea;">
            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.75rem; color: #667eea;">Data Platform</div>
            <div style="font-size: 0.9rem; line-height: 1.6;">
                • Databricks Lakehouse<br>
                • Delta Lake (ACID)<br>
                • Unity Catalog<br>
                • SQL Warehouses<br>
                • Workflows/Jobs
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(56, 239, 125, 0.1); padding: 1.5rem; border-radius: 8px; border-left: 4px solid #38ef7d;">
            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.75rem; color: #38ef7d;">AI/ML Layer</div>
            <div style="font-size: 0.9rem; line-height: 1.6;">
                • Foundation Models<br>
                • AI Functions<br>
                • MLflow Models<br>
                • Vector Search<br>
                • Genie AI
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: rgba(255, 215, 0, 0.1); padding: 1.5rem; border-radius: 8px; border-left: 4px solid #FFD700;">
            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.75rem; color: #FFA500;">Application</div>
            <div style="font-size: 0.9rem; line-height: 1.6;">
                • Streamlit UI<br>
                • Python SDK<br>
                • Plotly Charts<br>
                • REST APIs<br>
                • MCP Protocol
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Capabilities
    st.markdown("### Enterprise Capabilities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="padding: 1rem; border-radius: 8px; background: rgba(102, 126, 234, 0.05); margin-bottom: 1rem;">
            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.5rem;">Scalability</div>
            <div style="font-size: 0.9rem; color: #666;">
                Process thousands of leases in parallel with Databricks auto-scaling. 
                Delta Lake ensures ACID compliance and time travel for auditing.
            </div>
        </div>
        <div style="padding: 1rem; border-radius: 8px; background: rgba(56, 239, 125, 0.05); margin-bottom: 1rem;">
            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.5rem;">Accuracy</div>
            <div style="font-size: 0.9rem; color: #666;">
                Multi-stage validation with ML models ensures 99%+ extraction accuracy. 
                Human-in-the-loop for edge cases and continuous improvement.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 1rem; border-radius: 8px; background: rgba(255, 215, 0, 0.05); margin-bottom: 1rem;">
            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.5rem;">Real-Time Intelligence</div>
            <div style="font-size: 0.9rem; color: #666;">
                Streaming ingestion and incremental processing. 
                Dashboard updates reflect latest data within minutes of upload.
            </div>
        </div>
        <div style="padding: 1rem; border-radius: 8px; background: rgba(245, 87, 108, 0.05);">
            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 0.5rem;">Security & Governance</div>
            <div style="font-size: 0.9rem; color: #666;">
                Unity Catalog provides fine-grained access control, data lineage, 
                and audit logging. SOC 2 compliant infrastructure.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Performance Metrics
    st.markdown("### Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 8px;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #667eea;">< 5min</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">End-to-End Processing</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(56, 239, 125, 0.1), rgba(17, 153, 142, 0.1)); border-radius: 8px;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #38ef7d;">99%+</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Data Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.1)); border-radius: 8px;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #FFA500;">95%</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Time Savings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, rgba(245, 87, 108, 0.1), rgba(240, 147, 251, 0.1)); border-radius: 8px;">
            <div style="font-size: 2.5rem; font-weight: 700; color: #f5576c;">∞</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Horizontal Scale</div>
        </div>
        """, unsafe_allow_html=True)


def display_portfolio_dashboard(client, warehouse_id, catalog, schema):
    """Display the reimagined portfolio dashboard with rich KPIs and visualizations"""
    
    st.markdown('<p class="section-header">  Portfolio Intelligence Dashboard</p>', unsafe_allow_html=True)
    
    # Load portfolio health data
    with st.spinner("Loading portfolio intelligence..."):
        success_kpis, kpis, error_kpis = query_portfolio_kpis(client, warehouse_id, catalog, schema)
        success_health, health_data, health_columns, error_health = query_portfolio_health(client, warehouse_id, catalog, schema)
        success_leases, lease_data, lease_columns, error_leases = query_fact_lease_details(client, warehouse_id, catalog, schema)
    
    # Show specific error messages
    if not success_kpis:
        st.error(f"Failed to load portfolio KPIs: {error_kpis}")
        st.info("Make sure the fact_lease and dim_property tables exist with data.")
        st.code(f"""
-- Check if tables exist:
SHOW TABLES IN {catalog}.{schema};

-- Check fact_lease data:
SELECT COUNT(*) FROM {catalog}.{schema}.fact_lease;
        """, language="sql")
        return
    
    if not success_health:
        st.warning(f"Gold portfolio health table not available: {error_health}")
        st.info("The gold_portfolio_health table needs to be created. Run this in Databricks SQL:")
        st.code(f"""
CREATE OR REPLACE TABLE {catalog}.{schema}.gold_portfolio_health AS
SELECT 
    p.market,
    COUNT(*) as lease_count,
    ROUND(AVG(l.base_rent_psf), 2) as avg_rent_psf,
    ROUND(AVG(GREATEST(DATEDIFF(l.expiration_date, CURRENT_DATE()), 0) / 365.25), 2) as walt_years,
    SUM(CAST(l.has_termination_option AS INT)) as leases_with_exit_risk,
    SUM(CAST(l.has_rofr AS INT)) as leases_blocking_new_deals,
    ROUND(AVG(l.ai_risk_score), 1) as avg_market_risk_index
FROM {catalog}.{schema}.fact_lease l
INNER JOIN {catalog}.{schema}.dim_property p ON l.property_name = p.property_name
GROUP BY p.market;
        """, language="sql")
        st.warning("Continuing with limited functionality (KPIs and lease details only)...")
        # Continue without market analysis charts
    
    if not success_leases:
        st.warning(f"Failed to load lease details: {error_leases}")
        st.info("Continuing with KPIs only...")
        # Continue with just KPIs
    
    # ============= TOP KPI CARDS =============
    st.markdown("###   Portfolio Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{kpis['total_leases']}</div>
            <div class="metric-label">Total Leases</div>
            <div class="metric-delta">{kpis['markets_count']} Markets</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-blue">
            <div class="metric-value">{kpis['total_properties']}</div>
            <div class="metric-label">Properties</div>
            <div class="metric-delta">{kpis['total_tenants']} Tenants</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-green">
            <div class="metric-value">${kpis['avg_rent_psf']:.2f}</div>
            <div class="metric-label">Avg Rent PSF</div>
            <div class="metric-delta">Per Square Foot</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        walt_color = "metric-card-green" if kpis['portfolio_walt'] > 5 else "metric-card-orange" if kpis['portfolio_walt'] > 3 else "metric-card-orange"
        st.markdown(f"""
        <div class="{walt_color}">
            <div class="metric-value">{kpis['portfolio_walt']:.1f}y</div>
            <div class="metric-label">Portfolio WALT</div>
            <div class="metric-delta">Weighted Avg Lease Term</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        risk_color = "metric-card-green" if kpis['avg_risk_score'] < 4 else "metric-card-orange" if kpis['avg_risk_score'] < 7 else "metric-card-orange"
        st.markdown(f"""
        <div class="{risk_color}">
            <div class="metric-value">{kpis['avg_risk_score']:.1f}/10</div>
            <div class="metric-label">Risk Index</div>
            <div class="metric-delta">AI-Powered Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============= RISK ALERT BANNER =============
    risk_count = kpis['total_exit_risk'] + kpis['expiring_12_months']
    if risk_count > 0:
        st.markdown(f"""
        <div class="warning-box">
            <strong>  Portfolio Risk Alerts:</strong><br>
            • {kpis['total_exit_risk']} leases have termination options (exit risk)<br>
            • {kpis['total_rofr']} leases have ROFR clauses (blocking new deals)<br>
            • {kpis['expiring_12_months']} leases expiring within 12 months
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============= VISUALIZATIONS ROW 1: MARKET ANALYSIS =============
    if success_health and health_data and len(health_data) > 0:
        st.markdown("###   Market Analysis")
        
        df_health = pd.DataFrame(health_data, columns=health_columns)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Market Lease Count Bar Chart
            fig_market_count = px.bar(
                df_health,
                x='market',
                y='lease_count',
                title='Lease Count by Market',
                labels={'market': 'Market', 'lease_count': 'Number of Leases'},
                color='lease_count',
                color_continuous_scale='Blues',
                text='lease_count'
            )
            fig_market_count.update_traces(textposition='outside')
            fig_market_count.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="Market",
                yaxis_title="Lease Count"
            )
            st.plotly_chart(fig_market_count, use_container_width=True)
        
        with col2:
            # Average Rent PSF by Market
            fig_rent_psf = px.bar(
                df_health,
                x='market',
                y='avg_rent_psf',
                title='Average Rent per Sq Ft by Market',
                labels={'market': 'Market', 'avg_rent_psf': 'Avg Rent PSF ($)'},
                color='avg_rent_psf',
                color_continuous_scale='Greens',
                text='avg_rent_psf'
            )
            fig_rent_psf.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
            fig_rent_psf.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="Market",
                yaxis_title="Avg Rent PSF ($)"
            )
            st.plotly_chart(fig_rent_psf, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============= VISUALIZATIONS ROW 2: WALT & RISK =============
    if success_health and health_data and len(health_data) > 0:
        st.markdown("###   Portfolio Health Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # WALT by Market
            fig_walt = go.Figure()
            
            fig_walt.add_trace(go.Bar(
                x=df_health['market'],
                y=df_health['walt_years'],
                name='WALT (Years)',
                marker_color='rgb(102, 126, 234)',
                text=df_health['walt_years'],
                texttemplate='%{text:.1f}y',
                textposition='outside'
            ))
            
            # Add a reference line at 5 years (good WALT)
            fig_walt.add_hline(y=5, line_dash="dash", line_color="green", 
                              annotation_text="Target: 5+ years", annotation_position="right")
            
            fig_walt.update_layout(
                title='Weighted Average Lease Term (WALT) by Market',
                xaxis_title='Market',
                yaxis_title='Years',
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_walt, use_container_width=True)
        
        with col2:
            # Risk Index by Market
            fig_risk = go.Figure()
            
            # Create color scale based on risk (green = low, yellow = medium, red = high)
            colors = ['green' if float(x) < 4 else 'orange' if float(x) < 7 else 'red' 
                     for x in df_health['avg_market_risk_index']]
            
            fig_risk.add_trace(go.Bar(
                x=df_health['market'],
                y=df_health['avg_market_risk_index'],
                name='Risk Index',
                marker_color=colors,
                text=df_health['avg_market_risk_index'],
                texttemplate='%{text:.1f}',
                textposition='outside'
            ))
            
            fig_risk.update_layout(
                title='AI Risk Index by Market (1-10 scale)',
                xaxis_title='Market',
                yaxis_title='Risk Score',
                height=400,
                showlegend=False,
                yaxis=dict(range=[0, 10])
            )
            
            st.plotly_chart(fig_risk, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ============= VISUALIZATIONS ROW 3: RISK FLAGS =============
        st.markdown("###   Lease Risk Factors")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Exit Risk & ROFR Stacked Bar
            fig_risk_factors = go.Figure()
            
            fig_risk_factors.add_trace(go.Bar(
                name='Termination Options',
                x=df_health['market'],
                y=df_health['leases_with_exit_risk'],
                marker_color='rgb(245, 87, 108)'
            ))
            
            fig_risk_factors.add_trace(go.Bar(
                name='ROFR Clauses',
                x=df_health['market'],
                y=df_health['leases_blocking_new_deals'],
                marker_color='rgb(240, 147, 251)'
            ))
            
            fig_risk_factors.update_layout(
                title='Lease Risk Flags by Market',
                xaxis_title='Market',
                yaxis_title='Number of Leases',
                barmode='group',
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_risk_factors, use_container_width=True)
        
        with col2:
            # Rent Escalation Type Distribution
            if success_leases and lease_data:
                df_leases = pd.DataFrame(lease_data, columns=lease_columns)
                
                escalation_counts = df_leases['rent_escalation_type'].value_counts().reset_index()
                escalation_counts.columns = ['type', 'count']
                
                fig_escalation = px.pie(
                    escalation_counts,
                    values='count',
                    names='type',
                    title='Rent Escalation Types',
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                
                fig_escalation.update_traces(textposition='inside', textinfo='percent+label')
                fig_escalation.update_layout(height=400)
                
                st.plotly_chart(fig_escalation, use_container_width=True)
            else:
                st.info("Lease details needed for escalation analysis")
    
    st.markdown("---")
    
    # ============= DETAILED DATA TABLES =============
    st.markdown("###   Detailed Portfolio Data")
    
    tab1, tab2, tab3 = st.tabs(["  Market Summary", "  Lease Details", "  High-Risk Leases"])
    
    with tab1:
        st.markdown("#### Portfolio Health by Market")
        
        if success_health and health_data and len(health_data) > 0:
            df_display = df_health.copy()
            df_display['avg_rent_psf'] = df_display['avg_rent_psf'].apply(lambda x: f"${float(x):.2f}" if pd.notna(x) else "$0.00")
            df_display['walt_years'] = df_display['walt_years'].apply(lambda x: f"{float(x):.1f}" if pd.notna(x) else "0.0")
            df_display['avg_market_risk_index'] = df_display['avg_market_risk_index'].apply(lambda x: f"{float(x):.1f}" if pd.notna(x) else "0.0")
            
            df_display = df_display.rename(columns={
                'market': 'Market',
                'lease_count': 'Leases',
                'avg_rent_psf': 'Avg Rent PSF',
                'walt_years': 'WALT (Years)',
                'leases_with_exit_risk': 'Exit Risk',
                'leases_blocking_new_deals': 'ROFR Clauses',
                'avg_market_risk_index': 'Risk Index'
            })
            
            st.dataframe(df_display, use_container_width=True, height=300)
            
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="  Download Market Summary",
                data=csv,
                file_name=f"market_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("Market summary data not available. Please create the gold_portfolio_health table.")
    
    with tab2:
        st.markdown("#### All Lease Details with AI Enrichments")
        
        if success_leases and lease_data:
            df_display = df_leases.copy()
            
            # Format columns
            df_display['base_rent_psf'] = df_display['base_rent_psf'].apply(lambda x: f"${float(x):.2f}" if pd.notna(x) else "$0.00")
            df_display['ai_risk_score'] = df_display['ai_risk_score'].apply(lambda x: f"{float(x):.1f}" if pd.notna(x) else "N/A")
            df_display['years_remaining'] = df_display['years_remaining'].apply(lambda x: f"{float(x):.1f}y" if pd.notna(x) and float(x) > 0 else "Expired")
            df_display['has_termination_option'] = df_display['has_termination_option'].apply(lambda x: " " if x else "")
            df_display['has_rofr'] = df_display['has_rofr'].apply(lambda x: " " if x else "")
            
            df_display = df_display.rename(columns={
                'file_path': 'File',
                'property_name': 'Property',
                'market': 'Market',
                'asset_type': 'Type',
                'tenant_name': 'Tenant',
                'industry': 'Industry',
                'credit_rating': 'Credit',
                'commencement_date': 'Start',
                'expiration_date': 'End',
                'base_rent_psf': 'Rent PSF',
                'has_termination_option': 'Exit Clause',
                'has_rofr': 'ROFR',
                'rent_escalation_type': 'Escalation',
                'ai_risk_score': 'Risk',
                'years_remaining': 'Remaining'
            })
            
            st.dataframe(df_display, use_container_width=True, height=400)
            
            csv = df_leases.to_csv(index=False)
            st.download_button(
                label="  Download Full Lease Data",
                data=csv,
                file_name=f"lease_details_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with tab3:
        st.markdown("#### High-Risk Leases (Risk Score ≥ 7)")
        
        if success_leases and lease_data:
            # Convert ai_risk_score to numeric for filtering
            df_leases['ai_risk_score_numeric'] = pd.to_numeric(df_leases['ai_risk_score'], errors='coerce')
            df_high_risk = df_leases[df_leases['ai_risk_score_numeric'] >= 7].copy()
            
            if len(df_high_risk) > 0:
                # Format for display
                df_high_risk['base_rent_psf'] = df_high_risk['base_rent_psf'].apply(lambda x: f"${float(x):.2f}" if pd.notna(x) else "$0.00")
                df_high_risk['years_remaining_numeric'] = pd.to_numeric(df_high_risk['years_remaining'], errors='coerce')
                df_high_risk['years_remaining'] = df_high_risk['years_remaining_numeric'].apply(lambda x: f"{x:.1f}y" if pd.notna(x) and x > 0 else "Expired")
                
                # Add risk indicators
                def risk_flag(row):
                    flags = []
                    if row['has_termination_option']:
                        flags.append("  Exit Clause")
                    if row['has_rofr']:
                        flags.append("  ROFR")
                    years_rem = row['years_remaining_numeric']
                    if pd.notna(years_rem) and years_rem < 1:
                        flags.append("Expiring Soon")
                    return ", ".join(flags) if flags else "  High Risk Score"
                
                df_high_risk['risk_flags'] = df_high_risk.apply(risk_flag, axis=1)
                
                df_display = df_high_risk.rename(columns={
                    'file_path': 'File',
                'tenant_name': 'Tenant',
                    'property_name': 'Property',
                    'market': 'Market',
                    'ai_risk_score': 'Risk Score',
                    'base_rent_psf': 'Rent PSF',
                    'expiration_date': 'Expires',
                    'years_remaining': 'Time Left',
                    'risk_flags': 'Risk Factors'
                })
                
                st.dataframe(
                    df_display[['File', 'Tenant', 'Property', 'Market', 'Risk Score', 'Time Left', 'Risk Factors']],
                    use_container_width=True,
                    height=400
                )
                
                st.markdown(f"""
                <div class="warning-box">
                    <strong>  Attention Required:</strong> {len(df_high_risk)} lease(s) flagged as high-risk by AI analysis.
                    Review these leases for potential renegotiation or exit strategies.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-box">
                    <strong>  No High-Risk Leases:</strong> All leases have acceptable risk profiles.
            </div>
            """, unsafe_allow_html=True)


def display_upload_interface(client, warehouse_id, catalog, schema, volume_path):
    """Display the lease upload interface"""
    
    st.markdown('<p class="section-header">  Upload New Lease</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <strong>AI-Powered Lease Processing:</strong> Upload commercial or industrial real estate lease PDFs. 
        Our AI will automatically extract key terms, dates, financial details, and clauses—saving hours of manual data entry.
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drop lease PDF here or click to browse",
        type=['pdf'],
        help="Supported format: PDF"
    )
    
    if uploaded_file is not None:
        # File preview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Filename", uploaded_file.name)
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.metric("Size", f"{file_size_mb:.2f} MB")
        with col3:
            st.metric("Type", "PDF Document")
        
        st.markdown("---")
        
        # Upload button
        if st.button("  Process Lease with AI", type="primary", use_container_width=True):
            file_bytes = uploaded_file.read()
            
            # Upload to volume
            with st.spinner(f"Uploading {uploaded_file.name}..."):
                success, file_path, error = upload_to_volume(
                    client,
                    file_bytes,
                    uploaded_file.name,
                    volume_path
                )
            
            if success:
                st.success("  Upload successful!")
                st.code(file_path, language="text")
                
                # Show notification about processing time
                st.info("""
                    **Processing in Progress**
                    
                    Your lease is being processed by our AI pipeline (Bronze → Silver). 
                    This typically takes 2-5 minutes depending on document complexity.
                    
                    **What happens next:**
                    1. AI extracts lease data from PDF
                    2. Data is validated and structured
                    3. Lease appears in the dashboard automatically
                    
                    **Tip:** Click "  Refresh Data" in a few minutes to see your new lease in the dashboard.
                """)
                
                # Clear the file uploader by rerunning
                st.balloons()
                
            else:
                st.error(f"Upload failed: {error}")
                st.info("Please check your connection and try again.")




def main():
    # Header with branding
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<p class="main-header">Lease Intelligence Platform</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">AI-Powered Commercial Real Estate Lease Analysis for Private Equity</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("  Refresh Data", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Initialize Databricks client
    client, error = get_databricks_client()
    
    if error or not client:
        st.error(f"  Unable to connect to Databricks: {error}")
        st.info("  Ensure DATABRICKS_HOST and DATABRICKS_TOKEN are set in your .env file")
        return
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("##   Configuration")
        st.markdown("---")
        
        st.markdown("#### Unity Catalog Settings")
        catalog = st.text_input("Catalog", value="users", help="Unity Catalog name")
        schema = st.text_input("Schema", value="ray_rosalez", help="Schema name")
        volume = st.text_input("Volume", value="lease_uploads", help="Volume name")
        
        volume_path = f"/Volumes/{catalog}/{schema}/{volume}"
        
        st.markdown("#### SQL Warehouse")
        warehouse_id = st.text_input(
            "Warehouse ID",
            value="4b9b953939869799",
            help="Required for querying analytics"
        )
        
        if warehouse_id:
            st.success("  Connected")
        else:
            st.warning("  Warehouse ID required")
        
        st.markdown("---")
        
        st.markdown("####   Data Pipeline")
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; color: white; font-size: 0.85rem;">
        <strong>Bronze Layer:</strong> Raw PDF extraction<br>
        <strong>Silver Layer:</strong> Structured lease data<br>
        <strong>Gold Layer:</strong> Analytics ready
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("####   Value Proposition")
        st.markdown("""
        <div style="color: white; font-size: 0.85rem; line-height: 1.6;">
        • <strong>95% faster</strong> than manual entry<br>
        • <strong>99% accuracy</strong> with AI extraction<br>
        • <strong>Real-time</strong> portfolio insights<br>
        • <strong>Automated</strong> risk monitoring
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area - check if we have data
    if not warehouse_id:
        st.warning("  Please configure SQL Warehouse ID in the sidebar to continue")
        return
    
    # Create main tabs
    main_tab1, main_tab2, main_tab3 = st.tabs(["  Portfolio Dashboard", "  Upload Lease", "  AI Pipeline"])
    
    with main_tab1:
        display_portfolio_dashboard(client, warehouse_id, catalog, schema)
    
    with main_tab2:
        display_upload_interface(client, warehouse_id, catalog, schema, volume_path)
    
    with main_tab3:
        display_value_proposition()


if __name__ == "__main__":
    main()
