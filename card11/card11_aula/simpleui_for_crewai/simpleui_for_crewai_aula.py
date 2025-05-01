# Commented code from the card 11

# Required packages for this script:
# pip install crewai==0.22.5 streamlit==1.32.2

import streamlit as st  # Streamlit for building the UI
import os  # For environment variable access

# Importing necessary classes from CrewAI and LangChain
from crewai import Crew, Process, Agent, Task
from langchain_core.callbacks import BaseCallbackHandler
from typing import TYPE_CHECKING, Any, Dict, Optional
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv  # For loading environment variables from a .env file

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI language model with the API key from environment variables
llm = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"])

# Avatars for different roles in the chat
avatars = {
    "Writer": "https://cdn-icons-png.flaticon.com/512/320/320336.png",
    "Reviewer": "https://cdn-icons-png.freepik.com/512/9408/9408201.png"
}

# Custom callback handler to handle interactions between agents and the Streamlit UI
class MyCustomHandler(BaseCallbackHandler):
    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name  # Name of the agent (e.g., Writer or Reviewer)

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """Triggered when a chain starts. Adds the input to the chat."""
        st.session_state.messages.append({"role": "assistant", "content": inputs['input']})
        st.chat_message("assistant").write(inputs['input'])

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Triggered when a chain ends. Adds the output to the chat."""
        st.session_state.messages.append({"role": self.agent_name, "content": outputs['output']})
        st.chat_message(self.agent_name, avatar=avatars[self.agent_name]).write(outputs['output'])

# Define the Writer agent
writer = Agent(
    role='Blog Post Writer',
    backstory='''You are a blog post writer who is capable of writing a travel blog.
                 You generate one iteration of an article once at a time.
                 You never provide review comments.
                 You are open to reviewer comments and willing to iterate its article based on these comments.''',
    goal="Write and iterate a decent blog post.",
    llm=llm,  # Language model used by the agent
    callbacks=[MyCustomHandler("Writer")],  # Custom callback handler for the Writer
)

# Define the Reviewer agent
reviewer = Agent(
    role='Blog Post Reviewer',
    backstory='''You are a professional article reviewer and very helpful for improving articles.
                 You review articles and give change recommendations to make the article more aligned with user requests.
                 You will give review comments upon reading the entire article, so you will not generate anything when the article is not completely delivered.
                 You never generate blogs by itself.''',
    goal="List builtins about what needs to be improved in a specific blog post. Do not give comments on a summary or abstract of an article.",
    llm=llm,  # Language model used by the agent
    callbacks=[MyCustomHandler("Reviewer")],  # Custom callback handler for the Reviewer
)

# Streamlit UI title
st.title("💬 CrewAI Writing Studio")

# Initialize session state for storing chat messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "What blog post do you want us to write?"}]

# Display all previous messages in the chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input from the chat input box
if prompt := st.chat_input():
    # Add the user's input to the session state and display it in the chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Define the task for the Writer agent
    task1 = Task(
        description=f"Write a blog post of {prompt}.",
        agent=writer,
        expected_output="an article under 300 words."
    )

    # Define the task for the Reviewer agent
    task2 = Task(
        description="List review comments for improvement from the entire content of the blog post to make it more viral on social media.",
        agent=reviewer,
        expected_output="Builtin points about where need to be improved."
    )

    # Create a Crew instance to manage the tasks and agents
    project_crew = Crew(
        tasks=[task1, task2],  # Tasks to be executed
        agents=[writer, reviewer],  # Agents involved in the process
        manager_llm=llm,  # Manager language model
        process=Process.hierarchical  # Hierarchical management approach
    )

    # Kick off the process and get the final result
    final = project_crew.kickoff()

    # Display the final result in the chat
    result = f"## Here is the Final Result \n\n {final}"
    st.session_state.messages.append({"role": "assistant", "content": result})
    st.chat_message("assistant").write(result)
