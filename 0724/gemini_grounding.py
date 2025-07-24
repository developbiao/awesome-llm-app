
from agno.agent import Agent
from agno.models.google import Gemini

# Grounding build applications that can:
# 1. Increase factual accuracy: Reduce model hallucinations by basing responses on real world information.
# 2. Access real-time information: Answer questions about recent events and topics.
# 3. Provide citations: Build user truct by showing the sources for the model's claims.

agent = Agent(
    model=Gemini(id="gemini-2.5-flash", search=True),
    description="You are a helpful assistant.",
    show_tool_calls=True,
    debug_mode=True,
)

agent.print_response("What's happening in Chengdu?", stream=True)
