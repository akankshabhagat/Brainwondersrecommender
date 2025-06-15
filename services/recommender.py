

import json
from typing import List, Dict
from langchain_core.output_parsers import JsonOutputParser
from models.schemas import PreferenceExtraction, CareerRecommendation
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from models.career import CAREER_PATHS
from prompts.templates import PREFERENCE_EXTRACTION_PROMPT, CAREER_MAPPING_PROMPT, EXPLANATION_PROMPT, CLARIFYING_QUESTIONS, CONVERSATION_TEMPLATE

class CareerRecommendationSystem:
    def __init__(self, llm):
        self.llm = llm
        self.preference_parser = JsonOutputParser(pydantic_object=PreferenceExtraction)
        self.recommendation_parser = JsonOutputParser(pydantic_object=CareerRecommendation)
        
        # Initialize prompt templates
        self._setup_prompts()

        # Initialize conversation chain for clarifying questions
        self._setup_conversation_chain()
    
    def _setup_prompts(self):
        self.preference_extraction_prompt = PREFERENCE_EXTRACTION_PROMPT
        
        self.career_mapping_prompt = CAREER_MAPPING_PROMPT
        
        self.explanation_prompt = EXPLANATION_PROMPT
        
        self.clarifying_questions = CLARIFYING_QUESTIONS

    def _setup_conversation_chain(self):
        """Setup conversation chain with history for clarifying questions"""
        llm_chain = CONVERSATION_TEMPLATE | self.llm
        
        self.conversation_chain = RunnableWithMessageHistory(
            llm_chain,
            lambda session_id: SQLChatMessageHistory(
                session_id=session_id,
                connection="sqlite:///career_conversations.db"
            ),
            input_messages_key="message",
            history_messages_key="history"
        )
    
    def extract_preferences(self, conversation: str) -> Dict:
        """Extract preferences from conversation text"""
        prompt = self.preference_extraction_prompt.format(conversation=conversation)
        
        response = self.llm.invoke(prompt)
        try:
            # Try to extract JSON from response
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(response_text)
        except:
            # Fallback parsing
            return self._fallback_preference_extraction(conversation)
    
    def recommend_careers(self, preferences: Dict) -> Dict:
        """Map preferences to career recommendations"""
        prompt = self.career_mapping_prompt.format(preferences=json.dumps(preferences))
        
        response = self.llm.invoke(prompt)
        try:
            response_text = response.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(response_text)
        except:
            return self._fallback_career_recommendation(preferences)
    
    def generate_explanations(self, career_path: str, interests: List[str]) -> str:
        """Generate detailed explanation for a career recommendation"""
        prompt = self.explanation_prompt.format(
            career_path=career_path,
            interests=', '.join(interests)
        )
        
        return self.llm.invoke(prompt)
    
    def start_conversation(self, initial_message: str, session_id: str) -> str:
        """Start a conversation to gather more information"""
        config = {"configurable": {"session_id": session_id}}
        
        response = self.conversation_chain.invoke(
            {"message": initial_message}, 
            config=config
        )
        
        return response
    
    def continue_conversation(self, message: str, session_id: str) -> Dict:
        """Continue the conversation and check if ready for recommendation"""
        config = {"configurable": {"session_id": session_id}}
        
        response = self.conversation_chain.invoke(
            {"message": message}, 
            config=config
        )
        
        # Check if the model thinks it's ready for recommendation
        if "READY_FOR_RECOMMENDATION" in response:
            return {
                "status": "ready_for_recommendation",
                "response": response,
                "session_id": session_id
            }
        else:
            return {
                "status": "continue_conversation",
                "response": response,
                "session_id": session_id
            }
        
    def get_conversation_summary(self, session_id: str) -> str:
        """Get the full conversation history for final preference extraction"""
        # Get chat history
        chat_history = SQLChatMessageHistory(
            session_id=session_id,
            connection="sqlite:///career_conversations.db"
        )
        
        # Convert messages to text
        conversation_text = ""
        for message in chat_history.messages:
            if hasattr(message, 'content'):
                conversation_text += f"{message.type}: {message.content}\n"
        
        return conversation_text
    
    def ask_clarifying_questions(self, conversation: str = "", question_type: str = "insufficient_info") -> str:
        """Generate clarifying questions based on the situation"""
        if question_type == "insufficient_info":
            prompt = self.clarifying_questions["insufficient_info"].format()
        else:
            prompt = self.clarifying_questions["general"].format(context=conversation[:200])
        
        return self.llm.invoke(prompt)
    
    def _format_career_database(self) -> str:
        """Format career database for prompt"""
        formatted = ""
        for category, paths in CAREER_PATHS.items():
            formatted += f"\n{category}:\n"
            for path in paths:
                formatted += f"  - {path.name}: {path.description}\n"
                formatted += f"    Skills: {', '.join(path.required_skills)}\n"
                formatted += f"    Roles: {', '.join(path.typical_roles)}\n"
        return formatted
    
    def _fallback_preference_extraction(self, conversation: str) -> Dict:
        """Fallback method if JSON parsing fails"""
        return {
            "interests": [],
            "skills": [],
            "dislikes": [],
            "work_style": "unknown",
            "confidence_score": 0.3
        }
    
    def _fallback_career_recommendation(self, preferences: Dict) -> Dict:
        """Fallback method if recommendation parsing fails"""
        return {
            "career_paths": ["General Business", "Liberal Arts"],
            "match_reasons": ["Broad applicability", "Flexible options"],
            "confidence_score": 0.4
        }
    
    def interactive_recommendation_pipeline(self, initial_input: str, session_id: str = None) -> Dict:
        """Interactive pipeline that handles conversation until ready for recommendation"""
        if session_id is None:
            import uuid
            session_id = f"career_session_{uuid.uuid4().hex[:8]}"
        
        # First, try to extract preferences from initial input
        initial_preferences = self.extract_preferences(initial_input)
        
        # If confidence is high enough, proceed directly to recommendation
        if initial_preferences["confidence_score"] >= 0.7:
            return self._complete_recommendation(initial_preferences, initial_input)
        
        # Otherwise, start interactive conversation
        conversation_response = self.start_conversation(
            f"Based on this initial information: '{initial_input}', I need to ask some clarifying questions to better understand your career preferences.",
            session_id
        )
        
        return {
            "status": "conversation_started",
            "response": conversation_response,
            "session_id": session_id,
            "initial_preferences": initial_preferences
        }
    
    def finalize_recommendation(self, session_id: str) -> Dict:
        """Generate final recommendation based on complete conversation"""
        
        conversation_text = self.get_conversation_summary(session_id)
        
       
        preferences = self.extract_preferences(conversation_text)
        
        return self._complete_recommendation(preferences, conversation_text)
    
    def _complete_recommendation(self, preferences: Dict, conversation: str) -> Dict:
        """Complete the recommendation process"""
       
        recommendations = self.recommend_careers(preferences)
        
      
        explanations = []
        for i, career_path in enumerate(recommendations["career_paths"]):
            match_reason = recommendations["match_reasons"][i] if i < len(recommendations["match_reasons"]) else "Good general fit"
            explanation = self.generate_explanations(career_path, preferences.get("interests", []))
            explanations.append({
                "career_path": career_path,
                "explanation": explanation,
                "match_reason": match_reason
            })
        
        return {
            "status": "complete",
            "preferences": preferences,
            "recommendations": recommendations,
            "explanations": explanations
        }
    
    def full_recommendation_pipeline(self, conversation: str) -> Dict:
        """Complete pipeline from conversation to recommendations"""
        # Step 1: Extract preferences
        preferences = self.extract_preferences(conversation)
        
        # Step 2: Check if we need clarifying questions
        if preferences["confidence_score"] < 0.6:
            questions = self.ask_clarifying_questions(conversation)
            print("Need more information. Questions to ask:")
            print(questions)
            return {
                "status": "needs_clarification",
                "questions": questions,
                "extracted_preferences": preferences
            }
        
        # Step 3: Get recommendations
        recommendations = self.recommend_careers(preferences)
        
        # Step 4: Generate explanations
        explanations = []
        for i, career_path in enumerate(recommendations["career_paths"]):
            match_reason = recommendations["match_reasons"][i] if i < len(recommendations["match_reasons"]) else "Good general fit"
            explanation = self.generate_explanations(career_path, preferences.get("interests", []))
            explanations.append({
                "career_path": career_path,
                "explanation": explanation,
                "match_reason": match_reason
            })
        
        return {
            "status": "complete",
            "preferences": preferences,
            "recommendations": recommendations,
            "explanations": explanations
        }