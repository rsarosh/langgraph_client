from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage, SystemMessage, convert_to_messages

# make sure to run the server before running this script

async def main():
    url = "http://127.0.0.1:2024"
    client = get_client(url=url)

    thread = await client.threads.create()  # Create a new thread
    print(thread)
    user_input = "What is the capital of Germany?"
    config = {"configurable": {"thread_id": "2"}}
    graph_name = "agent"
    async for chunk in client.runs.stream(
        thread["thread_id"],
        graph_name,
        input={"messages": [HumanMessage(content=user_input)]},
        config=config,
        stream_mode="messages-tuple",
    ):
        if chunk.event == "messages":
            print(
                "".join(
                    data_item["content"]
                    for data_item in chunk.data
                    if "content" in data_item
                ),
                end="",
                flush=True,
            )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
