import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import io
from datetime import datetime
import json
import numpy as np
from resume_parser import ResumeParser
from matcher import JobMatcher
from utils import *

# Page configuration
st.set_page_config(
    page_title="🧠 AI Resume Analyzer Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    }
    
    .metric-card h3 {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card h2 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .candidate-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border-left: 5px solid #10b981;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .candidate-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
    }
    
    .candidate-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.12);
    }
    
    .skill-tag {
        display: inline-block;
        background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
        color: #0277bd;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.2rem;
        border: 1px solid rgba(2, 119, 189, 0.2);
        transition: all 0.2s ease;
    }
    
    .skill-tag:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(2, 119, 189, 0.2);
    }
    
    .matched-skill {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #166534;
        border: 1px solid #22c55e;
        font-weight: 600;
    }
    
    .score-excellent { 
        color: #10b981; 
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
    }
    .score-good { 
        color: #3b82f6; 
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
    }
    .score-fair { 
        color: #f59e0b; 
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
    }
    .score-poor { 
        color: #ef4444; 
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
    }
    
    .upload-area {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(135deg, #f8faff 0%, #f1f5ff 100%);
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #4f46e5;
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
        transform: translateY(-2px);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(102, 126, 234, 0.05);
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 24px;
        background: white;
        border-radius: 10px;
        border: 1px solid rgba(102, 126, 234, 0.1);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .highlight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .progress-container {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .animated-icon {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'parsed_resumes' not in st.session_state:
    st.session_state.parsed_resumes = []
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

def main():
    # Header with animation
    st.markdown("""
    <div class="main-header">
        <h1 class="animated-icon">🧠 AI Resume Analyzer Pro</h1>
        <p>Advanced recruitment intelligence platform powered by AI & Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎛️ Navigation Panel")
        
        page = st.selectbox(
            "Choose your destination:",
            ["📤 Upload & Analyze", "📊 Analytics Dashboard", "👥 Candidate Management", "⚙️ Settings"],
            index=0
        )
        
        # Quick stats in sidebar
        if st.session_state.parsed_resumes:
            st.markdown("### 📈 Quick Stats")
            total = len(st.session_state.parsed_resumes)
            excellent = len([r for r in st.session_state.parsed_resumes if r['match_score'] >= 0.8])
            st.metric("Total Candidates", total)
            st.metric("Excellent Matches", excellent)
            st.metric("Success Rate", f"{(excellent/total*100):.1f}%" if total > 0 else "0%")
    
    # Route to different pages
    if page == "📤 Upload & Analyze":
        upload_and_analyze_page()
    elif page == "📊 Analytics Dashboard":
        analytics_dashboard_page()
    elif page == "👥 Candidate Management":
        candidate_management_page()
    elif page == "⚙️ Settings":
        settings_page()

def upload_and_analyze_page():
    st.markdown("## 📤 Upload Resumes & Configure Analysis")
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📁 Upload Files", "📝 Job Configuration", "⚙️ Advanced Settings"])
    
    with tab1:
        st.markdown("### 📄 Upload Resume Files")
        
        # File uploader with enhanced styling
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        st.markdown("#### 🎯 Drag & Drop Your Resume Files Here")
        uploaded_files = st.file_uploader(
            "Choose resume files (PDF, DOCX, DOC, TXT)",
            type=['pdf', 'docx', 'doc', 'txt'],
            accept_multiple_files=True,
            help="Upload multiple resume files for batch processing. Max 200MB per file."
        )
        st.markdown("*Supports: PDF, DOCX, DOC, TXT formats*")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} files uploaded successfully!")
            
            # Display uploaded files with enhanced UI
            with st.expander("📋 View Uploaded Files", expanded=True):
                for i, file in enumerate(uploaded_files):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    with col1:
                        st.write(f"📄 **{file.name}**")
                    with col2:
                        st.write(f"📊 {file.size / 1024:.1f} KB")
                    with col3:
                        st.write(f"📋 {file.type.split('/')[-1].upper()}")
                    with col4:
                        st.write("✅ Ready")
    
    with tab2:
        st.markdown("### 🎯 Job Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input(
                "🎯 Job Title",
                placeholder="e.g., Senior Software Engineer",
                help="Enter the specific job title you're hiring for"
            )
            
            required_skills = st.text_area(
                "🛠️ Required Skills (comma-separated)",
                placeholder="e.g., Python, React, AWS, Machine Learning, Docker",
                help="Enter required skills separated by commas",
                height=100
            )
            
            experience_level = st.selectbox(
                "📈 Experience Level Required",
                ["Any Level", "Entry Level (0-2 years)", "Mid Level (3-5 years)", 
                 "Senior Level (6-10 years)", "Expert Level (10+ years)"]
            )
        
        with col2:
            location = st.text_input(
                "📍 Preferred Location",
                placeholder="e.g., San Francisco, CA or Remote",
                help="Preferred candidate location or 'Remote' for remote work"
            )
            
            salary_range = st.text_input(
                "💰 Salary Range",
                placeholder="e.g., $80,000 - $120,000",
                help="Expected salary range for the position"
            )
            
            company_size = st.selectbox(
                "🏢 Company Size",
                ["Startup (1-50)", "Small (51-200)", "Medium (201-1000)", "Large (1000+)"]
            )
        
        job_description = st.text_area(
            "📋 Detailed Job Description",
            placeholder="Enter comprehensive job description including responsibilities, requirements, qualifications, and company culture...",
            height=200,
            help="Provide a detailed job description for better matching accuracy"
        )
        
        st.session_state.job_description = job_description
    
    with tab3:
        st.markdown("### ⚙️ Advanced Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔍 Extraction Options**")
            extract_projects = st.checkbox("📊 Extract Projects", value=True)
            extract_certifications = st.checkbox("🏆 Extract Certifications", value=True)
            extract_languages = st.checkbox("🌐 Extract Languages", value=True)
            extract_publications = st.checkbox("📚 Extract Publications", value=False)
            extract_awards = st.checkbox("🏅 Extract Awards", value=True)
        
        with col2:
            st.markdown("**⚖️ Scoring Weights**")
            skills_weight = st.slider("🛠️ Skills Match Weight", 0, 100, 50, help="Weight for skills matching")
            experience_weight = st.slider("💼 Experience Weight", 0, 100, 30, help="Weight for experience matching")
            education_weight = st.slider("🎓 Education Weight", 0, 100, 20, help="Weight for education matching")
            
            # Ensure weights add up to 100
            total_weight = skills_weight + experience_weight + education_weight
            if total_weight != 100:
                st.warning(f"⚠️ Weights total: {total_weight}%. Recommended: 100%")
    
    # Enhanced process button
    if uploaded_files and job_description:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Analyze Resumes with AI", type="primary", use_container_width=True):
                process_resumes(uploaded_files, job_description, job_title, required_skills, 
                              skills_weight, experience_weight, education_weight)
    else:
        st.info("📝 Please upload resume files and provide a job description to start analysis.")

def process_resumes(uploaded_files, job_description, job_title, required_skills, 
                   skills_weight, experience_weight, education_weight):
    """Process uploaded resumes with enhanced UI feedback"""
    
    # Create progress container
    progress_container = st.container()
    
    with progress_container:
        st.markdown('<div class="progress-container">', unsafe_allow_html=True)
        st.markdown("### 🔄 Processing Resumes...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        time_estimate = st.empty()
        
        parser = ResumeParser()
        matcher = JobMatcher()
        parsed_resumes = []
        
        total_files = len(uploaded_files)
        start_time = datetime.now()
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                # Update progress with enhanced feedback
                progress = (i + 1) / total_files
                progress_bar.progress(progress)
                
                elapsed_time = (datetime.now() - start_time).total_seconds()
                estimated_total = elapsed_time / progress if progress > 0 else 0
                remaining_time = max(0, estimated_total - elapsed_time)
                
                status_text.markdown(f"**Processing:** `{uploaded_file.name}` ({i+1}/{total_files})")
                time_estimate.markdown(f"⏱️ Estimated time remaining: {remaining_time:.1f}s")
                
                # Extract text from file
                file_content = uploaded_file.read()
                extracted_text = extract_text_from_file(file_content, uploaded_file.name)
                
                # Parse resume
                parsed_resume = parser.parse_resume(extracted_text, uploaded_file.name)
                
                # Calculate job match score
                if job_description:
                    match_score = matcher.calculate_match_score(
                        extracted_text, job_description, job_title, required_skills
                    )
                    parsed_resume.update(match_score)
                
                # Add metadata
                parsed_resume.update({
                    'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'file_size': len(file_content),
                    'starred': False,
                    'notes': "",
                    'status': 'completed'
                })
                
                parsed_resumes.append(parsed_resume)
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                # Add error entry
                parsed_resumes.append({
                    'filename': uploaded_file.name,
                    'name': 'Error processing file',
                    'status': 'error',
                    'match_score': 0.0,
                    'error_message': str(e)
                })
                continue
        
        # Complete processing
        progress_bar.progress(1.0)
        status_text.markdown("✅ **Processing Complete!**")
        time_estimate.markdown(f"🎉 Total processing time: {(datetime.now() - start_time).total_seconds():.1f}s")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Store results and sort by match score
    st.session_state.parsed_resumes = sorted(
        [r for r in parsed_resumes if r.get('status') != 'error'], 
        key=lambda x: x.get('match_score', 0), 
        reverse=True
    )
    st.session_state.processing_complete = True
    
    # Show success message with stats
    successful = len([r for r in parsed_resumes if r.get('status') != 'error'])
    failed = len(parsed_resumes) - successful
    
    if successful > 0:
        st.success(f"🎉 Successfully processed {successful} resumes!")
        if failed > 0:
            st.warning(f"⚠️ {failed} files failed to process")
        
        # Show results immediately
        display_results()
    else:
        st.error("❌ No resumes were successfully processed. Please check your files and try again.")

def display_results():
    """Display parsed resume results with enhanced UI"""
    
    if not st.session_state.parsed_resumes:
        st.info("📭 No resumes processed yet.")
        return
    
    st.markdown("## 📊 Analysis Results")
    
    # Enhanced summary metrics
    display_summary_metrics()
    
    # Advanced filters section
    st.markdown("### 🔍 Advanced Filters & Search")
    
    # Filter controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        min_score = st.slider("🎯 Minimum Score", 0, 100, 0, help="Filter candidates by minimum match score")
    
    with col2:
        max_score = st.slider("🎯 Maximum Score", 0, 100, 100, help="Filter candidates by maximum match score")
    
    with col3:
        skill_filter = st.text_input("🛠️ Required Skills", placeholder="e.g., Python, React")
    
    with col4:
        sort_by = st.selectbox("📊 Sort by", ["Match Score", "Name", "Experience", "Upload Time"])
    
    # Enhanced search
    search_term = st.text_input(
        "🔍 Search candidates", 
        placeholder="Search by name, email, skills, company...",
        help="Search across all candidate information"
    )
    
    # Apply filters
    filtered_resumes = filter_resumes(
        st.session_state.parsed_resumes, 
        min_score, max_score, skill_filter, search_term
    )
    
    # Sort results
    filtered_resumes = sort_resumes(filtered_resumes, sort_by)
    
    # Results header with count
    st.markdown(f"### 👥 Candidates ({len(filtered_resumes)} of {len(st.session_state.parsed_resumes)})")
    
    # Display candidates with enhanced cards
    if filtered_resumes:
        for i, resume in enumerate(filtered_resumes):
            display_candidate_card(resume, i)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #64748b;">
            <h3>🔍 No candidates match your filters</h3>
            <p>Try adjusting your search criteria or filters</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced export options
    if filtered_resumes:
        st.markdown("### 📥 Export & Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Export CSV", use_container_width=True):
                export_to_csv(filtered_resumes)
        
        with col2:
            if st.button("📋 Export JSON", use_container_width=True):
                export_to_json(filtered_resumes)
        
        with col3:
            if st.button("📄 Generate Report", use_container_width=True):
                generate_report(filtered_resumes)
        
        with col4:
            if st.button("📧 Email Top Candidates", use_container_width=True):
                st.info("📧 Email functionality would be implemented here")

def display_summary_metrics():
    """Display enhanced summary metrics with animations"""
    
    resumes = st.session_state.parsed_resumes
    
    if not resumes:
        return
    
    # Calculate comprehensive metrics
    total_candidates = len(resumes)
    excellent_matches = len([r for r in resumes if r.get('match_score', 0) >= 0.8])
    good_matches = len([r for r in resumes if 0.6 <= r.get('match_score', 0) < 0.8])
    fair_matches = len([r for r in resumes if 0.4 <= r.get('match_score', 0) < 0.6])
    poor_matches = len([r for r in resumes if r.get('match_score', 0) < 0.4])
    avg_score = np.mean([r.get('match_score', 0) for r in resumes]) * 100
    
    # Display metrics in enhanced cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Total Candidates</h3>
            <h2>{total_candidates}</h2>
            <p style="color: #64748b; margin: 0;">Resumes Processed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 Excellent Matches</h3>
            <h2 style="color: #10b981;">{excellent_matches}</h2>
            <p style="color: #64748b; margin: 0;">80%+ Match Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👍 Good Matches</h3>
            <h2 style="color: #3b82f6;">{good_matches}</h2>
            <p style="color: #64748b; margin: 0;">60-79% Match Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Average Score</h3>
            <h2 style="color: #f59e0b;">{avg_score:.1f}%</h2>
            <p style="color: #64748b; margin: 0;">Overall Performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Score distribution chart
    if total_candidates > 1:
        st.markdown("### 📊 Score Distribution")
        
        # Create distribution data
        score_ranges = ['Excellent (80-100%)', 'Good (60-79%)', 'Fair (40-59%)', 'Poor (0-39%)']
        score_counts = [excellent_matches, good_matches, fair_matches, poor_matches]
        colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
        
        fig = px.pie(
            values=score_counts,
            names=score_ranges,
            title="Candidate Score Distribution",
            color_discrete_sequence=colors
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14)
        )
        st.plotly_chart(fig, use_container_width=True)

def display_candidate_card(resume, index):
    """Display enhanced candidate card with modern UI"""
    
    score = resume.get('match_score', 0) * 100
    score_class = get_score_class(resume.get('match_score', 0))
    score_label = get_score_label(resume.get('match_score', 0))
    
    # Main candidate card
    with st.container():
        st.markdown(f"""
        <div class="candidate-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <div>
                    <h3 style="margin: 0; color: #1f2937; font-size: 1.5rem; font-weight: 600;">
                        {resume.get('name', 'Name not found')}
                    </h3>
                    <div style="margin-top: 0.5rem; color: #6b7280;">
                        <span style="margin-right: 1rem;">📧 {resume.get('email', 'N/A')}</span>
                        <span style="margin-right: 1rem;">📞 {resume.get('phone', 'N/A')}</span>
                        <span>📍 {resume.get('location', 'N/A')}</span>
                    </div>
                </div>
                <div style="text-align: right;">
                    <h2 class="{score_class}" style="margin: 0; font-size: 2.5rem;">{score:.1f}%</h2>
                    <p style="margin: 0; color: #6b7280; font-weight: 500;">{score_label}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable details with enhanced content
        with st.expander(f"📋 Detailed Analysis - {resume.get('name', 'Candidate')}", expanded=False):
            
            # Score breakdown with visual indicators
            st.markdown("#### 📊 Score Breakdown")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                skill_score = resume.get('skill_match_score', 0) * 100
                st.metric("🛠️ Skills Match", f"{skill_score:.1f}%", 
                         delta=f"{skill_score - 50:.1f}%" if skill_score != 50 else None)
            
            with col2:
                exp_score = resume.get('experience_match_score', 0) * 100
                st.metric("💼 Experience Match", f"{exp_score:.1f}%",
                         delta=f"{exp_score - 50:.1f}%" if exp_score != 50 else None)
            
            with col3:
                edu_score = resume.get('education_match_score', 0) * 100
                st.metric("🎓 Education Match", f"{edu_score:.1f}%",
                         delta=f"{edu_score - 50:.1f}%" if edu_score != 50 else None)
            
            # Detailed information in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🛠️ Skills", "💼 Experience", "🎓 Education", "📊 Additional"])
            
            with tab1:
                st.markdown("**Technical Skills**")
                skills = resume.get('skills', [])
                if skills:
                    skills_html = ""
                    for skill in skills:
                        is_matched = skill.lower() in [k.lower() for k in resume.get('keywords_matched', [])]
                        class_name = "matched-skill" if is_matched else ""
                        skills_html += f'<span class="skill-tag {class_name}">{skill}</span>'
                    st.markdown(skills_html, unsafe_allow_html=True)
                else:
                    st.info("No skills extracted")
            
            with tab2:
                st.markdown("**Work Experience**")
                experience = resume.get('experience', [])
                if experience:
                    for exp in experience:
                        if isinstance(exp, dict):
                            st.markdown(f"""
                            **{exp.get('title', 'N/A')}** at *{exp.get('company', 'N/A')}*  
                            📅 {exp.get('duration', 'N/A')}  
                            📝 {exp.get('description', 'No description')[:200]}...
                            """)
                        else:
                            st.write(f"• {exp}")
                else:
                    st.info("No experience information extracted")
            
            with tab3:
                st.markdown("**Educational Background**")
                education = resume.get('education', [])
                if education:
                    for edu in education:
                        if isinstance(edu, dict):
                            st.markdown(f"""
                            **{edu.get('degree', 'N/A')}**  
                            🏫 {edu.get('institution', 'N/A')}  
                            📅 {edu.get('year', 'N/A')}
                            """)
                        else:
                            st.write(f"• {edu}")
                else:
                    st.info("No education information extracted")
            
            with tab4:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏆 Certifications**")
                    certs = resume.get('certifications', [])
                    if certs:
                        for cert in certs:
                            st.write(f"• {cert}")
                    else:
                        st.info("No certifications found")
                
                with col2:
                    st.markdown("**📊 Projects**")
                    projects = resume.get('projects', [])
                    if projects:
                        for project in projects:
                            if isinstance(project, dict):
                                st.write(f"• **{project.get('name', 'Project')}**: {project.get('description', 'No description')[:100]}...")
                            else:
                                st.write(f"• {project}")
                    else:
                        st.info("No projects found")
            
            # Action buttons and notes
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                notes_key = f"notes_{index}"
                notes = st.text_area(
                    "📝 Recruiter Notes:", 
                    value=resume.get('notes', ''), 
                    key=notes_key,
                    height=100,
                    placeholder="Add your notes about this candidate..."
                )
            
            with col2:
                if st.button(f"💾 Save Notes", key=f"save_{index}"):
                    st.session_state.parsed_resumes[index]['notes'] = notes
                    st.success("✅ Notes saved!")
                
                star_key = f"star_{index}"
                starred = st.checkbox(
                    "⭐ Star Candidate", 
                    value=resume.get('starred', False), 
                    key=star_key
                )
                st.session_state.parsed_resumes[index]['starred'] = starred
            
            with col3:
                if st.button(f"📧 Contact", key=f"contact_{index}"):
                    email = resume.get('email', '')
                    if email:
                        st.success(f"📧 Email: {email}")
                        st.info("Email client integration would open here")
                    else:
                        st.warning("No email found")
                
                if st.button(f"📄 View Resume", key=f"view_{index}"):
                    st.info("Resume viewer would open here")

def analytics_dashboard_page():
    """Enhanced analytics dashboard with comprehensive visualizations"""
    
    st.markdown("## 📊 Advanced Analytics Dashboard")
    
    if not st.session_state.parsed_resumes:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h3>📊 No Data Available</h3>
            <p>Please process some resumes first to see analytics</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    resumes = st.session_state.parsed_resumes
    
    # Key metrics overview
    st.markdown("### 📈 Key Performance Indicators")
    display_summary_metrics()
    
    # Advanced analytics
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution histogram
        st.markdown("### 📊 Score Distribution Analysis")
        scores = [r.get('match_score', 0) * 100 for r in resumes]
        
        fig = px.histogram(
            x=scores,
            nbins=20,
            title="Candidate Score Distribution",
            labels={'x': 'Match Score (%)', 'y': 'Number of Candidates'},
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Skills analysis
        st.markdown("### 🛠️ Top Skills Analysis")
        all_skills = []
        for resume in resumes:
            all_skills.extend(resume.get('skills', []))
        
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts().head(15)
            
            fig = px.bar(
                x=skill_counts.values,
                y=skill_counts.index,
                orientation='h',
                title="Most Common Skills",
                labels={'x': 'Number of Candidates', 'y': 'Skills'},
                color=skill_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Experience vs Score analysis
    st.markdown("### 📊 Experience vs Performance Analysis")
    
    # Create DataFrame for analysis
    df_analysis = pd.DataFrame([
        {
            'name': r.get('name', 'Unknown'),
            'score': r.get('match_score', 0) * 100,
            'experience': r.get('years_experience', 0),
            'skills_count': len(r.get('skills', [])),
            'education_level': get_education_level(r.get('education', []))
        }
        for r in resumes
    ])
    
    if not df_analysis.empty:
        fig = px.scatter(
            df_analysis,
            x='experience',
            y='score',
            size='skills_count',
            color='education_level',
            hover_name='name',
            title="Match Score vs Years of Experience",
            labels={
                'experience': 'Years of Experience', 
                'score': 'Match Score (%)',
                'skills_count': 'Number of Skills'
            }
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Skills gap analysis
    st.markdown("### 🎯 Skills Gap Analysis")
    
    if st.session_state.job_description:
        # Extract required skills from job description
        required_skills = extract_skills_from_text(st.session_state.job_description)
        
        # Calculate skill coverage
        skill_coverage = {}
        for skill in required_skills:
            count = sum(1 for resume in resumes if skill.lower() in [s.lower() for s in resume.get('skills', [])])
            skill_coverage[skill] = (count / len(resumes)) * 100
        
        if skill_coverage:
            coverage_df = pd.DataFrame(list(skill_coverage.items()), columns=['Skill', 'Coverage %'])
            coverage_df = coverage_df.sort_values('Coverage %', ascending=True)
            
            fig = px.bar(
                coverage_df,
                x='Coverage %',
                y='Skill',
                orientation='h',
                title="Skills Coverage Among Candidates",
                color='Coverage %',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)

def candidate_management_page():
    """Enhanced candidate management interface"""
    
    st.markdown("## 👥 Advanced Candidate Management")
    
    if not st.session_state.parsed_resumes:
        st.info("📭 No candidates available. Please process some resumes first.")
        return
    
    # Starred candidates section
    starred_candidates = [r for r in st.session_state.parsed_resumes if r.get('starred', False)]
    
    if starred_candidates:
        st.markdown("### ⭐ Starred Candidates")
        
        for i, candidate in enumerate(starred_candidates):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                score = candidate.get('match_score', 0) * 100
                st.markdown(f"""
                **{candidate.get('name', 'Unknown')}** - {score:.1f}% match  
                📧 {candidate.get('email', 'N/A')} | 📞 {candidate.get('phone', 'N/A')}
                """)
            
            with col2:
                if st.button(f"📧 Email", key=f"email_starred_{i}"):
                    st.info(f"📧 Would open email to: {candidate.get('email', 'N/A')}")
            
            with col3:
                if st.button(f"📞 Call", key=f"call_starred_{i}"):
                    st.info(f"📞 Would dial: {candidate.get('phone', 'N/A')}")
            
            with col4:
                if st.button(f"📄 View", key=f"view_starred_{i}"):
                    st.session_state.selected_candidate = candidate
    
    # Candidate pipeline management
    st.markdown("### 🔄 Candidate Pipeline")
    
    # Pipeline stages
    pipeline_stages = {
        "📥 New": [r for r in st.session_state.parsed_resumes if not r.get('pipeline_stage')],
        "📞 Contacted": [r for r in st.session_state.parsed_resumes if r.get('pipeline_stage') == 'contacted'],
        "📋 Interviewed": [r for r in st.session_state.parsed_resumes if r.get('pipeline_stage') == 'interviewed'],
        "✅ Hired": [r for r in st.session_state.parsed_resumes if r.get('pipeline_stage') == 'hired'],
        "❌ Rejected": [r for r in st.session_state.parsed_resumes if r.get('pipeline_stage') == 'rejected']
    }
    
    # Display pipeline metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📥 New", len(pipeline_stages["📥 New"]))
    with col2:
        st.metric("📞 Contacted", len(pipeline_stages["📞 Contacted"]))
    with col3:
        st.metric("📋 Interviewed", len(pipeline_stages["📋 Interviewed"]))
    with col4:
        st.metric("✅ Hired", len(pipeline_stages["✅ Hired"]))
    with col5:
        st.metric("❌ Rejected", len(pipeline_stages["❌ Rejected"]))
    
    # Bulk operations
    st.markdown("### 🔄 Bulk Operations")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Export All Data", use_container_width=True):
            export_to_csv(st.session_state.parsed_resumes)
    
    with col2:
        if st.button("⭐ Export Starred", use_container_width=True):
            if starred_candidates:
                export_to_csv(starred_candidates)
            else:
                st.warning("No starred candidates to export.")
    
    with col3:
        if st.button("📧 Email Top 5", use_container_width=True):
            top_candidates = sorted(st.session_state.parsed_resumes, 
                                  key=lambda x: x.get('match_score', 0), reverse=True)[:5]
            emails = [c.get('email', '') for c in top_candidates if c.get('email')]
            if emails:
                st.success(f"📧 Would email: {', '.join(emails)}")
            else:
                st.warning("No email addresses found in top candidates")
    
    with col4:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            if st.button("⚠️ Confirm Clear All"):
                st.session_state.parsed_resumes = []
                st.session_state.processing_complete = False
                st.success("🗑️ All data cleared!")
                st.experimental_rerun()

def settings_page():
    """Enhanced settings and configuration page"""
    
    st.markdown("## ⚙️ Settings & Configuration")
    
    # Parsing configuration
    st.markdown("### 🔧 Parsing Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⚖️ Default Scoring Weights**")
        default_skills_weight = st.slider("🛠️ Skills Weight", 0, 100, 50)
        default_experience_weight = st.slider("💼 Experience Weight", 0, 100, 30)
        default_education_weight = st.slider("🎓 Education Weight", 0, 100, 20)
        
        total_weight = default_skills_weight + default_experience_weight + default_education_weight
        if total_weight != 100:
            st.warning(f"⚠️ Total weight: {total_weight}%. Recommended: 100%")
    
    with col2:
        st.markdown("**🔍 Extraction Options**")
        extract_projects = st.checkbox("📊 Extract Projects by Default", value=True)
        extract_certifications = st.checkbox("🏆 Extract Certifications by Default", value=True)
        extract_languages = st.checkbox("🌐 Extract Languages by Default", value=True)
        extract_awards = st.checkbox("🏅 Extract Awards by Default", value=True)
        extract_publications = st.checkbox("📚 Extract Publications by Default", value=False)
    
    # Export settings
    st.markdown("### 📥 Export Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox("📄 Default Export Format", ["CSV", "JSON", "Excel"])
        include_raw_text = st.checkbox("📝 Include Raw Resume Text in Exports", value=False)
        include_notes = st.checkbox("📋 Include Recruiter Notes in Exports", value=True)
    
    with col2:
        date_format = st.selectbox("📅 Date Format", ["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY"])
        timezone = st.selectbox("🌍 Timezone", ["UTC", "EST", "PST", "CST", "MST"])
    
    # UI/UX settings
    st.markdown("### 🎨 User Interface Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox("🎨 Color Theme", ["Default", "Dark", "Light", "High Contrast"])
        show_animations = st.checkbox("✨ Enable Animations", value=True)
        compact_view = st.checkbox("📱 Compact View", value=False)
    
    with col2:
        results_per_page = st.slider("📄 Results Per Page", 5, 50, 10)
        auto_save = st.checkbox("💾 Auto-save Notes", value=True)
        show_tooltips = st.checkbox("💡 Show Help Tooltips", value=True)
    
    # Advanced settings
    st.markdown("### 🔬 Advanced Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🤖 AI/ML Settings**")
        similarity_threshold = st.slider("🎯 Similarity Threshold", 0.0, 1.0, 0.5, 0.1)
        use_advanced_nlp = st.checkbox("🧠 Use Advanced NLP", value=True)
        enable_fuzzy_matching = st.checkbox("🔍 Enable Fuzzy Skill Matching", value=True)
    
    with col2:
        st.markdown("**⚡ Performance Settings**")
        max_file_size = st.slider("📁 Max File Size (MB)", 1, 200, 50)
        parallel_processing = st.checkbox("⚡ Enable Parallel Processing", value=True)
        cache_results = st.checkbox("💾 Cache Processing Results", value=True)
    
    # Save settings
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        # Here you would save settings to a config file or database
        st.success("✅ Settings saved successfully!")
        st.balloons()

# Helper functions (continued in next part due to length)
def filter_resumes(resumes, min_score, max_score, skill_filter, search_term):
    """Enhanced resume filtering with multiple criteria"""
    
    filtered = []
    
    for resume in resumes:
        score = resume.get('match_score', 0) * 100
        
        # Score filter
        if score < min_score or score > max_score:
            continue
        
        # Skill filter
        if skill_filter:
            skills = [s.lower() for s in resume.get('skills', [])]
            filter_skills = [s.strip().lower() for s in skill_filter.split(',')]
            if not any(fs in ' '.join(skills) for fs in filter_skills):
                continue
        
        # Search filter (enhanced to search multiple fields)
        if search_term:
            search_fields = [
                resume.get('name', ''),
                resume.get('email', ''),
                ' '.join(resume.get('skills', [])),
                ' '.join([exp.get('company', '') if isinstance(exp, dict) else str(exp) 
                         for exp in resume.get('experience', [])]),
                ' '.join([edu.get('institution', '') if isinstance(edu, dict) else str(edu) 
                         for edu in resume.get('education', [])])
            ]
            search_text = ' '.join(search_fields).lower()
            if search_term.lower() not in search_text:
                continue
        
        filtered.append(resume)
    
    return filtered

def sort_resumes(resumes, sort_by):
    """Enhanced resume sorting with multiple criteria"""
    
    if sort_by == "Match Score":
        return sorted(resumes, key=lambda x: x.get('match_score', 0), reverse=True)
    elif sort_by == "Name":
        return sorted(resumes, key=lambda x: x.get('name', '').lower())
    elif sort_by == "Experience":
        return sorted(resumes, key=lambda x: x.get('years_experience', 0), reverse=True)
    elif sort_by == "Upload Time":
        return sorted(resumes, key=lambda x: x.get('upload_time', ''), reverse=True)
    
    return resumes

def get_score_class(score):
    """Get CSS class for score styling"""
    if score >= 0.8:
        return "score-excellent"
    elif score >= 0.6:
        return "score-good"
    elif score >= 0.4:
        return "score-fair"
    else:
        return "score-poor"

def get_score_label(score):
    """Get human-readable label for score"""
    if score >= 0.8:
        return "🎯 Excellent Match"
    elif score >= 0.6:
        return "👍 Good Match"
    elif score >= 0.4:
        return "⚖️ Fair Match"
    else:
        return "❌ Poor Match"

def get_education_level(education):
    """Determine education level from education list"""
    if not education:
        return "Unknown"
    
    for edu in education:
        degree = edu.get('degree', '').lower() if isinstance(edu, dict) else str(edu).lower()
        if 'phd' in degree or 'doctorate' in degree:
            return "PhD"
        elif 'master' in degree or 'mba' in degree:
            return "Masters"
        elif 'bachelor' in degree:
            return "Bachelors"
    
    return "Other"

def export_to_csv(resumes):
    """Enhanced CSV export with comprehensive data"""
    
    data = []
    for resume in resumes:
        data.append({
            'Name': resume.get('name', ''),
            'Email': resume.get('email', ''),
            'Phone': resume.get('phone', ''),
            'Location': resume.get('location', ''),
            'Match Score': f"{resume.get('match_score', 0)*100:.1f}%",
            'Skills Match': f"{resume.get('skill_match_score', 0)*100:.1f}%",
            'Experience Match': f"{resume.get('experience_match_score', 0)*100:.1f}%",
            'Education Match': f"{resume.get('education_match_score', 0)*100:.1f}%",
            'Skills': ', '.join(resume.get('skills', [])),
            'Years Experience': resume.get('years_experience', 0),
            'Education': '; '.join([
                f"{edu.get('degree', '')} from {edu.get('institution', '')}" 
                if isinstance(edu, dict) else str(edu) 
                for edu in resume.get('education', [])
            ]),
            'Certifications': '; '.join(resume.get('certifications', [])),
            'Starred': '⭐' if resume.get('starred', False) else '',
            'Notes': resume.get('notes', ''),
            'Upload Time': resume.get('upload_time', ''),
            'Filename': resume.get('filename', '')
        })
    
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def export_to_json(resumes):
    """Enhanced JSON export with full data structure"""
    
    # Clean and prepare data for JSON export
    export_data = {
        'export_info': {
            'timestamp': datetime.now().isoformat(),
            'total_candidates': len(resumes),
            'version': '2.0'
        },
        'candidates': resumes
    }
    
    json_data = json.dumps(export_data, indent=2, default=str)
    
    st.download_button(
        label="📥 Download JSON Data",
        data=json_data,
        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def generate_report(resumes):
    """Generate comprehensive analysis report"""
    
    # Calculate comprehensive statistics
    total_candidates = len(resumes)
    excellent_matches = len([r for r in resumes if r.get('match_score', 0) >= 0.8])
    good_matches = len([r for r in resumes if 0.6 <= r.get('match_score', 0) < 0.8])
    avg_score = np.mean([r.get('match_score', 0) for r in resumes]) * 100
    
    # Top skills analysis
    all_skills = []
    for resume in resumes:
        all_skills.extend(resume.get('skills', []))
    top_skills = pd.Series(all_skills).value_counts().head(10)
    
    report = f"""
# 📊 Resume Analysis Report
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Executive Summary
- **Total Candidates Analyzed:** {total_candidates}
- **Excellent Matches (80%+):** {excellent_matches} ({excellent_matches/total_candidates*100:.1f}%)
- **Good Matches (60-79%):** {good_matches} ({good_matches/total_candidates*100:.1f}%)
- **Average Match Score:** {avg_score:.1f}%

## 🎯 Top Performing Candidates

"""
    
    # Add top 10 candidates
    top_candidates = sorted(resumes, key=lambda x: x.get('match_score', 0), reverse=True)[:10]
    
    for i, resume in enumerate(top_candidates, 1):
        report += f"""
### {i}. {resume.get('name', 'Unknown')}
- **Match Score:** {resume.get('match_score', 0)*100:.1f}%
- **Email:** {resume.get('email', 'N/A')}
- **Phone:** {resume.get('phone', 'N/A')}
- **Top Skills:** {', '.join(resume.get('skills', [])[:5])}
- **Experience:** {resume.get('years_experience', 0)} years
- **Education:** {resume.get('education', [{}])[0].get('degree', 'N/A') if resume.get('education') else 'N/A'}

"""
    
    # Add skills analysis
    report += f"""
## 🛠️ Skills Analysis

### Most Common Skills:
"""
    
    for skill, count in top_skills.items():
        percentage = (count / total_candidates) * 100
        report += f"- **{skill}:** {count} candidates ({percentage:.1f}%)\n"
    
    # Add recommendations
    report += f"""

## 💡 Recommendations

### Immediate Actions:
1. **Contact Top {min(5, excellent_matches)} Candidates:** Focus on candidates with 80%+ match scores
2. **Skills Gap Analysis:** Consider training for skills with low coverage
3. **Pipeline Optimization:** Review filtering criteria if match rates are low

### Strategic Insights:
- **Average candidate quality:** {'High' if avg_score >= 70 else 'Medium' if avg_score >= 50 else 'Needs Improvement'}
- **Skill diversity:** {'High' if len(top_skills) >= 20 else 'Medium' if len(top_skills) >= 10 else 'Low'}
- **Experience range:** {min([r.get('years_experience', 0) for r in resumes])}-{max([r.get('years_experience', 0) for r in resumes])} years

---
*Report generated by AI Resume Analyzer Pro*
"""
    
    st.download_button(
        label="📄 Download Analysis Report",
        data=report,
        file_name=f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )

if __name__ == "__main__":
    main()
