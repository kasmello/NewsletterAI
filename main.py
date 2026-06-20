import os
import subprocess
import tempfile

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM, Process
from crewai_tools import SerperDevTool

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise EnvironmentError(
        "Missing ANTHROPIC_API_KEY in .env. Create a .env file with ANTHROPIC_API_KEY=."
    )

llm = LLM(model="anthropic/claude-sonnet-4-6", max_tokens=4096)


search = SerperDevTool()

researcher = Agent(
    role="Research Analyst",
    goal="Find the 5 most interesting recent developments on the topic",
    backstory="Expert at finding relevant news and summarising key points",
    tools=[search],
    llm=llm
)

writer = Agent(
    role="Newsletter Writer",
    goal="Write an engaging newsletter from the research",
    backstory="Experienced writer who makes technical content accessible",
    llm=llm
)

editor = Agent(
    role="Editor",
    goal="Critique drafts and decide if they are ready to publish",
    backstory="Senior editor with high standards for quality",
    llm=llm
)

# --- Step 1: Research (runs once) ---
research_task = Task(
    description="Research the 5 most interesting recent developments in: {topic}",
    agent=researcher,
    expected_output="5 summarised news items with key insights"
)

research_crew = Crew(agents=[researcher], tasks=[research_task], verbose=True)
research_result = research_crew.kickoff(inputs={"topic": "Corruption in Indonesia"})

# --- Step 2: Write → Editor critique loop ---
MAX_ROUNDS = 3
draft = None
feedback = None

for round_num in range(1, MAX_ROUNDS + 1):
    print(f"\n=== Round {round_num} ===")

    if feedback:
        write_description = (
            f"Revise the newsletter based on this editor feedback:\n{feedback}\n\n"
            f"Previous draft:\n{draft}\n\n"
            f"Research to draw from:\n{research_result}"
        )
    else:
        write_description = (
            f"Write a 500 word newsletter from this research:\n{research_result}"
        )

    write_task = Task(
        description=write_description,
        agent=writer,
        expected_output="Engaging newsletter with intro, 5 sections, conclusion"
    )

    critique_task = Task(
        description=(
            "Review the newsletter draft produced by the writer.\n\n"
            "Evaluate against these criteria:\n"
            "- Is it engaging?\n"
            "- Is it under 500 words?\n"
            "- Are all facts grounded in the research?\n\n"
            "If it passes all criteria, start your response with APPROVED.\n"
            "If it needs changes, start your response with REVISE: and explain what to fix."
        ),
        agent=editor,
        context=[write_task],
        expected_output="APPROVED or REVISE: <feedback>"
    )

    draft_crew = Crew(agents=[writer, editor], tasks=[write_task, critique_task], verbose=True)
    critique = str(draft_crew.kickoff())
    draft = write_task.output.raw

    if critique.strip().startswith("APPROVED"):
        print("\nEditor approved the draft!")
        break

    feedback = critique.replace("REVISE:", "").strip()
    print(f"\nEditor requested revisions: {feedback}")

    if round_num == MAX_ROUNDS:
        print("\nMax rounds reached, using last draft.")

print("\n=== FINAL NEWSLETTER ===")
print(draft)
with open("output.md", "w") as file:
    file.write(draft)
