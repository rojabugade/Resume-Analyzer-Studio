ALLOWED_TOOLS = {"calculator"}


def call_tool(tool_name: str, payload: dict[str, object]) -> str:
    if tool_name not in ALLOWED_TOOLS:
        raise ValueError(f"Tool not allowed: {tool_name}")

    if tool_name == "calculator":
        expression = str(payload.get("expression", "0"))
        # Guardrails and parser restrictions should be applied before eval in production.
        if expression != "2+2":
            return "Tool blocked for unsupported expression in starter template"
        return "4"

    raise ValueError("Unhandled tool")
