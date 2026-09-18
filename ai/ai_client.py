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

        # =====================================================
        # TRANSFORMATION OPERATIONS
        # =====================================================

        "operations": {

            "type": "array",

            "description": (
                "Ordered list of data transformation operations. "
                "Operations must be applied in the order provided."
            ),

            "items": {

                "type": "object",

                "properties": {

                    # -----------------------------------------
                    # Operation type
                    # -----------------------------------------

                    "operation": {

                        "type": "string",

                        "enum": [
                            "select_columns",
                            "drop_columns",
                            "rename_columns",
                            "filter",
                            "remove_duplicates",
                            "sort",
                            "limit",
                            "aggregate",
                            "group_by"
                        ]
                    },


                    # -----------------------------------------
                    # Column list
                    # -----------------------------------------

                    "columns": {

                        "type": "array",

                        "items": {
                            "type": "string"
                        }
                    },


                    # -----------------------------------------
                    # Rename columns
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # Filter
                    # -----------------------------------------

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


                    # -----------------------------------------
                    # Sort
                    # -----------------------------------------

                    "ascending": {

                        "type": "boolean"
                    },


                    # -----------------------------------------
                    # Limit
                    # -----------------------------------------

                    "count": {

                        "type": "integer",

                        "description": (
                            "Number of rows to keep. "
                            "Must be a positive integer."
                        )
                    },


                    # -----------------------------------------
                    # Group By
                    # -----------------------------------------

                    "group_columns": {

                        "type": "array",

                        "items": {
                            "type": "string"
                        }
                    },


                    # -----------------------------------------
                    # Aggregations
                    # -----------------------------------------

                    "aggregations": {

                        "type": "array",

                        "items": {

                            "type": "object",

                            "properties": {

                                "column": {
                                    "type": "string"
                                },

                                "function": {

                                    "type": "string",

                                    "enum": [

                                        "sum",
                                        "mean",
                                        "average",
                                        "min",
                                        "max",
                                        "count",
                                        "count_distinct",
                                        "median",
                                        "std",
                                        "variance"
                                    ]
                                },

                                "alias": {
                                    "type": "string"
                                }
                            },

                            "required": [
                                "column",
                                "function",
                                "alias"
                            ]
                        }
                    }
                },

                "required": [
                    "operation"
                ]
            }
        },


        # =====================================================
        # OUTPUT FORMAT
        # =====================================================

        "output_format": {

            "type": "string",

            "enum": [
                "csv",
                "excel",
                "json",
                "sql",
                "txt"
            ]
        },


        # =====================================================
        # DELIMITER
        # =====================================================

        "delimiter": {

            "type": "string",

            "description": (
                "Delimiter for TXT output. "
                "Examples: | , ; or tab. "
                "Use empty string when no delimiter is requested."
            )
        },


        # =====================================================
        # VALIDATION
        # =====================================================

        "validation_errors": {

            "type": "array",

            "items": {
                "type": "string"
            }
        },


        # =====================================================
        # SUMMARY
        # =====================================================

        "summary": {

            "type": "string"
        }
    },


    # =========================================================
    # REQUIRED TOP-LEVEL FIELDS
    # =========================================================

    "required": [

        "operations",
        "output_format",
        "delimiter",
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
    df=df,
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
    response_schema=TRANSFORMATION_SCHEMA,
    automatic_function_calling=types.AutomaticFunctionCallingConfig(
        disable=True
    )
            
        )
    )

    try:

        plan = json.loads(response.text)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Gemini returned invalid JSON: {e}"
        )

    return plan