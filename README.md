# 🧠 AI Resume Analyzer Pro

An advanced AI-powered recruitment intelligence platform that helps HR professionals and recruiters efficiently analyze resumes, match candidates to job requirements, and make data-driven hiring decisions.

![AI Resume Analyzer Pro](https://img.shields.io/badge/AI-Resume%20Analyzer-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## ✨ Features

### 🚀 Core Functionality
- **Multi-format Resume Processing**: Support for PDF, DOCX, DOC, and TXT files
- **AI-Powered Parsing**: Extract structured information using NLP and machine learning
- **Intelligent Job Matching**: Advanced algorithms to match candidates with job requirements
- **Batch Processing**: Analyze multiple resumes simultaneously
- **Real-time Analytics**: Comprehensive dashboards and visualizations

### 📊 Advanced Analytics
- **Match Score Calculation**: Multi-dimensional scoring based on skills, experience, and education
- **Skills Gap Analysis**: Identify missing skills and competencies
- **Candidate Ranking**: Automatic ranking based on job fit
- **Performance Metrics**: Detailed analytics and insights
- **Export Capabilities**: CSV, JSON, and comprehensive reports

### 🎯 Smart Features
- **Fuzzy Matching**: Intelligent skill and keyword matching
- **Semantic Analysis**: Understanding context and meaning
- **Experience Calculation**: Automatic years of experience detection
- **Education Matching**: Degree and qualification analysis
- **Contact Extraction**: Automatic contact information parsing

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Dashboards**: Rich visualizations with Plotly
- **Intuitive Navigation**: User-friendly interface
- **Real-time Updates**: Live progress tracking
- **Customizable Themes**: Multiple color schemes

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS/HTML
- **Backend**: Python with advanced NLP libraries
- **Machine Learning**: Scikit-learn, spaCy, NLTK
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly, Matplotlib, Seaborn
- **Document Processing**: PyPDF2, python-docx, pdfplumber
- **Text Analysis**: TF-IDF, Cosine Similarity, Fuzzy Matching

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for initial setup

## 🚀 Quick Start

### 1. Clone the Repository
\`\`\`bash
git clone https://github.com/yourusername/ai-resume-analyzer-pro.git
cd ai-resume-analyzer-pro
\`\`\`

### 2. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Download Required Models
\`\`\`bash
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
\`\`\`

### 4. Run the Application
\`\`\`bash
streamlit run app.py
\`\`\`

### 5. Open in Browser
Navigate to `http://localhost:8501` in your web browser.

## 📖 Usage Guide

### 1. Upload Resumes
- Navigate to the "📤 Upload & Analyze" tab
- Drag and drop resume files or use the file uploader
- Supported formats: PDF, DOCX, DOC, TXT
- Maximum file size: 200MB per file

### 2. Configure Job Requirements
- Enter job title and description
- Specify required skills (comma-separated)
- Set experience level and other preferences
- Adjust scoring weights in advanced settings

### 3. Analyze Results
- Click "🚀 Analyze Resumes with AI"
- View real-time processing progress
- Review comprehensive match scores and rankings
- Use filters and search to find ideal candidates

### 4. Manage Candidates
- Star top candidates for easy access
- Add recruiter notes and comments
- Track candidates through hiring pipeline
- Export data for external use

### 5. View Analytics
- Access the "📊 Analytics Dashboard"
- Explore score distributions and trends
- Analyze skills gaps and requirements
- Generate comprehensive reports

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
\`\`\`env
# Optional: Set custom configurations
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
MAX_UPLOAD_SIZE=200
\`\`\`

### Customization
- Modify `requirements.txt` for additional packages
- Update `.streamlit/config.toml` for theme customization
- Extend skill keywords in `resume_parser.py`
- Adjust matching algorithms in `matcher.py`

## 📊 API Reference

### ResumeParser Class
```python
from resume_parser import ResumeParser

parser = ResumeParser()
result = parser.parse_resume(text, filename)
