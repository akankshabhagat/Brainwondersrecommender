
#  Career Counselling Chatbot (/bot)

This project is my submission for the **Barinwonder Career Counselling Assignment**.

It is a conversational chatbot that helps students identify the most suitable career paths based on their interests, preferences, and concerns — just like a real career counsellor would. The chatbot intelligently asks follow-up questions and provides personalized suggestions using LLMs (Large Language Models).

---

##  Features

- 💬 Uses **Gemini (Google's LLM)** via LangChain for conversation and reasoning
- 🧠 Plans to support **Mistral and LLaMA** models for more diverse responses
- 🗣️ Simulates a real counsellor's dialogue with relevant, NLP-powered questions
- 📈 Uses a **confidence score pipeline** to assess clarity and satisfaction
- 🖥️ Works via both **Command Line Interface (CLI)** and **Streamlit UI**
- 📊 Embedding-based job matching (coming soon)
- 🏃‍♂️ Plans to improve response speed (Gemini can be slow on Streamlit)

---

##  Tech Stack

- Python
- LangChain
- Gemini API (via Google AI Studio)
- Streamlit (for the web UI)
- MongoDB (for user session and profile saving)
- Future: Mistral, LLaMA, Embedding Search (FAISS or similar)

---

##  Logic Pipeline (How it works)





##  Screenshots

###  CLI Version

A simple command-line interaction that helps debug and test the core logic.

![CLI Screenshot](https://github.com/user-attachments/assets/d1ddfacf-e425-4a99-9de2-3103d9cc667b)

---

###  Streamlit UI

A more user-friendly version for non-technical users. Conversation is smoother and easier to follow.

![Streamlit Screenshot 1](https://github.com/user-attachments/assets/3b2cc131-168e-4106-82e1-df2778698878)
![Streamlit Screenshot 2](https://github.com/user-attachments/assets/699f8f4f-22e8-49db-8b80-801f097ba1d6)

---

## 🎥 Demo Video 

https://drive.google.com/file/d/1VdxBaniVgAqVmo2HHvHkWhpVqH8aeecA/view?usp=sharing

---

##  Future Enhancements

* ✅ Integrate faster LLMs like Mistral and LLaMA
* ✅ Add embeddings-based job exploration (searchable job descriptions)
* ✅ Deploy on a cloud platform (Streamlit Cloud / HuggingFace Spaces / AWS)
* ✅ Better confidence tracking and satisfaction metrics
* ✅ Resume parsing + profile saving for more detailed analysis

---

##  Project Structure

```
/bot
├── services/
│   └── recommender.py      # Core recommendation logic
├── llm/
│   └── gemini.py           # Gemini LLM initialization
├── app.py                  # Streamlit UI
├── main.py                 # CLI logic
├── conversation.txt        # Optional saved dialogue
└── README.md               # This file
```

---



