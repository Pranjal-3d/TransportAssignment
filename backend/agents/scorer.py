import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

# Define models for structured output

class JDRequirements(BaseModel):
    skills: List[str] = Field(description="List of mandatory and preferred skills")
    experience_years: str = Field(description="Required years of experience")
    domain: str = Field(description="Primary industry or domain")
    education: List[str] = Field(description="Required education levels or certifications")
    typical_projects: List[str] = Field(description="Types of projects expected")
    summary: str = Field(description="High-level summary of the role")

class DimensionScore(BaseModel):
    score: int = Field(description="Score from 0 to 10")
    justification: str = Field(description="One-line justification for the score")

class ScoringResult(BaseModel):
    skills_match: DimensionScore
    experience_relevance: DimensionScore
    education_certs: DimensionScore
    project_portfolio: DimensionScore
    communication_quality: DimensionScore
    total_weighted_score: float = Field(description="Weighted sum based on proportions: Skills(30%), Exp(25%), Edu(15%), Proj(20%), Comm(10%)")
    hire_recommendation: str = Field(description="Hire/No-Hire and brief reason")

class HRScorer:
    def __init__(self, api_key: str):
        model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash-latest")
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
        )
        self.jd_parser = PydanticOutputParser(pydantic_object=JDRequirements)
        self.score_parser = PydanticOutputParser(pydantic_object=ScoringResult)

    def parse_jd(self, jd_text: str) -> JDRequirements:
        prompt = PromptTemplate(
            template="Extract the following requirements from the Job Description:\n{format_instructions}\n\nJD Text:\n{jd_text}",
            input_variables=["jd_text"],
            partial_variables={"format_instructions": self.jd_parser.get_format_instructions()}
        )
        chain = prompt | self.llm | self.jd_parser
        return chain.invoke({"jd_text": jd_text})

    def score_candidate(self, jd_reqs: JDRequirements, candidate_text: str) -> ScoringResult:
        rubric_description = """
        Scoring Rubric:
        1. Skills Match (30% weight): 0 (Poor, <30% match), 5 (Average, 50-70%), 10 (Excellent, >85%).
        2. Experience Relevance (25% weight): 0 (Unrelated), 5 (Adjacent domain), 10 (Exact domain & seniority).
        3. Education & Certs (15% weight): 0 (Does not meet min), 5 (Meets minimum), 10 (Exceeds + extra certs).
        4. Project / Portfolio (20% weight): 0 (No evidence), 5 (1-2 generic projects), 10 (Strong relevant portfolio).
        5. Communication Quality (10% weight): 0 (Poor structure/grammar), 5 (Adequate clarity), 10 (Crisp, structured, impactful).
        """
        
        prompt = PromptTemplate(
            template="""
            Evalute the candidate against the following Job Description requirements and rubric.
            
            JD Requirements:
            {jd_reqs}
            
            Candidate Profile:
            {candidate_text}
            
            {rubric_description}
            
            Return the scores and justifications in the following format:
            {format_instructions}
            
            Note: The total_weighted_score should be calculated as:
            (Skills*0.30 + Experience*0.25 + Education*0.15 + Projects*0.20 + Communication*0.10)
            """,
            input_variables=["jd_reqs", "candidate_text", "rubric_description"],
            partial_variables={"format_instructions": self.score_parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | self.score_parser
        return chain.invoke({
            "jd_reqs": jd_reqs.model_dump_json(),
            "candidate_text": candidate_text,
            "rubric_description": rubric_description
        })
