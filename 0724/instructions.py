from agno.agent import Agent
from agno.models.google import Gemini


agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    description="You are a famous short shory writer asked to write for a magazine",
    instructions=["You are a pilot on a plane flying from Hawaii to China."],
    markdown=True,
    debug_mode=True,
)

agent.print_response("Tell me a 2 sentence horror story.", stream=True)
