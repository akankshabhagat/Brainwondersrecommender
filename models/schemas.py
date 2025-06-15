from typing import List
from pydantic import BaseModel, Field

class PreferenceExtraction(BaseModel):
    interests: List[str] = Field(description="List of interests mentioned")
    skills: List[str] = Field(description="List of skills mentioned")
    dislikes: List[str] = Field(description="List of things the person dislikes")
    work_style: str = Field(description="Preferred work style (e.g., collaborative, independent, creative)")
    confidence_score: float = Field(description="Confidence in extraction (0.0-1.0)")

class CareerRecommendation(BaseModel):
    career_paths: List[str] = Field(description="List of recommended career paths")
    match_reasons: List[str] = Field(description="Reasons for each recommendation")
    confidence_score: float = Field(description="Overall confidence in recommendations")

class ExplanationOutput(BaseModel):
    """Schema for career explanation output"""
    explanation: str = Field(description="Detailed explanation for the career recommendation")

class ClarifyingQuestionsOutput(BaseModel):
    """Schema for clarifying questions output"""
    questions: List[str] = Field(description="List of clarifying questions to ask the user")