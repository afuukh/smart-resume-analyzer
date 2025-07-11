import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from typing import Dict, List, Any, Tuple
import logging

class JobMatcher:
    """Advanced job matching using multiple algorithms and scoring methods"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000,
            lowercase=True
        )
        
        # Weight factors for different matching components
        self.weights = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.2,
            'keywords': 0.1
        }
    
    def calculate_match_score(self, resume_text: str, job_description: str, 
                            job_title: str = "", required_skills: str = "") -> Dict[str, Any]:
        """
        Calculate comprehensive match score between resume and job description
        
        Args:
            resume_text: Full text of the resume
            job_description: Job description text
            job_title: Specific job title
            required_skills: Comma-separated required skills
            
        Returns:
            Dictionary containing various match scores and analysis
        """
        
        try:
            # Parse required skills
            skills_list = [skill.strip() for skill in required_skills.split(',') if skill.strip()]
            
            # Calculate individual component scores
            skill_score = self._calculate_skills_match(resume_text, skills_list, job_description)
            experience_score = self._calculate_experience_match(resume_text, job_description, job_title)
            education_score = self._calculate_education_match(resume_text, job_description)
            keyword_score = self._calculate_keyword_match(resume_text, job_description)
            semantic_score = self._calculate_semantic_similarity(resume_text, job_description)
            
            # Calculate weighted overall score
            overall_score = (
                skill_score * self.weights['skills'] +
                experience_score * self.weights['experience'] +
                education_score * self.weights['education'] +
                keyword_score * self.weights['keywords']
            )
            
            # Boost score with semantic similarity
            final_score = (overall_score * 0.8) + (semantic_score * 0.2)
            
            # Extract matched keywords and skills
            matched_keywords = self._extract_matched_keywords(resume_text, job_description)
            matched_skills = self._extract_matched_skills(resume_text, skills_list)
            missing_skills = [skill for skill in skills_list if skill not in matched_skills]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                skill_score, experience_score, education_score, missing_skills
            )
            
            return {
                'match_score': min(final_score, 1.0),  # Cap at 1.0
                'skill_match_score': skill_score,
                'experience_match_score': experience_score,
                'education_match_score': education_score,
                'keyword_match_score': keyword_score,
                'semantic_similarity_score': semantic_score,
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'keywords_matched': matched_keywords,
                'recommendations': recommendations,
                'match_breakdown': {
                    'skills': f"{skill_score:.1%}",
                    'experience': f"{experience_score:.1%}",
                    'education': f"{education_score:.1%}",
                    'keywords': f"{keyword_score:.1%}",
                    'semantic': f"{semantic_score:.1%}"
                }
            }
            
        except Exception as e:
            logging.error(f"Error calculating match score: {str(e)}")
            return {
                'match_score': 0.0,
                'skill_match_score': 0.0,
                'experience_match_score': 0.0,
                'education_match_score': 0.0,
                'keyword_match_score': 0.0,
                'semantic_similarity_score': 0.0,
                'matched_skills': [],
                'missing_skills': [],
                'keywords_matched': [],
                'recommendations': ['Error in matching process'],
                'error': str(e)
            }
    
    def _calculate_skills_match(self, resume_text: str, required_skills: List[str], 
                               job_description: str) -> float:
        """Calculate skills matching score"""
        
        if not required_skills:
            return 0.5  # Neutral score if no specific skills required
        
        resume_lower = resume_text.lower()
        matched_skills = 0
        total_skills = len(required_skills)
        
        for skill in required_skills:
            skill_lower = skill.lower()
            
            # Exact match
            if skill_lower in resume_lower:
                matched_skills += 1
            # Fuzzy match for similar skills
            elif any(fuzz.ratio(skill_lower, word) > 80 for word in resume_lower.split()):
                matched_skills += 0.8
        
        # Bonus for additional relevant skills mentioned in job description
        job_skills = self._extract_skills_from_text(job_description)
        bonus_skills = 0
        
        for skill in job_skills:
            if skill.lower() in resume_lower and skill not in required_skills:
                bonus_skills += 0.1
        
        base_score = matched_skills / total_skills if total_skills > 0 else 0
        final_score = min(base_score + (bonus_skills * 0.1), 1.0)
        
        return final_score
    
    def _calculate_experience_match(self, resume_text: str, job_description: str, 
                                  job_title: str) -> float:
        """Calculate experience matching score"""
        
        # Extract years of experience from resume
        resume_years = self._extract_years_experience(resume_text)
        
        # Extract required experience from job description
        required_years = self._extract_required_experience(job_description)
        
        # Calculate experience match
        if required_years == 0:
            experience_score = 0.7  # Neutral score if no specific requirement
        elif resume_years >= required_years:
            # Perfect match or overqualified
            experience_score = min(1.0, 0.8 + (resume_years - required_years) * 0.05)
        else:
            # Underqualified but give partial credit
            experience_score = max(0.2, resume_years / required_years * 0.8)
        
        # Check for relevant job titles and roles
        title_match = self._calculate_title_match(resume_text, job_title, job_description)
        
        # Combine experience and title matching
        final_score = (experience_score * 0.7) + (title_match * 0.3)
        
        return min(final_score, 1.0)
    
    def _calculate_education_match(self, resume_text: str, job_description: str) -> float:
        """Calculate education matching score"""
        
        # Extract education requirements from job description
        required_education = self._extract_education_requirements(job_description)
        
        # Extract candidate's education from resume
        candidate_education = self._extract_candidate_education(resume_text)
        
        if not required_education:
            return 0.7  # Neutral score if no specific requirement
        
        education_score = 0.0
        
        # Check degree level matching
        degree_levels = {
            'high school': 1, 'diploma': 1,
            'associate': 2, 'bachelor': 3, 'master': 4, 'mba': 4,
            'phd': 5, 'doctorate': 5
        }
        
        required_level = 0
        candidate_level = 0
        
        for req in required_education:
            for degree, level in degree_levels.items():
                if degree in req.lower():
                    required_level = max(required_level, level)
        
        for edu in candidate_education:
            for degree, level in degree_levels.items():
                if degree in edu.lower():
                    candidate_level = max(candidate_level, level)
        
        if candidate_level >= required_level:
            education_score = 1.0
        elif candidate_level > 0:
            education_score = candidate_level / required_level * 0.8
        else:
            education_score = 0.3  # Some credit for any education
        
        return min(education_score, 1.0)
    
    def _calculate_keyword_match(self, resume_text: str, job_description: str) -> float:
        """Calculate keyword matching score using TF-IDF"""
        
        try:
            # Prepare texts
            texts = [resume_text, job_description]
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
            
        except Exception as e:
            logging.error(f"Error in keyword matching: {str(e)}")
            return 0.0
    
    def _calculate_semantic_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity between texts"""
        
        # Simple implementation using word overlap and TF-IDF
        # In production, you might want to use more advanced NLP models
        
        try:
            # Tokenize and clean texts
            resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
            job_words = set(re.findall(r'\b\w+\b', job_description.lower()))
            
            # Calculate Jaccard similarity
            intersection = len(resume_words.intersection(job_words))
            union = len(resume_words.union(job_words))
            
            jaccard_similarity = intersection / union if union > 0 else 0
            
            # Combine with TF-IDF similarity for better results
            tfidf_similarity = self._calculate_keyword_match(resume_text, job_description)
            
            # Weighted combination
            semantic_score = (jaccard_similarity * 0.3) + (tfidf_similarity * 0.7)
            
            return semantic_score
            
        except Exception as e:
            logging.error(f"Error in semantic similarity: {str(e)}")
            return 0.0
    
    def _extract_years_experience(self, text: str) -> int:
        """Extract years of experience from resume text"""
        
        # Patterns to match experience mentions
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'experience.*?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience'
        ]
        
        years = []
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            years.extend([int(match) for match in matches])
        
        # Return the maximum years found, or 0 if none
        return max(years) if years else 0
    
    def _extract_required_experience(self, job_description: str) -> int:
        """Extract required years of experience from job description"""
        
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience\s*required',
            r'minimum\s*(?:of\s*)?(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:relevant\s*)?experience',
            r'require[sd]?\s*(\d+)\+?\s*years?'
        ]
        
        years = []
        text_lower = job_description.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            years.extend([int(match) for match in matches])
        
        return max(years) if years else 0
    
    def _calculate_title_match(self, resume_text: str, job_title: str, 
                              job_description: str) -> float:
        """Calculate job title matching score"""
        
        if not job_title:
            return 0.5
        
        resume_lower = resume_text.lower()
        job_title_lower = job_title.lower()
        
        # Direct title match
        if job_title_lower in resume_lower:
            return 1.0
        
        # Fuzzy matching for similar titles
        resume_titles = re.findall(r'(?:^|\n)([^,\n]*(?:engineer|developer|manager|analyst|director|lead|senior|junior)[^,\n]*)', resume_lower)
        
        max_similarity = 0
        for title in resume_titles:
            similarity = fuzz.ratio(job_title_lower, title.strip()) / 100
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _extract_education_requirements(self, job_description: str) -> List[str]:
        """Extract education requirements from job description"""
        
        education_section = re.search(
            r'(?:education|qualifications|requirements)[\s\S]*?(?=\n[A-Z]|\Z)',
            job_description, re.IGNORECASE
        )
        
        if education_section:
            text = education_section.group()
            degrees = re.findall(
                r'(bachelor|master|phd|doctorate|mba|associate|diploma)[\w\s]*',
                text, re.IGNORECASE
            )
            return degrees
        
        return []
    
    def _extract_candidate_education(self, resume_text: str) -> List[str]:
        """Extract candidate's education from resume"""
        
        education_patterns = [
            r'(bachelor[\w\s]*)',
            r'(master[\w\s]*)',
            r'(phd|ph\.d\.?)',
            r'(doctorate)',
            r'(mba)',
            r'(associate[\w\s]*)',
            r'(diploma)'
        ]
        
        education = []
        text_lower = resume_text.lower()
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text_lower)
            education.extend(matches)
        
        return education
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract technical skills from text"""
        
        # Common technical skills (subset for matching)
        skills_keywords = [
            'python', 'java', 'javascript', 'react', 'angular', 'node.js',
            'sql', 'mysql', 'postgresql', 'mongodb', 'aws', 'azure',
            'docker', 'kubernetes', 'git', 'machine learning', 'ai'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_matched_keywords(self, resume_text: str, job_description: str) -> List[str]:
        """Extract keywords that appear in both resume and job description"""
        
        # Get important keywords from job description
        job_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))
        resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
        
        # Common stop words to exclude
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
            'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy',
            'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'
        }
        
        # Find intersection excluding stop words
        matched = job_words.intersection(resume_words) - stop_words
        
        # Filter for meaningful keywords (length > 3)
        meaningful_matches = [word for word in matched if len(word) > 3]
        
        return sorted(meaningful_matches)
    
    def _extract_matched_skills(self, resume_text: str, required_skills: List[str]) -> List[str]:
        """Extract skills from required list that appear in resume"""
        
        matched_skills = []
        resume_lower = resume_text.lower()
        
        for skill in required_skills:
            if skill.lower() in resume_lower:
                matched_skills.append(skill)
        
        return matched_skills
    
    def _generate_recommendations(self, skill_score: float, experience_score: float,
                                education_score: float, missing_skills: List[str]) -> List[str]:
        """Generate recommendations based on matching scores"""
        
        recommendations = []
        
        if skill_score < 0.6:
            recommendations.append("Consider candidates with stronger technical skill alignment")
            if missing_skills:
                recommendations.append(f"Key missing skills: {', '.join(missing_skills[:3])}")
        
        if experience_score < 0.5:
            recommendations.append("Candidate may need additional experience for this role")
        elif experience_score > 0.9:
            recommendations.append("Candidate appears overqualified - consider for senior roles")
        
        if education_score < 0.5:
            recommendations.append("Educational background may not fully align with requirements")
        
        if skill_score > 0.8 and experience_score > 0.7:
            recommendations.append("Strong candidate - recommend for interview")
        
        if not recommendations:
            recommendations.append("Well-balanced candidate profile")
        
        return recommendations
