import re
import nltk
import spacy
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional
import textstat

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if spaCy model is not installed
    nlp = None

class ResumeParser:
    """Advanced resume parser using NLP and pattern matching"""
    
    def __init__(self):
        self.skills_keywords = self._load_skills_keywords()
        self.education_keywords = self._load_education_keywords()
        self.experience_keywords = self._load_experience_keywords()
        
    def _load_skills_keywords(self) -> List[str]:
        """Load comprehensive list of technical skills"""
        return [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift',
            'Kotlin', 'TypeScript', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'Bash', 'PowerShell',
            
            # Web Technologies
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js', 'Django', 'Flask',
            'Spring', 'Laravel', 'Ruby on Rails', 'ASP.NET', 'jQuery', 'Bootstrap', 'Sass', 'Less',
            
            # Databases
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server', 'Cassandra',
            'DynamoDB', 'Neo4j', 'Elasticsearch', 'InfluxDB',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions',
            'Terraform', 'Ansible', 'Chef', 'Puppet', 'Vagrant', 'Nginx', 'Apache',
            
            # Data Science & ML
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas',
            'NumPy', 'Matplotlib', 'Seaborn', 'Jupyter', 'Apache Spark', 'Hadoop', 'Kafka',
            
            # Mobile Development
            'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
            
            # Tools & Frameworks
            'Git', 'SVN', 'JIRA', 'Confluence', 'Slack', 'Trello', 'Asana', 'Figma', 'Sketch',
            'Photoshop', 'Illustrator', 'InDesign', 'Blender', 'Unity', 'Unreal Engine',
            
            # Methodologies
            'Agile', 'Scrum', 'Kanban', 'DevOps', 'CI/CD', 'TDD', 'BDD', 'Microservices',
            'RESTful APIs', 'GraphQL', 'SOAP', 'OAuth', 'JWT'
        ]
    
    def _load_education_keywords(self) -> List[str]:
        """Load education-related keywords"""
        return [
            'Bachelor', 'Master', 'PhD', 'Doctorate', 'Associate', 'Diploma', 'Certificate',
            'B.S.', 'B.A.', 'M.S.', 'M.A.', 'MBA', 'Ph.D.', 'B.Tech', 'M.Tech',
            'University', 'College', 'Institute', 'School', 'Academy'
        ]
    
    def _load_experience_keywords(self) -> List[str]:
        """Load experience-related keywords"""
        return [
            'Software Engineer', 'Developer', 'Programmer', 'Analyst', 'Manager', 'Director',
            'Lead', 'Senior', 'Junior', 'Intern', 'Consultant', 'Architect', 'Specialist',
            'Coordinator', 'Administrator', 'Designer', 'Tester', 'DevOps', 'Data Scientist'
        ]
    
    def parse_resume(self, text: str, filename: str) -> Dict[str, Any]:
        """Parse resume text and extract structured information"""
        
        try:
            # Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Extract basic information
            name = self._extract_name(cleaned_text)
            email = self._extract_email(cleaned_text)
            phone = self._extract_phone(cleaned_text)
            location = self._extract_location(cleaned_text)
            
            # Extract skills
            skills = self._extract_skills(cleaned_text)
            
            # Extract experience
            experience = self._extract_experience(cleaned_text)
            years_experience = self._calculate_years_experience(experience)
            
            # Extract education
            education = self._extract_education(cleaned_text)
            
            # Extract additional information
            certifications = self._extract_certifications(cleaned_text)
            projects = self._extract_projects(cleaned_text)
            languages = self._extract_languages(cleaned_text)
            awards = self._extract_awards(cleaned_text)
            
            # Calculate readability and other metrics
            readability_score = textstat.flesch_reading_ease(cleaned_text)
            
            return {
                'filename': filename,
                'name': name,
                'email': email,
                'phone': phone,
                'location': location,
                'skills': skills,
                'experience': experience,
                'years_experience': years_experience,
                'education': education,
                'certifications': certifications,
                'projects': projects,
                'languages': languages,
                'awards': awards,
                'readability_score': readability_score,
                'text_length': len(cleaned_text),
                'parsed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error parsing resume {filename}: {str(e)}")
            return {
                'filename': filename,
                'name': 'Error parsing resume',
                'email': '',
                'phone': '',
                'location': '',
                'skills': [],
                'experience': [],
                'years_experience': 0,
                'education': [],
                'certifications': [],
                'projects': [],
                'languages': [],
                'awards': [],
                'error': str(e)
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name using NLP and patterns"""
        
        # Try NLP approach first
        if nlp:
            doc = nlp(text[:500])  # Check first 500 characters
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text.strip()
        
        # Fallback to pattern matching
        lines = text.split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            # Skip lines with email or phone
            if '@' in line or re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line):
                continue
            
            # Look for name patterns
            name_pattern = r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?)'
            match = re.search(name_pattern, line)
            if match:
                return match.group(1)
        
        return "Name not found"
    
    def _extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_patterns = [
            r'\+?1?[-.\s]?$$?([0-9]{3})$$?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'$$\d{3}$$\s?\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    return f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
                else:
                    return matches[0]
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location information"""
        
        # Common location patterns
        location_patterns = [
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
            r'([A-Z][a-z]+\s[A-Z][a-z]+,\s*[A-Z]{2})',  # City Name, State
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Country
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        
        # Try NLP approach
        if nlp:
            doc = nlp(text[:1000])
            locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]
            if locations:
                return locations[0]
        
        return ""
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.skills_keywords:
            # Use word boundaries for exact matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        
        # Remove duplicates and sort
        return sorted(list(set(found_skills)))
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience"""
        experience = []
        
        # Split text into sections
        sections = re.split(r'\n(?=\s*(?:EXPERIENCE|WORK|EMPLOYMENT|PROFESSIONAL))', text, flags=re.IGNORECASE)
        
        if len(sections) > 1:
            exp_section = sections[1]
            
            # Extract job entries
            job_pattern = r'([A-Z][^,\n]+?)(?:\s+at\s+|\s+@\s+|\s+-\s+)([A-Z][^,\n]+?)(?:\s+\|\s+|\s+-\s+|\n)([0-9]{4}(?:\s*-\s*(?:[0-9]{4}|Present|Current))?)'
            
            matches = re.findall(job_pattern, exp_section)
            
            for match in matches:
                experience.append({
                    'title': match[0].strip(),
                    'company': match[1].strip(),
                    'duration': match[2].strip(),
                    'description': ''
                })
        
        return experience
    
    def _calculate_years_experience(self, experience: List[Dict[str, str]]) -> int:
        """Calculate total years of experience"""
        total_years = 0
        current_year = datetime.now().year
        
        for exp in experience:
            duration = exp.get('duration', '')
            
            # Extract years from duration
            years = re.findall(r'(\d{4})', duration)
            if len(years) >= 2:
                start_year = int(years[0])
                end_year = int(years[1]) if years[1] != 'Present' else current_year
                total_years += max(0, end_year - start_year)
            elif len(years) == 1:
                # Assume 1 year if only one year mentioned
                total_years += 1
        
        return total_years
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        
        # Education patterns
        edu_pattern = r'((?:Bachelor|Master|PhD|Doctorate|B\.S\.|B\.A\.|M\.S\.|M\.A\.|MBA|Ph\.D\.)[^,\n]*?)(?:\s+(?:from|at|\|)\s+)?([A-Z][^,\n]+?)(?:\s*,?\s*(\d{4}))?'
        
        matches = re.findall(edu_pattern, text, re.IGNORECASE)
        
        for match in matches:
            education.append({
                'degree': match[0].strip(),
                'institution': match[1].strip(),
                'year': match[2].strip() if match[2] else ''
            })
        
        return education
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications"""
        cert_keywords = [
            'AWS Certified', 'Microsoft Certified', 'Google Cloud', 'Cisco', 'CompTIA',
            'PMP', 'Scrum Master', 'Six Sigma', 'ITIL', 'Salesforce', 'Oracle Certified'
        ]
        
        certifications = []
        text_lower = text.lower()
        
        for cert in cert_keywords:
            if cert.lower() in text_lower:
                certifications.append(cert)
        
        return certifications
    
    def _extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information"""
        projects = []
        
        # Look for project sections
        project_section_pattern = r'(?:PROJECTS?|PORTFOLIO)[\s\S]*?(?=\n[A-Z]{2,}|\Z)'
        project_match = re.search(project_section_pattern, text, re.IGNORECASE)
        
        if project_match:
            project_text = project_match.group()
            
            # Extract individual projects
            project_lines = project_text.split('\n')
            current_project = None
            
            for line in project_lines:
                line = line.strip()
                if line and not line.isupper():
                    if current_project is None:
                        current_project = {'name': line, 'description': ''}
                    else:
                        current_project['description'] += ' ' + line
                elif current_project:
                    projects.append(current_project)
                    current_project = None
        
        return projects
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract programming and spoken languages"""
        languages = []
        
        # Programming languages already covered in skills
        # Focus on spoken languages
        spoken_languages = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Hindi', 'Russian'
        ]
        
        text_lower = text.lower()
        for lang in spoken_languages:
            if lang.lower() in text_lower:
                languages.append(lang)
        
        return languages
    
    def _extract_awards(self, text: str) -> List[str]:
        """Extract awards and achievements"""
        awards = []
        
        award_keywords = [
            'award', 'recognition', 'achievement', 'honor', 'prize', 'winner',
            'excellence', 'outstanding', 'top performer', 'employee of'
        ]
        
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            for keyword in award_keywords:
                if keyword in line_lower and len(line.strip()) > 10:
                    awards.append(line.strip())
                    break
        
        return list(set(awards))  # Remove duplicates
