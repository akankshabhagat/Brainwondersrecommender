
from services.recommender import CareerRecommendationSystem
from llm.gemini import create_gemini
from dotenv import load_dotenv
import os
load_dotenv()
llm = create_gemini()

recommender = CareerRecommendationSystem(llm)


fallback_input = """
Counselor:
Hi Akanksha, I’m glad you reached out are you excited to explore some career options?.

Student:
Um, to be honest, I’m really confused . I feel like everyone around me knows what they want to do, and I'm just… lost.
"""

conversation_file = "conversation.txt"

if os.path.exists(conversation_file):
    with open(conversation_file, "r", encoding="utf-8") as file:
        file_content = file.read().strip()
        initial_input = file_content if file_content else fallback_input
else:
    initial_input = fallback_input

result = recommender.interactive_recommendation_pipeline(initial_input)

if result["status"] == "conversation_started":
    print("Bot:", result["response"].content)
    session_id = result["session_id"]
    
    while True:
        user_input = input("You: ")
        
        conversation_result = recommender.continue_conversation(user_input, session_id)
        print("Bot:", conversation_result["response"].content)

        if conversation_result["status"] == "ready_for_recommendation":
            final_recommendation = recommender.finalize_recommendation(session_id)
            print("\nFinal Career Recommendations:")
            for explanation in final_recommendation["explanations"]:
                print(f"\n- {explanation['career_path']}")
                print(f"  Explanation: {explanation['explanation']}")
                print(f"  Match Reason: {explanation['match_reason']}")
            break
elif result["status"] == "complete":
    print("Direct recommendations generated!")
    for explanation in result["explanations"]:
        print(f"\n-{explanation['career_path']}")
        print(f" Explanation: {explanation['explanation']}")