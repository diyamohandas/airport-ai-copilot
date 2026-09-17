import json
from typing import Any, Dict

from groq import Groq

from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override,
)


MODEL_NAME = "openai/gpt-oss-120b"


# -------------------------------------------------------------------
# Tool definitions
# These definitions tell the LLM what tools are available.
# -------------------------------------------------------------------

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_airport_metrics",
            "description": (
                "Get the latest operational metrics for an airport. "
                "Use this when the user asks about airport performance, "
                "completion rate, ETA, active drivers, cancellations, "
                "queue size, surge multiplier, or request volume."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": (
                            "Airport code. Must be one of SFO, LAX, or JFK."
                        ),
                    }
                },
                "required": ["airport_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_driver_incentive",
            "description": (
                "Calculate the recommended driver incentive based on "
                "driver count and operational severity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "driver_count": {
                        "type": "integer",
                        "description": "Number of active drivers.",
                    },
                    "severity_level": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high",
                            "critical",
                        ],
                        "description": "Operational severity level.",
                    },
                },
                "required": [
                    "driver_count",
                    "severity_level",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_surge_override",
            "description": (
                "Request a surge multiplier override for an airport. "
                "Use this when the user explicitly asks to change "
                "the surge multiplier."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": (
                            "Airport code. Must be SFO, LAX, or JFK."
                        ),
                    },
                    "new_multiplier": {
                        "type": "number",
                        "description": (
                            "Requested new surge multiplier."
                        ),
                    },
                    "reason": {
                        "type": "string",
                        "description": (
                            "Business or operational reason for "
                            "the requested surge change."
                        ),
                    },
                },
                "required": [
                    "airport_code",
                    "new_multiplier",
                    "reason",
                ],
            },
        },
    },
]


# -------------------------------------------------------------------
# Tool executor
# -------------------------------------------------------------------

def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a tool selected by the LLM.

    Returns a structured dictionary so that the LLM can
    reason over the tool result.
    """

    try:
        if tool_name == "get_airport_metrics":
            return get_airport_metrics(
                arguments["airport_code"]
            )

        if tool_name == "calculate_driver_incentive":
            return calculate_driver_incentive(
                driver_count=arguments["driver_count"],
                severity_level=arguments["severity_level"],
            )

        if tool_name == "trigger_surge_override":
            return trigger_surge_override(
                airport_code=arguments["airport_code"],
                new_multiplier=arguments["new_multiplier"],
                reason=arguments["reason"],
            )

        return {
            "status": "error",
            "error": f"Unknown tool: {tool_name}",
        }

    except KeyError as exc:
        return {
            "status": "error",
            "error": f"Missing required argument: {exc}",
        }

    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }


# -------------------------------------------------------------------
# LLM tool-calling workflow
# -------------------------------------------------------------------

def run_tool_calling(
    user_query: str,
    client: Groq
) -> Dict[str, Any]:
    """
    Send a user query to the LLM, allow it to select a tool,
    execute the selected tool, and then generate a final response.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are an Airport Operations AI Copilot. "
                "Use the available tools when operational data "
                "or calculations are required. "
                "Do not invent operational metrics. "
                "If a tool returns an error, explain the error clearly. "
                "For surge overrides, clearly state whether human "
                "approval is required."
            ),
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]

    # ---------------------------------------------------------------
    # First LLM call: decide whether a tool is required
    # ---------------------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0,
    )

    assistant_message = response.choices[0].message

    # ---------------------------------------------------------------
    # No tool required
    # ---------------------------------------------------------------

    if not assistant_message.tool_calls:

        return {
            "query": user_query,
            "tool_called": False,
            "tool_results": [],
            "response": assistant_message.content.strip(),
        }

    # ---------------------------------------------------------------
    # Tool call detected
    # ---------------------------------------------------------------

    messages.append(
        {
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in assistant_message.tool_calls
            ],
        }
    )

    tool_results = []

    for tool_call in assistant_message.tool_calls:

        tool_name = tool_call.function.name

        try:
            arguments = json.loads(
                tool_call.function.arguments
            )
        except json.JSONDecodeError:
            tool_result = {
                "status": "error",
                "error": "Invalid JSON arguments generated by the LLM.",
            }

            arguments = {}

        else:
            tool_result = execute_tool(
                tool_name=tool_name,
                arguments=arguments,
            )

        tool_results.append(
            {
                "tool": tool_name,
                "arguments": arguments,
                "result": tool_result,
            }
        )

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            }
        )

    # ---------------------------------------------------------------
    # Second LLM call: interpret the tool result
    # ---------------------------------------------------------------

    final_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0,
    )

    answer = final_response.choices[0].message.content

    return {
        "query": user_query,
        "tool_called": True,
        "tool_results": tool_results,
        "response": answer.strip(),
    }


# -------------------------------------------------------------------
# Manual tests
# -------------------------------------------------------------------

if __name__ == "__main__":

    from src.llm import load_groq_client

    print("\n" + "=" * 70)
    print("AIRPORT OPERATIONS AI COPILOT - TOOL CALLING TEST")
    print("=" * 70)

    client = load_groq_client()

    test_queries = [
        "What are the latest operational metrics for SFO?",
        "Calculate the driver incentive for 250 drivers at high severity.",
        "Request a surge multiplier of 1.4x at SFO because the airport queue is increasing.",
    ]

    for query in test_queries:

        print("\n" + "-" * 70)
        print("USER QUERY:")
        print(query)

        result = run_tool_calling(
            user_query=query,
            client=client,
        )

        print("\nTOOL CALLED:")
        print(result["tool_called"])

        print("\nTOOL RESULTS:")

        for tool_result in result["tool_results"]:
            print(
                json.dumps(
                    tool_result,
                    indent=2
                )
            )

        print("\nFINAL RESPONSE:")
        print(result["response"])

    print("\n" + "=" * 70)
    print("TOOL CALLING TEST COMPLETED")
    print("=" * 70)
