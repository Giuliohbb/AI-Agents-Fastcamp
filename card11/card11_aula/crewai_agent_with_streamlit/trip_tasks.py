# Commented code from the card 11
# Import the necessary libraries
from crewai import Task
from textwrap import dedent
from datetime import date

# This class defines the tasks that the agents will perform during the trip planning process.
# Each task has a specific description, expected output, and is associated with an agent.
# The tasks are designed to be executed in a sequence to provide a comprehensive travel experience.
class TripTasks():
    # This method creates a task for identifying the best city for the trip.
    # It takes the agent, origin, cities, interests, and date range as input parameters.
    # The task description includes specific criteria for selecting the city,
    # such as weather patterns, seasonal events, and travel costs.
    # The expected output is a detailed report on the chosen city,
    # including flight costs, weather forecast, and attractions.
    # The task is associated with the agent responsible for city selection.
    # The task description is formatted using the dedent function to maintain readability.
    # The __tip_section method is called to add a motivational tip for the agent.
    # The method returns a Task object with the specified parameters.
    def identify_task(self, agent, origin, cities, interests, range):
        return Task(description=dedent(f"""
            Analyze and select the best city for the trip based
            on specific criteria such as weather patterns, seasonal
            events, and travel costs. This task involves comparing
            multiple cities, considering factors like current weather
            conditions, upcoming cultural or seasonal events, and
            overall travel expenses.

            Your final answer must be a detailed
            report on the chosen city, and everything you found out
            about it, including the actual flight costs, weather
            forecast and attractions.
            {self.__tip_section()}

            Traveling from: {origin}
            City Options: {cities}
            Trip Date: {range}
            Traveler Interests: {interests}
          """),
            expected_output="A detailed report on the chosen city with flight costs, weather forecast, and attractions.",
            agent=agent)

    def gather_task(self, agent, origin, interests, range):
        return Task(description=dedent(f"""
            As a local expert on this city you must compile an
            in-depth guide for someone traveling there and wanting
            to have THE BEST trip ever!
            Gather information about  key attractions, local customs,
            special events, and daily activity recommendations.
            Find the best spots to go to, the kind of place only a
            local would know.
            This guide should provide a thorough overview of what
            the city has to offer, including hidden gems, cultural
            hotspots, must-visit landmarks, weather forecasts, and
            high level costs.

            The final answer must be a comprehensive city guide,
            rich in cultural insights and practical tips,
            tailored to enhance the travel experience.
            {self.__tip_section()}

            Trip Date: {range}
            Traveling from: {origin}
            Traveler Interests: {interests}
          """),
            expected_output="A comprehensive city guide with cultural insights and practical tips.",
            agent=agent)

    def plan_task(self, agent, origin, interests, range):
        return Task(description=dedent(f"""
            Expand this guide into a full travel
            itinerary for this time {range} with detailed per-day plans, including
            weather forecasts, places to eat, packing suggestions,
            and a budget breakdown.

            You MUST suggest actual places to visit, actual hotels
            to stay and actual restaurants to go to.

            This itinerary should cover all aspects of the trip,
            from arrival to departure, integrating the city guide
            information with practical travel logistics.

            Your final answer MUST be a complete expanded travel plan,
            formatted as markdown, encompassing a daily schedule,
            anticipated weather conditions, recommended clothing and
            items to pack, and a detailed budget, ensuring THE BEST
            TRIP EVER, Be specific and give it a reason why you picked
            # up each place, what make them special! {self.__tip_section()}

            Trip Date: {range}
            Traveling from: {origin}
            Traveler Interests: {interests}
          """),
            expected_output="A complete 7-day travel plan, formatted as markdown, with a daily schedule and budget.",
            agent=agent)

    def __tip_section(self):
        return "If you do your BEST WORK, I'll tip you $100 and grant you any wish you want!"
