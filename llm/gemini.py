from langchain_google_genai import ChatGoogleGenerativeAI
import os
import google.generativeai as genai

# os.environ["GOOGLE_API_KEY"] = "AIzaSyCPeniE1Tl1F_-VCE58VrO5KfOdi8zS2mI"  # <-- You must assign the key
# genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
# response = llm.invoke("recommend me a BTS song to listen to")
# print(response.text)

from langchain_google_genai import ChatGoogleGenerativeAI
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def create_gemini():
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
