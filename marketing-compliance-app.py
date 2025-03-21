import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import io

# Set page configuration
st.set_page_config(
    page_title="GGTC Marketing Compliance Review Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Basic CSS for styling
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
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio("", ["Dashboard", "Submit Request", "Review Queue", "Settings"], index=0)

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
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Submissions", len(df), f"{len(df) - len(df[df['submission_date'] < last_3q])}")
    
    with col2:
        pending = len(df[df['status'].isin(['Pending', 'In Review'])])
        st.metric("Pending Reviews", pending, f"{pending - len(df[df['status'].isin(['Pending', 'In Review']) & (df['submission_date'] < last_4q)])}")
    
    with col3:
        avg_time = df[df['review_time_hours'].notna()]['review_time_hours'].mean()
        st.metric("Avg. Review Time (hrs)", f"{avg_time:.1f}")
    
    with col4:
        compliance = len(df[df['compliance_score'] >= 80]) / len(df) * 100 if len(df) > 0 else 0
        st.metric("Compliance Rate", f"{compliance:.1f}%")
    
    # Create a simple bar chart showing submission counts by material type
    st.markdown("<div class='sub-header'>Submissions by Material Type</div>", unsafe_allow_html=True)
    
    material_counts = df['material_type'].value_counts().reset_index()
    material_counts.columns = ['Material Type', 'Count']
    
    fig = px.bar(
        material_counts,
        x='Material Type',
        y='Count',
        color='Material Type'
    )
    
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a simple line chart showing submissions over time
    st.markdown("<div class='sub-header'>Submission Trends</div>", unsafe_allow_html=True)
    
    df['month'] = df['submission_date'].dt.strftime('%Y-%m')
    monthly_counts = df.groupby('month').size().reset_index()
    monthly_counts.columns = ['Month', 'Count']
    
    fig_line = px.line(
        monthly_counts,
        x='Month',
        y='Count',
        markers=True
    )
    
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Display key highlights
    st.markdown("<div class='sub-header'>Key Highlights</div>", unsafe_allow_html=True)
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
    
    with col2:
        st.markdown("<div class='sub-header'>Upload Content</div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Marketing Material", 
                                        type=["pdf", "docx", "pptx", "xlsx", "txt", "jpg", "png"])
        
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Display file details
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
    
    # Submit button
    if st.button("Submit for Review", type="primary"):
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
                "flags": 0,
                "review_time_hours": None
            }
            
            # Add to database
            st.session_state.data = pd.concat([st.session_state.data, 
                                             pd.DataFrame([new_submission])], 
                                            ignore_index=True)
            
            st.session_state.current_id += 1
            
            # Success message
            st.success(f"Submission successful! Your reference ID is {new_id}")

# Review Queue Page
elif page == "Review Queue":
    st.markdown("<div class='main-header'>Compliance Review Queue</div>", unsafe_allow_html=True)
    
    # Filter controls
    status_filter = st.multiselect(
        "Status",
        ["Pending", "In Review", "Approved", "Rejected", "Needs Revision"],
        default=["Pending", "In Review"]
    )
    
    # Apply filters
    df = st.session_state.data.copy()
    
    if status_filter:
        df = df[df['status'].isin(status_filter)]
    
    # Queue metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total in Queue", len(df))
    
    with col2:
        pending = len(df[df['status'] == 'Pending'])
        st.metric("Pending Assignment", pending)
    
    with col3:
        in_review = len(df[df['status'] == 'In Review'])
        st.metric("In Review", in_review)
    
    # Queue table
    st.markdown("<div class='sub-header'>Current Queue</div>", unsafe_allow_html=True)
    
    # Create a simplified dataframe for display
    display_df = df[['submission_id', 'title', 'submission_date', 'material_type', 
                    'source', 'status', 'page_count', 'assigned_to']].copy()
    
    # Fill NaN values
    display_df['assigned_to'] = display_df['assigned_to'].fillna('Unassigned')
    
    # Display table
    st.dataframe(display_df, use_container_width=True)
    
    # Queue management controls
    st.markdown("<div class='sub-header'>Assign Reviewers</div>", unsafe_allow_html=True)
    
    selected_item = st.selectbox(
        "Select Submission",
        df[df['status'] == 'Pending']['submission_id'].tolist(),
        format_func=lambda x: f"{x} - {df[df['submission_id'] == x]['title'].values[0]}" if len(df[df['submission_id'] == x]) > 0 else x
    )
    
    if selected_item:
        reviewers = ["Amanda H.", "Michael T.", "Sarah L.", "David R.", "Jessica W."]
        assigned_reviewer = st.selectbox("Assign to", reviewers)
        
        if st.button("Assign"):
            # Update dataframe
            idx = st.session_state.data[st.session_state.data['submission_id'] == selected_item].index
            if len(idx) > 0:
                st.session_state.data.loc[idx, 'assigned_to'] = assigned_reviewer
                st.session_state.data.loc[idx, 'status'] = 'In Review'
                
                st.success(f"Successfully assigned {selected_item} to {assigned_reviewer}")
                st.experimental_rerun()

# Settings Page
elif page == "Settings":
    st.markdown("<div class='main-header'>System Settings</div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["General Settings", "Compliance Rules"])
    
    with tab1:
        st.markdown("<div class='sub-header'>General Settings</div>", unsafe_allow_html=True)
        
        sla_days = st.slider("Default SLA (Business Days)", 1, 15, 7)
        
        smartsheet_api = st.text_input("Smartsheet API Key", type="password")
        
        refresh_interval = st.select_slider(
            "Dashboard Refresh Interval",
            options=["5 minutes", "15 minutes", "30 minutes", "1 hour", "4 hours", "Daily"],
            value="30 minutes"
        )
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully")
    
    with tab2:
        st.markdown("<div class='sub-header'>Compliance Rules Configuration</div>", unsafe_allow_html=True)
        
        # Display requirements from session state
        requirements = st.session_state.requirements
        
        # Create tabs for each category
        req_tabs = st.tabs(requirements.keys())
        
        for i, (category, rules) in enumerate(requirements.items()):
            with req_tabs[i]:
                st.markdown(f"**{category} Requirements**")
                
                # Display rules
                for j, rule in enumerate(rules):
                    st.markdown(f"- {rule}")

# Run the app
if __name__ == "__main__":
    # This is where the app would be executed
    pass
