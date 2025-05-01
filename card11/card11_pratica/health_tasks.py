from crewai import Task, Process
from textwrap import dedent

# Defines multiple tasks to be performed by a team of health-focused AI agents
class HealthTasks:

    def interpret_question(self, user_question, agent):
        return Task(
            description=dedent(f"""
                Analyze the following patient question and identify the key health topic(s), possible context,
                and any implicit concerns:

                "{user_question}"

                Structure your interpretation in a clear bullet-point format and avoid speculation beyond the given question.
            """),
            expected_output="A structured breakdown of the patient's question including topic, intent, and urgency level.",
            agent=agent,
            process=Process.sequential
        )

    def gather_medical_info(self, topic_summary, agent):
        return Task(
            description=dedent(f"""
                Using the interpreted summary of a patient's question, retrieve reliable and up-to-date information
                from trusted medical sources (e.g., WHO, Mayo Clinic, PubMed).

                Summarize findings in a concise format and clearly distinguish facts, common practices, and potential risks.
            """),
            expected_output="A fact-based medical summary relevant to the interpreted patient question.",
            agent=agent,
            process=Process.sequential
        )

    def draft_patient_friendly_response(self, agent):
        return Task(
            description=dedent("""
                Based on the interpreted question and gathered medical insights,
                generate a compassionate and clear answer for the patient.

                Ensure the response:
                - Uses simple, supportive language
                - Avoids alarming or overly technical terms
                - Recommends seeing a professional when necessary

                Include a short disclaimer that this is not a medical diagnosis.
            """),
            expected_output="A well-structured answer written in a tone suitable for general public understanding.",
            agent=agent,
            process=Process.sequential
        )
