import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

from tools.mcp_tool import get_mcp_tool
from rag.rag_tool import get_rag_tool
from tools.web_search_tool import get_web_search_tool


def build_agent():

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    tools = [
        get_mcp_tool(),
        get_rag_tool(),
        get_web_search_tool(),
    ]

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        verbose=True,
    )

    return agent


def main():

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY missing in .env")
        return

    print("\nPresidio Internal Research Agent")
    print("Type 'exit' to quit.\n")

    agent = build_agent()

    while True:

        query = input(" Ask: ")

        if query.lower() == "exit":
            break

        try:

            response = agent.invoke({
                "input": query
            })

            print("\nRESPONSE:\n")
            print(response["output"])
            print()

        except Exception as e:

            print(f"\nERROR:\n{e}\n")


if __name__ == "__main__":
    main()