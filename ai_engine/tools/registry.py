
"""Central registry of AI tools available to the agent."""

ALL_TOOLS = []


def register(tool):
    ALL_TOOLS.append(tool)
    return tool
