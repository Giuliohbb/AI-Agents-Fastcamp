# Commented code from the card 11
# Importing necessary libraries
from crewai import Agent
import re
import streamlit as st
from langchain_community.llms import OpenAI
from crewai_tools import SerperDevTool

## My initial parsing code using callback handler to print to app
# def streamlit_callback(step_output):
#     # This function will be called after each step of the agent's execution
#     st.markdown("---")
#     for step in step_output:
#         if isinstance(step, tuple) and len(step) == 2:
#             action, observation = step
#             if isinstance(action, dict) and "tool" in action and "tool_input" in action and "log" in action:
#                 st.markdown(f"# Action")
#                 st.markdown(f"**Tool:** {action['tool']}")
#                 st.markdown(f"**Tool Input** {action['tool_input']}")
#                 st.markdown(f"**Log:** {action['log']}")
#                 st.markdown(f"**Action:** {action['Action']}")
#                 st.markdown(
#                     f"**Action Input:** ```json\n{action['tool_input']}\n```")
#             elif isinstance(action, str):
#                 st.markdown(f"**Action:** {action}")
#             else:
#                 st.markdown(f"**Action:** {str(action)}")

#             st.markdown(f"**Observation**")
#             if isinstance(observation, str):
#                 observation_lines = observation.split('\n')
#                 for line in observation_lines:
#                     if line.startswith('Title: '):
#                         st.markdown(f"**Title:** {line[7:]}")
#                     elif line.startswith('Link: '):
#                         st.markdown(f"**Link:** {line[6:]}")
#                     elif line.startswith('Snippet: '):
#                         st.markdown(f"**Snippet:** {line[9:]}")
#                     elif line.startswith('-'):
#                         st.markdown(line)
#                     else:
#                         st.markdown(line)
#             else:
#                 st.markdown(str(observation))
#         else:
#             st.markdown(step)


# This class defines the agents used in the trip planning process.
# Each agent has a specific role, goal, and backstory.
# The agents are designed to work together to provide a comprehensive travel experience.
class TripAgents(): 

    def city_selection_agent(self):
        return Agent(
            role='City Selection Expert', # Role of the agent
            goal='Select the best city based on weather, season, and prices', # Goal of the agent
            # The backstory provides context for the agent's expertise and approach.
            backstory='An expert in analyzing travel data to pick ideal destinations',
            tools=[
                SerperDevTool(), # Tool used by the agent to search the internet
            ],
            verbose=True,
            # step_callback=streamlit_callback,
        )
    # The local_expert agent is designed to provide in-depth knowledge about a specific city.
    # It gathers information about attractions, customs, and events to enhance the travel experience.
    # The travel_concierge agent is responsible for creating detailed travel itineraries,
    # including budget and packing suggestions.
    # This agent focuses on logistics and planning to ensure a smooth travel experience.
    # The verbose parameter is set to True to enable detailed output during the agent
    def local_expert(self): 
        return Agent(
            role='Local Expert at this city',
            goal='Provide the BEST insights about the selected city',
            backstory="""A knowledgeable local guide with extensive information
        about the city, it's attractions and customs""",
            tools=[
                SerperDevTool(),
            ],
            verbose=True,
            # step_callback=streamlit_callback,
        )

    def travel_concierge(self):
        return Agent(
            role='Amazing Travel Concierge',
            goal="""Create the most amazing travel itineraries with budget and 
        packing suggestions for the city""",
            backstory="""Specialist in travel planning and logistics with 
        decades of experience""",
            tools=[
                SerperDevTool(),
            ],
            verbose=True,
            # step_callback=streamlit_callback,
        )

###########################################################################################
# Print agent process to Streamlit app container                                          #
# This portion of the code is adapted from @AbubakrChan; thank you!                       #
# https://github.com/AbubakrChan/crewai-UI-business-product-launch/blob/main/main.py#L210 #
###########################################################################################

# This class is used to stream the output of the agents to a Streamlit expander.
# It filters out ANSI escape codes and formats the output for better readability.
class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange']  # Define a list of colors
        self.color_index = 0  # Initialize color index

    # The write method is called to write data to the expander.
    # It filters out ANSI escape codes and formats the output based on specific phrases.
    # It also checks for task information and updates the expander accordingly.
    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.write(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "City Selection Expert" in cleaned_data:
            # Apply different color 
            cleaned_data = cleaned_data.replace("City Selection Expert", f":{self.colors[self.color_index]}[City Selection Expert]")
        if "Local Expert at this city" in cleaned_data:
            cleaned_data = cleaned_data.replace("Local Expert at this city", f":{self.colors[self.color_index]}[Local Expert at this city]")
        if "Amazing Travel Concierge" in cleaned_data:
            cleaned_data = cleaned_data.replace("Amazing Travel Concierge", f":{self.colors[self.color_index]}[Amazing Travel Concierge]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []
    
    # The flush method is called to flush the buffer.
    def flush(self):
        pass
    
