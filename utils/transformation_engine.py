import pandas as pd


SUPPORTED_OPERATORS = {
    "equals",
    "not_equals",
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
    "contains"
}


def validate_plan(df, plan):
    """
    Validate the AI transformation plan against
    the actual DataFrame columns.
    """

    errors = []

    if not isinstance(plan, dict):
        return ["Transformation plan must be a dictionary."]

    operations = plan.get("operations", [])

    if not isinstance(operations, list):
        return ["Operations must be provided as a list."]

    available_columns = set(df.columns)

    for index, operation in enumerate(operations, start=1):

        operation_type = operation.get("operation")

        if operation_type == "select_columns":

            columns = operation.get("columns", [])

            for column in columns:

                if column not in available_columns:

                    errors.append(
                        f"Operation {index}: "
                        f"Column '{column}' does not exist."
                    )

        elif operation_type == "rename_columns":

            rename_pairs = operation.get(
                "rename_pairs",
                []
            )

            for pair in rename_pairs:

                old_column = pair.get("from")

                if old_column not in available_columns:

                    errors.append(
                        f"Operation {index}: "
                        f"Column '{old_column}' does not exist."
                    )

        elif operation_type == "filter":

            column = operation.get("column")

            operator = operation.get("operator")

            if column not in available_columns:

                errors.append(
                    f"Operation {index}: "
                    f"Column '{column}' does not exist."
                )

            if operator not in SUPPORTED_OPERATORS:

                errors.append(
                    f"Operation {index}: "
                    f"Unsupported filter operator "
                    f"'{operator}'."
                )

        elif operation_type == "sort":

            column = operation.get("column")

            if column not in available_columns:

                errors.append(
                    f"Operation {index}: "
                    f"Column '{column}' does not exist."
                )

        elif operation_type == "remove_duplicates":

            pass

        else:

            errors.append(
                f"Operation {index}: "
                f"Unsupported operation '{operation_type}'."
            )

    return errors


def apply_filter(df, column, operator, value):
    """
    Apply a filter operation to the DataFrame.
    """

    series = df[column]

    if operator == "equals":

        return df[
            series.astype(str).str.lower()
            == str(value).lower()
        ]

    elif operator == "not_equals":

        return df[
            series.astype(str).str.lower()
            != str(value).lower()
        ]

    elif operator == "contains":

        return df[
            series.astype(str)
            .str.contains(
                str(value),
                case=False,
                na=False
            )
        ]

    elif operator == "greater_than":

        return df[series > value]

    elif operator == "greater_than_or_equal":

        return df[series >= value]

    elif operator == "less_than":

        return df[series < value]

    elif operator == "less_than_or_equal":

        return df[series <= value]

    else:

        raise ValueError(
            f"Unsupported filter operator: {operator}"
        )


def apply_transformation(df, plan):
    """
    Execute the AI-generated transformation plan
    against the complete DataFrame.
    """

    validation_errors = validate_plan(
        df,
        plan
    )

    if validation_errors:

        raise ValueError(
            "\n".join(validation_errors)
        )

    result = df.copy()

    operations = plan.get(
        "operations",
        []
    )

    for operation in operations:

        operation_type = operation.get(
            "operation"
        )

        # -----------------------------------------
        # SELECT COLUMNS
        # -----------------------------------------

        if operation_type == "select_columns":

            columns = operation.get(
                "columns",
                []
            )

            result = result[
                columns
            ]

        # -----------------------------------------
        # RENAME COLUMNS
        # -----------------------------------------

        elif operation_type == "rename_columns":

            rename_pairs = operation.get(
                "rename_pairs",
                []
            )

            rename_map = {}

            for pair in rename_pairs:

                rename_map[
                    pair["from"]
                ] = pair["to"]

            result = result.rename(
                columns=rename_map
            )

        # -----------------------------------------
        # FILTER
        # -----------------------------------------

        elif operation_type == "filter":

            column = operation.get(
                "column"
            )

            operator = operation.get(
                "operator"
            )

            value = operation.get(
                "value"
            )

            # Try numeric conversion when possible
            if pd.api.types.is_numeric_dtype(
                result[column]
            ):

                try:

                    value = float(value)

                except (ValueError, TypeError):

                    pass

            result = apply_filter(
                result,
                column,
                operator,
                value
            )

        # -----------------------------------------
        # REMOVE DUPLICATES
        # -----------------------------------------

        elif operation_type == "remove_duplicates":

            result = result.drop_duplicates()

        # -----------------------------------------
        # SORT
        # -----------------------------------------

        elif operation_type == "sort":

            column = operation.get(
                "column"
            )

            ascending = operation.get(
                "ascending",
                True
            )

            result = result.sort_values(
                by=column,
                ascending=ascending
            )

    return result.reset_index(
        drop=True
    )