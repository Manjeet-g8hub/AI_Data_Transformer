import pandas as pd

from utils.transformation_engine import (
    apply_transformation
)


# -----------------------------------------
# Sample dataset
# -----------------------------------------

df = pd.DataFrame({

    "customer_id": [
        1001,
        1002,
        1003,
        1004,
        1005
    ],

    "name": [
        "Rahul",
        "Amit",
        "Priya",
        "Neha",
        "Rahul"
    ],

    "email": [
        "rahul@gmail.com",
        "amit@gmail.com",
        "priya@gmail.com",
        "neha@gmail.com",
        "rahul@gmail.com"
    ],

    "city": [
        "Delhi",
        "Mumbai",
        "Kolkata",
        "Delhi",
        "Delhi"
    ],

    "age": [
        32,
        41,
        28,
        35,
        32
    ]
})


# -----------------------------------------
# Transformation plan
# -----------------------------------------

plan = {

    "output_format": "json",

    "operations": [

        {
            "operation": "filter",
            "column": "city",
            "operator": "equals",
            "value": "Delhi"
        },

        {
            "operation": "remove_duplicates"
        },

        {
            "operation": "select_columns",
            "columns": [
                "customer_id",
                "name",
                "email"
            ]
        }
    ],

    "validation_errors": [],

    "summary": (
        "Filter Delhi customers, "
        "remove duplicates, "
        "and select customer information."
    )
}


# -----------------------------------------
# Apply transformation
# -----------------------------------------

result = apply_transformation(
    df,
    plan
)


# -----------------------------------------
# Display results
# -----------------------------------------

print("\nORIGINAL DATA")
print("=============")

print(df)


print("\nTRANSFORMED DATA")
print("================")

print(result)


print("\nTRANSFORMATION SUCCESSFUL")