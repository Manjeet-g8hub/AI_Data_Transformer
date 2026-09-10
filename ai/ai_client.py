import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from ai.prompts import (
    SYSTEM_PROMPT,
    build_user_prompt
)


load_dotenv()


TRANSFORMATION_SCHEMA = {
    "type": "object",
    "properties": {

        "output_format": {
            "type": "string",
            "enum": [
                "csv",
                "excel",
                "json",
                "sql",
                "txt"
            ],
            "description": "Requested output format."
        },

        "delimiter": {
            "type": "string",
            "description": (
                "Delimiter to use for delimited text output. "
                "Examples: | for pipe, , for comma, "
                "\\t for tab, ; for semicolon. "
                "Use an empty string when no delimiter is requested."
            )
        },

        "operations": {
            "type": "array",
            "description": "Ordered list of transformations.",
            "items": {
                "type": "object",
                "properties": {

                    "operation": {
                        "type": "string",
                        "enum": [
                            "select_columns",
                            "rename_columns",
                            "filter",
                            "remove_duplicates",
                            "sort"
                        ]
                    },

                    "columns": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

"rename_pairs": {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "from": {
                "type": "string"
            },
            "to": {
                "type": "string"
            }
        },
        "required": [
            "from",
            "to"
        ]
    }
},

                    "column": {
                        "type": "string"
                    },

                    "operator": {
                        "type": "string",
                        "enum": [
                            "equals",
                            "not_equals",
                            "greater_than",
                            "greater_than_or_equal",
                            "less_than",
                            "less_than_or_equal",
                            "contains"
                        ]
                    },

                    "value": {
                        "type": "string"
                    },

                    "ascending": {
                        "type": "boolean"
                    }
                },

                "required": [
                    "operation"
                ]
            }
        },

        "validation_errors": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "summary": {
            "type": "string"
        }
    },

    "required": [
        "output_format",
        "operations",
        "validation_errors",
        "summary"
    ]
}


def get_gemini_client():
    """
    Create and return the Gemini client.
    """

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:

        raise ValueError(
            "GOOGLE_API_KEY was not found. "
            "Please check your .env file."
        )

    return genai.Client(
        api_key=api_key
    )


def create_transformation_plan(
    df,
    user_instruction,
    output_format
):
    """
    Ask Gemini to convert the user's natural language
    request into a structured transformation plan.
    """

    client = get_gemini_client()

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.7-flash"
    )

    columns = list(df.columns)

    data_types = {
        column: str(df[column].dtype)
        for column in df.columns
    }

    sample_df = df.head(10)

    sample_data = sample_df.to_dict(
        orient="records"
    )

    user_prompt = build_user_prompt(
        columns=columns,
        data_types=data_types,
        sample_data=sample_data,
        user_instruction=user_instruction,
        output_format=output_format
    )

    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(

            system_instruction=SYSTEM_PROMPT,

            temperature=0,

            response_mime_type="application/json",

            response_schema=TRANSFORMATION_SCHEMA
        )
    )

    try:

        plan = json.loads(response.text)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Gemini returned invalid JSON: {e}"
        )

    return plan