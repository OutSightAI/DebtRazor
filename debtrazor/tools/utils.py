def execute_tool(message, tools):
    """
    Executes a tool based on the tool calls specified in the message.

    Parameters:
    message (object): An object that contains tool calls. It is expected to have an attribute 'tool_calls' which is a list of dictionaries. Each dictionary should have keys 'name' and 'args'.
    tools (list): A list of tool objects. Each tool object is expected to have attributes 'name' and 'func'. The 'func' attribute should be a callable.

    Returns:
    Any: The result of the tool's function if a matching tool is found and executed, otherwise None.
    """
    if len(message.tool_calls) > 0:
        # Find the first tool in the tools list that matches the name in the first tool call
        selected_tool = next(
            (tool for tool in tools if tool.name in message.tool_calls[0]["name"]), None
        )
        if selected_tool is not None:
            # Execute the tool's function with the provided arguments
            return selected_tool.func(**message.tool_calls[0]["args"])
        else:
            return None
    return None
