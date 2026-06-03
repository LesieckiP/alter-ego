record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record details of a user interacting with the AI alter-ego.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The user's email address."},
            "name": {"type": "string", "description": "The user's name."},
            "notes": {"type": "string", "description": "Any additional notes about the user."}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Use this tool to record a question that the AI alter-ego was not able to understand.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that was not understood."}
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]