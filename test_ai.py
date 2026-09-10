import pandas as pd

from ai.ai_client import create_transformation_plan


# ---------------------------------------------
# Sample dataset
# ---------------------------------------------

df = pd.DataFrame({

    "customer_id": [
        1001,
        1002,
        1003,
        1004
    ],

    "name": [
        "Rahul",
        "Amit",
        "Priya",
        "Neha"
    ],

    "email": [
        "rahul@gmail.com",
        "amit@gmail.com",
        "priya@gmail.com",
        "neha@gmail.com"
    ],

    "city": [
        "Delhi",
        "Mumbai",
        "Kolkata",
        "Delhi"
    ],

    "age": [
        32,
        41,
        28,
        35
    ]
})


# ---------------------------------------------
# User request
# ---------------------------------------------

instruction = """
Keep only customers from Delhi,
remove duplicate records,
and keep customer_id, name and email.

Provide the downloadable output as a
pipe-separated TXT file.
"""


output_format = "TXT"


# ---------------------------------------------
# Call AI
# ---------------------------------------------

plan = create_transformation_plan(
    df=df,
    user_instruction=instruction,
    output_format=output_format
)


# ---------------------------------------------
# Display result
# ---------------------------------------------

print("\nAI TRANSFORMATION PLAN")
print("======================")

print(plan)