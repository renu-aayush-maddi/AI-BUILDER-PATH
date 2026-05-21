
# TOOL CALLING WITH LANGCHAIN AGENT
# import os
# from dotenv import load_dotenv

# load_dotenv()

# from langchain_openai import ChatOpenAI
# from langchain.agents import initialize_agent, AgentType
# from langchain.memory import ConversationBufferMemory

# from tools.mcp_tool import get_mcp_tool
# from rag.rag_tool import get_rag_tool
# from tools.web_search_tool import get_web_search_tool


# def build_agent():

#     llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)

#     tools = [
#         get_mcp_tool(),
#         get_rag_tool(),
#         get_web_search_tool(),
#     ]

#     memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True)

#     agent = initialize_agent(
#         tools=tools,
#         llm=llm,
#         agent=AgentType.OPENAI_FUNCTIONS,
#         # agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
#         memory=memory,
#         verbose=True,
#     )

#     return agent


# def main():

#     if not os.getenv("OPENAI_API_KEY"):
#         print("OPENAI_API_KEY missing in .env")
#         return

#     print("\nPresidio Internal Research Agent")
#     print("Type 'exit' to quit.\n")

#     agent = build_agent()

#     while True:

#         query = input(" Ask: ")

#         if query.lower() == "exit":
#             break

#         try:

#             response = agent.invoke({"input": query})

#             print("\nRESPONSE:\n")
#             print(response["output"])
#             print()

#         except Exception as e:

#             print(f"\nERROR:\n{e}\n")


# if __name__ == "__main__":
#     main()


# SEPERATE MCP SERVERS FOR EACH TOOL


import asyncio

from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI

from langchain.agents import create_agent

from langchain_mcp_adapters.client import MultiServerMCPClient


async def build_agent():

    client = MultiServerMCPClient(
        {
            "google_docs": {
                "command": "python",
                "args": ["mcp_servers/google_docs_server.py"],
                "transport": "stdio",
            },

            "rag": {
                "command": "python",
                "args": ["mcp_servers/rag_server.py"],
                "transport": "stdio",
            },

            "web": {
                "command": "python",
                "args": ["mcp_servers/web_search_server.py"],
                "transport": "stdio",
            },
        }
    )

    tools = await client.get_tools()

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=(
            "You are Presidio's Internal Research Agent. "
            "Use the available MCP tools to answer employee questions, "
            "search HR policies, retrieve Google Docs information, "
            "and search the web for benchmarks and compliance updates."
        )
    )

    return agent


async def main():

    agent = await build_agent()

    print("\nPresidio Internal Research Agent")
    print("Type 'exit' to quit.\n")

    while True:

        query = input("Ask: ")

        if query.lower() == "exit":
            break

        try:

            response = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                }
            )

            print("\nRESPONSE:\n")

            print(
                response["messages"][-1].content
            )

            print()

        except Exception as e:

            print(f"\nERROR:\n{e}\n")


if __name__ == "__main__":

    asyncio.run(main())