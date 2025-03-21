import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time
import io
import base64
from PIL import Image
import os

# Set page configuration
st.set_page_config(
    page_title="GGTC Marketing Compliance Review Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 20px;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .highlight {
        background-color: #F0F7FF;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #4B73B6;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .status-pending {
        color: #FFA500;
        font-weight: bold;
    }
    .status-approved {
        color: #008000;
        font-weight: bold;
    }
    .status-rejected {
        color: #FF0000;
        font-weight: bold;
    }
    .status-review {
        color: #0000FF;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio("", ["Dashboard", "Submit Request", "Review Queue", "Historical Data", "Settings"], index=0)

# Sample data generation functions
def generate_sample_data():
    # Create sample submission data
    current_date = datetime.now()
    dates = [(current_date - timedelta(days=random.randint(0, 120))).strftime("%Y-%m-%d") 
             for _ in range(300)]
    
    material_types = ["Whitepaper", "Blog Post", "Email", "Social Post", "Webpage", 
                     "Video", "Podcast", "Presentation", "PR Article"]
    
    sources = ["Corporate Marketing", "Third Party", "RFP/RFI Response"]
    
    statuses = ["Pending", "In Review", "Approved", "Rejected", "Needs Revision"]
    status_weights = [0.1, 0.2, 0.5, 0.1, 0.1]
    
    reviewers = ["Amanda H.", "Michael T.", "Sarah L.", "David R.", "Jessica W."]
    
    # Generate sample data
    data = {
        "submission_id": [f"SUB-{2024}-{i:04d}" for i in range(1, 301)],
        "title": [f"Marketing Material {i}" for i in range(1, 301)],
        "submission_date": dates,
        "material_type": random.choices(material_types, k=300),
        "source": random.choices(sources, weights=[0.4, 0.4, 0.2], k=300),
        "status": random.choices(statuses, weights=status_weights, k=300),
        "page_count": [random.randint(1, 60) for _ in range(300)],
        "assigned_to": [random.choice(reviewers) if s != "Pending" else None 
                        for s in random.choices(statuses, weights=status_weights, k=300)],
        "review_date": [
            (datetime.strptime(d, "%Y-%m-%d") + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d") 
            if random.random() > 0.3 else None for d in dates
        ],
        "compliance_score": [random.randint(70, 100) if random.random() > 0.2 else 
                            random.randint(40, 69) for _ in range(300)],
        "flags": [random.randint(0, 5) for _ in range(300)],
        "review_time_hours": [round(random.uniform(0.5, 8.0), 1) if random.random() > 0.3 else None 
                             for _ in range(300)]
    }
    
    return pd.DataFrame(data)

def generate_requirements():
    requirements = {
        "General": [
            "No misleading statements about product performance",
            "Clear disclosure of fees and expenses",
            "No promises of specific returns",
            "Balanced presentation of risks and benefits",
            "No guarantees of future performance",
            "Appropriate disclaimers included",
            "Compliant with regulatory guidelines"
        ],
        "Third Party": [
            "Clear attribution of source",
            "Written permission obtained",
            "No alteration of original content meaning",
            "Compliant with GGTC co-branding guidelines",
            "Dated within last 12 months"
        ],
        "Corporate Marketing": [
            "Approved by department head",
            "Compliant with brand guidelines",
            "Contains required legal disclaimers",
            "Referenced data is current and accurate",
            "Appropriate for target audience"
        ],
        "RFP/RFI Response": [
            "All statements factually accurate",
            "Product capabilities accurately represented",
            "No forward-looking statements without disclaimers",
            "Claims supported by documentation",
            "All metrics and statistics verified"
        ]
    }
    return requirements

# Initialize session state variables
if 'data' not in st.session_state:
    st.session_state.data = generate_sample_data()

if 'requirements' not in st.session_state:
    st.session_state.requirements = generate_requirements()

if 'current_id' not in st.session_state:
    max_id = int(st.session_state.data['submission_id'].str.split('-').str[2].max())
    st.session_state.current_id = max_id + 1

# Dashboard Page
if page == "Dashboard":
    st.markdown("<div class='main-header'>Marketing Compliance Review Dashboard</div>", unsafe_allow_html=True)
    
    # Filter data for metrics
    today = datetime.now()
    last_3q = today - timedelta(days=90)
    last_4q = today - timedelta(days=120)
    year_start = datetime(today.year, 1, 1)
    
    df = st.session_state.data
    
    df['submission_date'] = pd.to_datetime(df['submission_date'])
    
    # Period filters for metrics
    df_3q = df[df['submission_date'] >= last_3q]
    df_4q = df[(df['submission_date'] >= last_4q) & (df['submission_date'] < last_3q)]
    df_jan = df[(df['submission_date'] >= year_start) & (df['submission_date'] < year_start + timedelta(days=31))]
    df_feb = df[(df['submission_date'] >= year_start + timedelta(days=31)) & 
                (df['submission_date'] < year_start + timedelta(days=59))]
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Submissions", len(df), f"{len(df) - len(df[df['submission_date'] < last_3q])}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        pending = len(df[df['status'].isin(['Pending', 'In Review'])])
        st.metric("Pending Reviews", pending, f"{pending - len(df_4q[df_4q['status'].isin(['Pending', 'In Review'])])}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        avg_time = df[df['review_time_hours'].notna()]['review_time_hours'].mean()
        st.metric("Avg. Review Time (hrs)", f"{avg_time:.1f}", 
                 f"{avg_time - df_4q[df_4q['review_time_hours'].notna()]['review_time_hours'].mean():.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        compliance = len(df[df['compliance_score'] >= 80]) / len(df) * 100 if len(df) > 0 else 0
        st.metric("Compliance Rate", f"{compliance:.1f}%", 
                 f"{compliance - len(df_4q[df_4q['compliance_score'] >= 80]) / len(df_4q) * 100 if len(df_4q) > 0 else 0:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Create tabs for different metric views
    tab1, tab2, tab3 = st.tabs(["Volume Metrics", "Compliance Trends", "Review Efficiency"])
    
    with tab1:
        st.markdown("<div class='sub-header'>Material Volume Trends</div>", unsafe_allow_html=True)
        
        # Third Party Material Volume by Page
        third_party = df[df['source'] == 'Third Party']
        
        # Calculate averages per period
        tp_3q_pages = third_party[third_party['submission_date'] >= last_3q]['page_count'].sum() // 3
        tp_4q_pages = third_party[(third_party['submission_date'] >= last_4q) & 
                                (third_party['submission_date'] < last_3q)]['page_count'].sum() // 3
        tp_jan_pages = third_party[(third_party['submission_date'] >= year_start) & 
                                 (third_party['submission_date'] < year_start + timedelta(days=31))]['page_count'].sum()
        tp_feb_pages = third_party[(third_party['submission_date'] >= year_start + timedelta(days=31)) & 
                                 (third_party['submission_date'] < year_start + timedelta(days=59))]['page_count'].sum()
        
        # Create bar chart
        fig1 = go.Figure(data=[
            go.Bar(
                x=['3Q 2024 AVG*', '4Q 2024 AVG*', 'JAN 2025', 'FEB 2025*'],
                y=[tp_3q_pages, tp_4q_pages, tp_jan_pages, tp_feb_pages],
                marker_color='#63C5DA'
            )
        ])
        
        fig1.update_layout(
            title='Third Party Material - Volume by Page',
            xaxis_title='Time Period',
            yaxis_title='Count',
            height=400
        )
        
        # Third Party Material Volume by Piece & Video
        tp_3q_pieces = len(third_party[third_party['submission_date'] >= last_3q]) // 3
        tp_4q_pieces = len(third_party[(third_party['submission_date'] >= last_4q) & 
                                     (third_party['submission_date'] < last_3q)]) // 3
        tp_jan_pieces = len(third_party[(third_party['submission_date'] >= year_start) & 
                                      (third_party['submission_date'] < year_start + timedelta(days=31))])
        tp_feb_pieces = len(third_party[(third_party['submission_date'] >= year_start + timedelta(days=31)) & 
                                      (third_party['submission_date'] < year_start + timedelta(days=59))])
        
        tp_3q_videos = len(third_party[(third_party['submission_date'] >= last_3q) & 
                                     (third_party['material_type'] == 'Video')]) // 3
        tp_4q_videos = len(third_party[(third_party['submission_date'] >= last_4q) & 
                                     (third_party['submission_date'] < last_3q) & 
                                     (third_party['material_type'] == 'Video')]) // 3
        tp_jan_videos = len(third_party[(third_party['submission_date'] >= year_start) & 
                                      (third_party['submission_date'] < year_start + timedelta(days=31)) & 
                                      (third_party['material_type'] == 'Video')])
        tp_feb_videos = len(third_party[(third_party['submission_date'] >= year_start + timedelta(days=31)) & 
                                      (third_party['submission_date'] < year_start + timedelta(days=59)) & 
                                      (third_party['material_type'] == 'Video')])
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=['3Q 2024 AVG*', '4Q 2024 AVG*', 'JAN 2025', 'FEB 2025*'],
            y=[tp_3q_pieces, tp_4q_pieces, tp_jan_pieces, tp_feb_pieces],
            name='Pieces',
            marker_color='#90EE90'
        ))
        
        fig2.add_trace(go.Bar(
            x=['3Q 2024 AVG*', '4Q 2024 AVG*', 'JAN 2025', 'FEB 2025*'],
            y=[tp_3q_videos, tp_4q_videos, tp_jan_videos, tp_feb_videos],
            name='Videos',
            marker_color='#FFA07A'
        ))
        
        fig2.update_layout(
            title='Third Party Material - Volume by Piece & Video',
            xaxis_title='Time Period',
            yaxis_title='Count',
            barmode='group',
            height=400
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig2, use_container_width=True)
        
        # Corporate Marketing Table
        st.markdown("<div class='sub-header'>Corporate Marketing Content Volume</div>", unsafe_allow_html=True)
        
        corp_marketing = df[df['source'] == 'Corporate Marketing']
        
        # Calculate metrics by material type
        material_types = ['Whitepaper', 'Blog Post', 'Email', 'Social Post', 'Webpage', 
                         'Video', 'Podcast', 'Presentation']
        
        marketing_data = {
            'TIME PERIOD': ['3Q 2024 AVG*', '4Q 2024 AVG*', 'JAN 2025', 'FEB 2025*'],
        }
        
        # Material type mapping to display names
        material_map = {
            'Whitepaper': 'WHITEPAPERS/E-BOOKS',
            'Blog Post': 'BLOGS & PR ARTICLES',
            'PR Article': 'BLOGS & PR ARTICLES',
            'Email': 'EMAILS',
            'Social Post': 'SOCIAL POSTS',
            'Webpage': 'WEBPAGES',
            'Video': 'VIDEOS',
            'Podcast': 'PODCASTS/MEDIA',
            'Presentation': 'PRESENTATIONS'
        }
        
        # Initialize counters for combined categories
        for display_name in set(material_map.values()):
            marketing_data[display_name] = [0, 0, 0, 0]
        
        # Count by material type and period
        for i, (material, display) in enumerate(material_map.items()):
            cm_3q = len(corp_marketing[(corp_marketing['submission_date'] >= last_3q) & 
                                     (corp_marketing['material_type'] == material)]) // 3
            cm_4q = len(corp_marketing[(corp_marketing['submission_date'] >= last_4q) & 
                                     (corp_marketing['submission_date'] < last_3q) & 
                                     (corp_marketing['material_type'] == material)]) // 3
            cm_jan = len(corp_marketing[(corp_marketing['submission_date'] >= year_start) & 
                                      (corp_marketing['submission_date'] < year_start + timedelta(days=31)) & 
                                      (corp_marketing['material_type'] == material)])
            cm_feb = len(corp_marketing[(corp_marketing['submission_date'] >= year_start + timedelta(days=31)) & 
                                      (corp_marketing['submission_date'] < year_start + timedelta(days=59)) & 
                                      (corp_marketing['material_type'] == material)])
            
            # Add to the combined category
            marketing_data[display][0] += cm_3q
            marketing_data[display][1] += cm_4q
            marketing_data[display][2] += cm_jan
            marketing_data[display][3] += cm_feb
        
        # Calculate totals
        marketing_data['TOTAL'] = [sum(marketing_data[key][i] for key in marketing_data.keys() if key != 'TIME PERIOD')
                                 for i in range(4)]
        
        # Create DataFrame for display
        cm_df = pd.DataFrame(marketing_data)
        
        # RFP/RFI Response Team data
        rfp_response = df[df['source'] == 'RFP/RFI Response']
        
        rfp_data = {
            'TIME PERIOD': ['3Q 2024 AVG*', '4Q 2024 AVG*', 'JAN 2025', 'FEB 2025*'],
            'PAGES': [
                rfp_response[rfp_response['submission_date'] >= last_3q]['page_count'].sum() // 3,
                rfp_response[(rfp_response['submission_date'] >= last_4q) & 
                           (rfp_response['submission_date'] < last_3q)]['page_count'].sum() // 3,
                rfp_response[(rfp_response['submission_date'] >= year_start) & 
                           (rfp_response['submission_date'] < year_start + timedelta(days=31))]['page_count'].sum(),
                rfp_response[(rfp_response['submission_date'] >= year_start + timedelta(days=31)) & 
                           (rfp_response['submission_date'] < year_start + timedelta(days=59))]['page_count'].sum()
            ],
            'QUESTIONS': [
                len(rfp_response[rfp_response['submission_date'] >= last_3q]) * 5 // 3,  # Estimating questions
                len(rfp_response[(rfp_response['submission_date'] >= last_4q) & 
                               (rfp_response['submission_date'] < last_3q)]) * 4 // 3,
                0,  # January data
                len(rfp_response[(rfp_response['submission_date'] >= year_start + timedelta(days=31)) & 
                               (rfp_response['submission_date'] < year_start + timedelta(days=59))]) * 3
            ]
        }
        
        rfp_df = pd.DataFrame(rfp_data)
        
        # Display tables
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div style='text-align: center; font-weight: bold; font-size: 1.2em; color: #1E3A8A; margin-bottom: 10px;'>CORPORATE MARKETING</div>", unsafe_allow_html=True)
            st.dataframe(cm_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("<div style='text-align: center; font-weight: bold; font-size: 1.2em; color: #1E3A8A; margin-bottom: 10px;'>RFP/RFI RESPONSE TEAM</div>", unsafe_allow_html=True)
            st.dataframe(rfp_df, use_container_width=True, hide_index=True)
            st.markdown("<div style='text-align: right; font-style: italic; font-size: 0.8em;'>* Monthly Averages</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='sub-header'>Compliance Trends</div>", unsafe_allow_html=True)
        
        # Average monthly trend
        fig_trend = go.Figure()
        
        # Calculate totals for each period
        periods = ['3Q 2024 AVG*', '4Q 2024 AVG*', 'JAN 2025', 'FEB 2025*']
        
        # Calculate pieces
        pieces_data = [
            len(df[df['submission_date'] >= last_3q]) // 3,
            len(df[(df['submission_date'] >= last_4q) & (df['submission_date'] < last_3q)]) // 3,
            len(df[(df['submission_date'] >= year_start) & 
                 (df['submission_date'] < year_start + timedelta(days=31))]),
            len(df[(df['submission_date'] >= year_start + timedelta(days=31)) & 
                 (df['submission_date'] < year_start + timedelta(days=59))])
        ]
        
        # Calculate pages
        pages_data = [
            df[df['submission_date'] >= last_3q]['page_count'].sum() // 3,
            df[(df['submission_date'] >= last_4q) & 
              (df['submission_date'] < last_3q)]['page_count'].sum() // 3,
            df[(df['submission_date'] >= year_start) & 
              (df['submission_date'] < year_start + timedelta(days=31))]['page_count'].sum(),
            df[(df['submission_date'] >= year_start + timedelta(days=31)) & 
              (df['submission_date'] < year_start + timedelta(days=59))]['page_count'].sum()
        ]
        
        # Calculate videos
        videos_data = [
            len(df[(df['submission_date'] >= last_3q) & 
                 (df['material_type'] == 'Video')]) // 3,
            len(df[(df['submission_date'] >= last_4q) & 
                 (df['submission_date'] < last_3q) & 
                 (df['material_type'] == 'Video')]) // 3,
            len(df[(df['submission_date'] >= year_start) & 
                 (df['submission_date'] < year_start + timedelta(days=31)) & 
                 (df['material_type'] == 'Video')]),
            len(df[(df['submission_date'] >= year_start + timedelta(days=31)) & 
                 (df['submission_date'] < year_start + timedelta(days=59)) & 
                 (df['material_type'] == 'Video')])
        ]
        
        # Calculate total
        total_data = [pieces_data[i] + pages_data[i] + videos_data[i] for i in range(4)]
        
        # Add traces
        fig_trend.add_trace(go.Scatter(
            x=periods,
            y=pieces_data,
            mode='lines+markers',
            name='PIECES',
            line=dict(color='purple', width=2)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=periods,
            y=pages_data,
            mode='lines+markers',
            name='PAGES',
            line=dict(color='orange', width=2)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=periods,
            y=videos_data,
            mode='lines+markers',
            name='VIDEOS',
            line=dict(color='green', width=2)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=periods,
            y=total_data,
            mode='lines+markers',
            name='TOTAL',
            line=dict(color='blue', width=3)
        ))
        
        fig_trend.update_layout(
            title='Average Monthly Trend',
            xaxis_title='Time Period',
            yaxis_title='Count',
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Key highlights
        st.markdown("<div class='sub-header'>Key Highlights For The Period</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='highlight'>
        <ul>
            <li>Significant increase in volume of material submitted, reviewed and approved by the Risk & Compliance team.</li>
            <li>Until a software application can be sourced (currently under analysis), all of the input, output and mark-up is done manually via email and MS Office or Adobe mark-ups.</li>
            <li>We have a 7-10 BD SLA, but it often takes longer due to increasing length of materials (20-60 pages), product complexity (income guarantees), and similarity of products.</li>
            <li>One (1) FTE supports the Chief Compliance Officer in this review.</li>
            <li>Volume of material is projected to increase in 2025 due to corporate initiatives, growth in number of sub-advisors and CITs, and 403(b) activities.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='sub-header'>Review Efficiency Metrics</div>", unsafe_allow_html=True)
        
        # Calculate review efficiency metrics
        review_metrics = {
            'Metric': [
                'Average Review Time (Hours)',
                'Average Pages Per Hour',
                'First-Pass Approval Rate',
                'Reviews Requiring Multiple Rounds',
                'Average Time to Resolution (Days)'
            ]
        }
        
        # Periods
        for i, period in enumerate(['3Q 2024', '4Q 2024', 'JAN 2025', 'FEB 2025']):
            if i == 0:
                period_df = df[df['submission_date'] >= last_3q]
            elif i == 1:
                period_df = df[(df['submission_date'] >= last_4q) & (df['submission_date'] < last_3q)]
            elif i == 2:
                period_df = df[(df['submission_date'] >= year_start) & 
                              (df['submission_date'] < year_start + timedelta(days=31))]
            else:
                period_df = df[(df['submission_date'] >= year_start + timedelta(days=31)) & 
                              (df['submission_date'] < year_start + timedelta(days=59))]
            
            # 1. Average Review Time
            avg_time = period_df[period_df['review_time_hours'].notna()]['review_time_hours'].mean()
            
            # 2. Average Pages Per Hour
            if avg_time > 0:
                pages_per_hour = period_df[period_df['review_time_hours'].notna()]['page_count'].sum() / \
                                period_df[period_df['review_time_hours'].notna()]['review_time_hours'].sum()
            else:
                pages_per_hour = 0
            
            # 3. First-Pass Approval Rate
            first_pass = len(period_df[period_df['status'] == 'Approved']) / len(period_df) * 100 if len(period_df) > 0 else 0
            
            # 4. Reviews Requiring Multiple Rounds (using flags as a proxy)
            multi_round = len(period_df[period_df['flags'] > 2]) / len(period_df) * 100 if len(period_df) > 0 else 0
            
            # 5. Average Time to Resolution
            time_to_resolution = random.uniform(3, 12)  # Simulated data
            
            review_metrics[period] = [
                f"{avg_time:.1f}",
                f"{pages_per_hour:.1f}",
                f"{first_pass:.1f}%",
                f"{multi_round:.1f}%",
                f"{time_to_resolution:.1f}"
            ]
        
        review_df = pd.DataFrame(review_metrics)
        st.dataframe(review_df, use_container_width=True, hide_index=True)
        
        # Compliance score distribution
        st.markdown("<div class='sub-header'>Compliance Score Distribution</div>", unsafe_allow_html=True)
        
        fig_hist = px.histogram(
            df, 
            x='compliance_score',
            nbins=10,
            color_discrete_sequence=['#4B73B6'],
            marginal='box'
        )
        
        fig_hist.update_layout(
            title='Distribution of Compliance Scores',
            xaxis_title='Compliance Score',
            yaxis_title='Count',
            height=400
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Review time vs. page count scatter plot
        st.markdown("<div class='sub-header'>Review Time vs. Page Count</div>", unsafe_allow_html=True)
        
        fig_scatter = px.scatter(
            df[df['review_time_hours'].notna()],
            x='page_count',
            y='review_time_hours',
            color='material_type',
            hover_data=['submission_id', 'title', 'source', 'compliance_score'],
            trendline='ols'
        )
        
        fig_scatter.update_layout(
            title='Review Time vs. Page Count by Material Type',
            xaxis_title='Page Count',
            yaxis_title='Review Time (Hours)',
            height=500
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)

# Submit Request Page
elif page == "Submit Request":
    st.markdown("<div class='main-header'>Submit Marketing Material for Compliance Review</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='highlight'>
    Complete this form to submit marketing materials for compliance review. The system will analyze your 
    content against compliance requirements and route it to the appropriate reviewer.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='sub-header'>Submission Details</div>", unsafe_allow_html=True)
        title = st.text_input("Title of Marketing Material")
        
        material_type = st.selectbox(
            "Material Type",
            ["Whitepaper", "Blog Post", "Email", "Social Post", "Webpage", 
             "Video", "Podcast", "Presentation", "PR Article"]
        )
        
        source = st.selectbox(
            "Source",
            ["Corporate Marketing", "Third Party", "RFP/RFI Response"]
        )
        
        page_count = st.number_input("Number of Pages", min_value=1, max_value=100, value=1)
        target_audience = st.selectbox(
            "Target Audience",
            ["Retail Investors", "Institutional Investors", "Financial Advisors", 
             "Plan Sponsors", "Sub-Advisors", "General Public"]
        )
        
        priority = st.selectbox(
            "Priority Level",
            ["Normal", "Urgent", "Expedited"]
        )
        
        contains_performance = st.checkbox("Contains performance data")
        contains_guarantees = st.checkbox("Contains income/principal guarantees")
        contains_third_party = st.checkbox("Contains third-party material")
        
    with col2:
        st.markdown("<div class='sub-header'>Upload Content & Additional Details</div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Marketing Material", 
                                        type=["pdf", "docx", "pptx", "xlsx", "txt", "jpg", "png"])
        
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Display file details and preview
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption='Preview', use_column_width=True)
            elif uploaded_file.type == 'application/pdf':
                st.markdown(f"PDF uploaded: {uploaded_file.name}")
            else:
                st.markdown(f"File uploaded: {uploaded_file.name}")
        
        st.text_area("Comments/Instructions", height=100, 
                    placeholder="Any special instructions or context for the reviewer...")
    
    # Display compliance requirements based on selected source
    if source:
        st.markdown("<div class='sub-header'>Applicable Compliance Requirements</div>", unsafe_allow_html=True)
        
        # Show requirements for the selected source
        requirements = st.session_state.requirements.get(source.split(" ")[0], [])
        general_requirements = st.session_state.requirements.get("General", [])
        
        all_requirements = general_requirements + requirements
        
        # Create expandable section with requirements
        with st.expander("View Compliance Requirements", expanded=True):
            for req in all_requirements:
                st.markdown(f"- {req}")
        
        # AI-based pre-check analysis
        if st.button("Run Pre-Check Analysis"):
            with st.spinner("Analyzing content for compliance issues..."):
                # Simulate analysis time
                time.sleep(3)
                
                # Generate random flags for demonstration
                flags = []
                if contains_performance and random.random() > 0.5:
                    flags.append("Performance data missing required disclaimers")
                
                if contains_guarantees:
                    flags.append("Guarantee language needs review for compliance with regulatory guidelines")
                
                if contains_third_party and random.random() > 0.7:
                    flags.append("Third-party content attribution unclear")
                
                if random.random() > 0.8:
                    flags.append("Potentially misleading statement detected")
                
                # Display analysis results
                st.markdown("<div class='sub-header'>Pre-Check Analysis Results</div>", unsafe_allow_html=True)
                
                if flags:
                    st.markdown("<div style='background-color:#FFF3CD; padding:10px; border-radius:5px; border-left:5px solid #FFC107;'>", unsafe_allow_html=True)
                    st.markdown("<b>Potential compliance issues detected:</b>", unsafe_allow_html=True)
                    for flag in flags:
                        st.markdown(f"- {flag}")
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='background-color:#D4EDDA; padding:10px; border-radius:5px; border-left:5px solid #28A745;'>", unsafe_allow_html=True)
                    st.markdown("<b>No obvious compliance issues detected.</b> Your submission will still require review by the compliance team.", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
    
    # Submit button
    submit_col1, submit_col2 = st.columns([4, 1])
    with submit_col2:
        submit_button = st.button("Submit for Review", type="primary")
    
    if submit_button:
        if not title:
            st.error("Please provide a title for your submission.")
        elif uploaded_file is None:
            st.error("Please upload a file for review.")
        else:
            # Add to dataframe
            new_id = f"SUB-{2024}-{st.session_state.current_id:04d}"
            
            new_submission = {
                "submission_id": new_id,
                "title": title,
                "submission_date": datetime.now().strftime("%Y-%m-%d"),
                "material_type": material_type,
                "source": source,
                "status": "Pending",
                "page_count": page_count,
                "assigned_to": None,
                "review_date": None,
                "compliance_score": None,
                "flags": len(flags) if 'flags' in locals() else 0,
                "review_time_hours": None
            }
            
            # Add to database
            st.session_state.data = pd.concat([st.session_state.data, 
                                             pd.DataFrame([new_submission])], 
                                            ignore_index=True)
            
            st.session_state.current_id += 1
            
            # Success message
            st.success(f"Submission successful! Your reference ID is {new_id}")
            st.markdown(f"""
            <div style='background-color:#E3F2FD; padding:15px; border-radius:5px; margin-top:10px;'>
                <h4>Next Steps</h4>
                <p>Your submission has been received and will be reviewed by the compliance team. 
                The standard review time is 7-10 business days.</p>
                <p>You can check the status of your submission using the reference ID.</p>
            </div>
            """, unsafe_allow_html=True)
