import json

from notifier import Notifier


class ToolExecutor:
    def __init__(self, notifier: Notifier | None = None):
        self.notifier = notifier or Notifier()
        self.handlers = {
            "record_user_details": self.notifier.record_user_details,
            "record_unknown_question": self.notifier.record_unknown_question,
        }

    def execute(self, tool_calls):
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            params = json.loads(tool_call.function.arguments or "{}")
            print(f"Tool called: {tool_name}", flush=True)
            tool = self.handlers.get(tool_name)
            try:
                result = tool(**params) if tool else {"error": f"Unknown tool: {tool_name}"}
            except Exception as exc:
                print(f"Tool execution failed for {tool_name}: {exc}", flush=True)
                result = {"error": str(exc), "tool": tool_name}
            results.append(
                {
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                }
            )

        return results
