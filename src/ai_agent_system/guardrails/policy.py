def check_input_policy(message: str) -> None:
    blocked = ["ignore all previous instructions", "bypass policy"]
    lower = message.lower()
    if any(rule in lower for rule in blocked):
        raise ValueError("Input violates policy")


def check_output_policy(answer: str) -> None:
    if len(answer) > 5000:
        raise ValueError("Output too long")
