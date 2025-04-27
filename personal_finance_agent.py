
import os, json, openai

from pydantic import BaseModel

from personal_finance_tools import load_budget, simulate, format_plan



def read_tools():
    with open('personal_finance_tools.py', 'r') as file:
        return file.read()


SYSTEM = f"""
You are BudgetCoach, an AI agent that reallocates a household budget.
TOOLS you can call:
- load_budget
- simulate
- format_plan

TOOL Definitions:
{read_tools()}

WORKFLOW
1. Call load_budget() first.
2. From the user's request extract:
   • target surplus (₹)          • locked categories
3. Propose only unlocked cuts: {{category, new_amount}}.
4. Call simulate(); if surplus ≥ target -> format_plan() and STOP.
5. Else reflect, adjust cuts, loop back to simulate().

Always return valid JSON:
  {{ "tool": "<name>", "args": {{ ... }}, "thoughts": "<Your thoughts>", "result": "Final result" }}

"""

openai.api_key = os.getenv("OPENAI_API_KEY")

TOOLS = {
    "load_budget": load_budget,
    "simulate": simulate,
    "format_plan": format_plan,
}


def call_llm(history):
    resp = openai.chat.completions.create(
        model="gpt-4o-mini", messages=history,temperature=1,max_completion_tokens=2048,top_p=1)
    return resp.choices[0].message.content.strip()


def run_agent(user_msg):
    print(f"\nUser: {user_msg}")
    history = [{"role": "system", "content": SYSTEM},
               {"role": "user", "content": user_msg}]
    for _ in range(10):                      # hard stop after 10 tool calls
        reply = call_llm(history)
        try:
            cmd = json.loads(reply)
            tool_name = cmd.get("tool", None)
            tool = TOOLS.get(tool_name, None)
            if not tool:
                return cmd.get("result", reply)
            args = cmd.get("args", {})
            print(f"Agent: Tool call: {tool_name}({args})")
            out  = tool(**args)
            print(f"Tool result: {out}")
            history.append({"role": "assistant", "content": reply})
            history.append({"role": "user", "content": serialize_to_json(out)})
        except (json.JSONDecodeError, KeyError):
            return reply
    return "Loop limit reached."


def serialize(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    else:
        return obj  # fallback for primitives


def serialize_to_json(obj):
    return json.dumps(serialize(obj))


