from crewai import Crew
from card11_pratica.health_agents import HealthAgents, StreamToExpander
from card11_pratica.health_tasks import HealthTasks
import streamlit as st
import sys
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# Core app logic class that organizes the Crew
class HealthCrew:
    def __init__(self, user_question):
        self.user_question = user_question
        self.output_area = st.empty()

    def run(self):
        agents = HealthAgents()
        tasks = HealthTasks()

        analyst = agents.question_analyst()
        researcher = agents.medical_researcher()
        responder = agents.response_specialist()

        task1 = tasks.interpret_question(self.user_question, analyst)
        task2 = tasks.gather_medical_info(task1.output, researcher)
        task3 = tasks.draft_patient_friendly_response(responder)

        crew = Crew(
            agents=[analyst, researcher, responder],
            tasks=[task1, task2, task3],
            verbose=True
        )

        result = crew.kickoff()
        self.output_area.markdown(result)
        return result

# Streamlit interface
if __name__ == "__main__":
    st.set_page_config(page_title="Virtual Health Assistant", layout="centered")
    st.title("🩺 Virtual Health Assistant")
    st.markdown("""
        Ask your health-related question below and our intelligent agent team will provide a helpful, compassionate response.
    """)

    question = st.text_area(
        "Your Question:",
        placeholder="e.g. What are the early symptoms of high blood pressure?",
        height=140
    )

    if st.button("Ask AI Assistant"):
        if question.strip():
            with st.status("🤖 Working on your answer...", expanded=True):
                sys.stdout = StreamToExpander(st)
                assistant = HealthCrew(question)
                result = assistant.run()
                st.subheader("📋 Answer", anchor=False)
                st.markdown(result)
        else:
            st.warning("⚠️ Please enter a valid health question.")
