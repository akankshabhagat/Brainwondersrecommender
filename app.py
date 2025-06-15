import streamlit as st
import os
from dotenv import load_dotenv
from services.recommender import CareerRecommendationSystem
from llm.gemini import create_gemini

# Load environment variables
load_dotenv()

# Initialize LLM and recommender
llm = create_gemini()
recommender = CareerRecommendationSystem(llm)

# Fallback conversation
fallback_input = """
Counselor:
Hi Akanksha, I’m glad you reached out. Are you excited to explore some career options?

Student:
Um, to be honest, I’m really confused. I feel like everyone around me knows what they want to do, and I'm just… lost.
"""

conversation_file = "conversation.txt"
if os.path.exists(conversation_file):
    with open(conversation_file, "r", encoding="utf-8") as file:
        file_content = file.read().strip()
        initial_input = file_content if file_content else fallback_input
else:
    initial_input = fallback_input

# Streamlit layout
st.set_page_config(page_title="Career Recommender", page_icon="🎯")
st.title("🎯 Career Guidance Chatbot")

# Initialize session state
if "session_id" not in st.session_state:
    with st.spinner("Starting conversation..."):
        result = recommender.interactive_recommendation_pipeline(initial_input)
    st.session_state.session_id = result.get("session_id")
    st.session_state.chat_history = [("Bot", result["response"].content)]
    st.session_state.recommendations = []
    st.session_state.status = result["status"]
elif "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.recommendations = []

# Show chat messages
for role, msg in st.session_state.chat_history:
    with st.chat_message(role.lower()):
        st.markdown(msg)

# Chat input
if st.session_state.status != "complete" and not st.session_state.recommendations:
    user_input = st.chat_input("Your response...")
    if user_input:
        st.session_state.chat_history.append(("User", user_input))

        with st.spinner("Thinking..."):
            response = recommender.continue_conversation(user_input, st.session_state.session_id)

        bot_message = response["response"].content
        st.session_state.chat_history.append(("Bot", bot_message))
        st.session_state.status = response["status"]

        if st.session_state.status == "ready_for_recommendation":
            with st.spinner("Generating your career recommendations..."):
                final_result = recommender.finalize_recommendation(st.session_state.session_id)
            st.session_state.recommendations = final_result["explanations"]

# Show recommendations
if st.session_state.status == "complete" or st.session_state.recommendations:
    if not st.session_state.recommendations:
        with st.spinner("Generating career recommendations..."):
            result = recommender.interactive_recommendation_pipeline(initial_input)
        st.session_state.recommendations = result["explanations"]

    st.markdown("## ✅ Final Career Recommendations")
    for rec in st.session_state.recommendations:
        st.markdown(f"""
- **{rec['career_path']}**
  - 📘 **Explanation:** {rec['explanation']}
  - 🎯 **Why it's a match:** {rec['match_reason']}
""")

# Reset option
if st.button("🔁 Restart Conversation"):
    for key in ["session_id", "chat_history", "recommendations", "status"]:
        st.session_state.pop(key, None)
    st.rerun()
