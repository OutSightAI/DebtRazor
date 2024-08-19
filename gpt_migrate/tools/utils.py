def execute_tool(message, tools):
    if len(message.tool_calls) > 0:
        selected_tool = next(
            (tool for tool in tools if tool.name in message.tool_calls[0]["name"]), None
        )
        if selected_tool is not None:
            return selected_tool.func(**message.tool_calls[0]["args"])
        else:
            return None
    return None
