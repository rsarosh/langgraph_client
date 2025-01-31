# https://langchain-ai.github.io/langgraph/cloud/how-tos/human_in_the_loop_user_input/

from langgraph_sdk import get_client
from langchain_core.messages import HumanMessage, SystemMessage, convert_to_messages


async def main():
    url = "http://127.0.0.1:2024"
    client = get_client(url=url)

    thread = await client.threads.create()  # Create a new thread
 
    # Human intervention needed
    user_input = "Ask the user where they are? and then using the search tool check the weather in that location"
    #user_input = "Ask human to help me query: Tell me about langgraph human in loop feature" 
    user_input_data = {
    "messages": [
        {
            "role": "user",
            "content": user_input,
        }
    ]
    }
    config = {"configurable": {"thread_id": "2"}}
    assistant_id = "agent"

    # Now, let's invoke our graph by interrupting before ask_human node:
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id,  
        input=user_input_data,
        stream_mode="updates",
        # interrupt_before=["ask_human"], #No intrupt go directly to the human in loop

    ):
        if chunk.data and chunk.event != "metadata": 
            if "agent" in chunk.data:
                print(chunk.data["agent"]["messages"][0]["content"])
                print (chunk.data["agent"]["messages"][0]["tool_calls"][0]["args"]["question"])
            else:
                if "__interrupt__" in chunk.data:
                    print("\033[92m" + chunk.data["__interrupt__"][0]["value"] + "\033[0m") # Question coming from the graph interrupt

    # Adding user input to state¶
    # We now want to update this thread with a response from the user. We then can kick off another run.
    # Because we are treating this as a tool call, we will need to update the state as if it is a response 
    # from a tool call. 
    # In order to do this, we will need to check the state to get the ID of the tool call.

    state = await client.threads.get_state(thread['thread_id'])
   
    tool_call_id = state['values']['messages'][-1]['tool_calls'][0]['id']
    # We now create the tool call with the id and the response we want
    print("Enter the city name: ")
    city_name = input()
    human_response =  {"data": city_name}
   
    tool_message = [{"tool_call_id": tool_call_id, "type": "tool", "content": human_response}]
    response = await client.threads.update_state(thread['thread_id'], {"messages": tool_message}, as_node="ask_human")
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id, #assistant_id,
        input=None,
        stream_mode="updates",
        ):
        if chunk.data and chunk.event != "metadata": 
            if "agent" in chunk.data:
                print(chunk.data["agent"]["messages"][0]["content"])

    # Invoking after receiving human input¶
    # We can now tell the agent to continue. We can just pass in None as the input to the graph, since no additional input is needed:
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id,
        input=None,
        stream_mode="updates",
    ):
        if chunk.data and chunk.event != "metadata": 
            print("\033[92m" + str(chunk.data) + "\033[0m")

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
