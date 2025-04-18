# from praisonaigents import Agent, MCP
# import gradio as gr 

# def search_maps(query):
#     search_agent = Agent(
#         instructions="You help finding information details on events, shops or institutions on Google maps",
#         llm="ollama/llama3.2",
#         tools=MCP("npx -y @modelcontextprotocol/server-google-maps", env={"GOOGLE_MAPS_API_KEY": ""})
#     )
#     result = agent.start(query)
#     return f"## Google Maps Search Results\n\n{result}"

# demo = gr.Interface(
#     fn=search_maps,
#     inputs=gr.Textbox(placeholder="I want to know about this event"),
#     outputs=gr.Markdown(),
#     title="Airbnb Booking Assistant",
#     description="Enter your event requirements below:"
# )

#search_agent.start("Search for events today around the city of Agde")


import os
import gradio as gr
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain.agents.format_scratchpad import format_log_to_str
import subprocess
import json
import tempfile

# Load environment variables from .env file
load_dotenv()

# 1. First define the tool with proper initialization
@tool
def search_maps_mcp(query: str) -> str:
    """Search for information on Google Maps using MCP."""
    try:
        # Create a temporary JSON file to store the query
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp:
            json.dump({"input": query}, temp)
            temp_path = temp.name

        # Set environment variables
        env = os.environ.copy()
        env["GOOGLE_MAPS_API_KEY"] = os.getenv("GOOGLE_MAPS_API_KEY", "")

        # Execute the MCP command
        result = subprocess.run(
            ["npx", "-y", "@modelcontextprotocol/server-google-maps"],
            input=json.dumps({"input": query}),
            text=True,
            capture_output=True,
            env=env
        )

        # Parse the output
        if result.returncode == 0 and result.stdout:
            try:
                output = json.loads(result.stdout)
                return output.get("output", result.stdout)
            except json.JSONDecodeError:
                return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error with MCP search: {str(e)}"

# 2. Then create the agent components
def create_search_agent():
    # Initialize the LLM
    llm = OllamaLLM(model="llama3.2")

    # Create tools list with the properly defined tool
    tools = [search_maps_mcp]

    # Create ReAct prompt template
    react_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Google Maps assistant. Use the tool to find location information.
Answer in this format:

Question: {input}
Thought: Consider tools and user needs
Action: {tool_names}
Action Input: Tool parameters
Observation: Tool result
Thought: Final synthesis
Final Answer: Organized response"""),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
        ("human", "{input}"),
    ])

    # Create agent with proper formatting
    agent = create_react_agent(llm, tools, react_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor

# 3. Main processing function
def search_maps(query):
    if not query.strip():
        return "Please enter a search query."

    try:
        agent = create_search_agent()
        response = agent.invoke({"input": query})
        return f"## Google Maps Search Results\n\n{response.get('output', 'No results found.')}"
    except Exception as e:
        return f"Error: {str(e)}"

# 4. Gradio interface setup
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""# 🗺️ Google Maps Search Assistant (MCP)""")

    with gr.Row():
        query_input = gr.Textbox(
            placeholder="Enter location search query...",
            label="Search Query",
            lines=2
        )

    search_button = gr.Button("🔍 Search", variant="primary")
    output = gr.Markdown()

    search_button.click(fn=search_maps, inputs=query_input, outputs=output)
    query_input.submit(fn=search_maps, inputs=query_input, outputs=output)

if __name__ == "__main__":
    demo.launch()