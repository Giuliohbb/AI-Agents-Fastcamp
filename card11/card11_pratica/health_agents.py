from crewai import Agent
from crewai_tools import SerperDevTool
import streamlit as st
import re

# Web search tool for agents to retrieve real-time medical content
search_tool = SerperDevTool()

# Defines multiple specialized agents for healthcare conversation and research
class HealthAgents:

    def question_analyst(self):
        return Agent(
            role='Patient Question Analyst',
            goal='Understand and structure the patient question clearly and accurately',
            backstory='An empathetic virtual assistant trained to identify topics and intent in medical queries.',
            tools=[],
            verbose=True,
            allow_delegation=False
        )

    def medical_researcher(self):
        return Agent(
            role='Medical Information Researcher',
            goal='Retrieve accurate and current medical information from reliable public health sources',
            backstory='An expert in searching, filtering, and summarizing peer-reviewed health content in layman-friendly terms.',
            tools=[search_tool],
            verbose=True
        )

    def response_specialist(self):
        return Agent(
            role='Patient Communication Specialist',
            goal='Formulate human-centered, clear, and non-alarming responses to medical questions',
            backstory='An AI trained to transform scientific data into emotionally intelligent answers for the general public.',
            tools=[],
            verbose=True
        )

# Handles redirecting agent output to Streamlit interface
class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['green', 'blue', 'orange']
        self.color_index = 0

    def write(self, data):
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)
        if "Patient Question Analyst" in cleaned_data:
            cleaned_data = cleaned_data.replace("Patient Question Analyst", f":green[Question Analyst]")
        if "Medical Information Researcher" in cleaned_data:
            cleaned_data = cleaned_data.replace("Medical Information Researcher", f":blue[Researcher]")
        if "Patient Communication Specialist" in cleaned_data:
            cleaned_data = cleaned_data.replace("Patient Communication Specialist", f":orange[Responder]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []

    def flush(self):
        pass
