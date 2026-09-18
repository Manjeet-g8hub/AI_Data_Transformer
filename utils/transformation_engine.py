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


SUPPORTED_AGGREGATIONS = {
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
}


def validate_plan(df, plan):

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
                        f"Operation {index}: Column '{column}' does not exist."
                    )

        elif operation_type == "drop_columns":

            columns = operation.get("columns", [])

            for column in columns:
                if column not in available_columns:
                    errors.append(
                        f"Operation {index}: Column '{column}' does not exist."
                    )

        elif operation_type == "rename_columns":

            rename_pairs = operation.get("rename_pairs", [])

            for pair in rename_pairs:

                old_column = pair.get("from")

                if old_column not in available_columns:
                    errors.append(
                        f"Operation {index}: Column '{old_column}' does not exist."
                    )

        elif operation_type == "filter":

            column = operation.get("column")
            operator = operation.get("operator")

            if column not in available_columns:
                errors.append(
                    f"Operation {index}: Column '{column}' does not exist."
                )

            if operator not in SUPPORTED_OPERATORS:
                errors.append(
                    f"Operation {index}: Unsupported filter operator '{operator}'."
                )

        elif operation_type == "sort":

            column = operation.get("column")

            if column not in available_columns:
                errors.append(
                    f"Operation {index}: Column '{column}' does not exist."
                )

        elif operation_type == "limit":

            count = operation.get("count")

            if not isinstance(count, int) or count < 1:
                errors.append(
                    f"Operation {index}: Limit count must be a positive integer."
                )

        elif operation_type == "aggregate":

            aggregations = operation.get("aggregations", [])

            for aggregation in aggregations:

                column = aggregation.get("column")
                function = aggregation.get("function")

                if column not in available_columns:
                    errors.append(
                        f"Operation {index}: Column '{column}' does not exist."
                    )

                if function not in SUPPORTED_AGGREGATIONS:
                    errors.append(
                        f"Operation {index}: Unsupported aggregation '{function}'."
                    )

        elif operation_type == "group_by":

            group_columns = operation.get("group_columns", [])

            for column in group_columns:

                if column not in available_columns:
                    errors.append(
                        f"Operation {index}: Column '{column}' does not exist."
                    )

            aggregations = operation.get("aggregations", [])

            for aggregation in aggregations:

                column = aggregation.get("column")
                function = aggregation.get("function")

                if column not in available_columns:
                    errors.append(
                        f"Operation {index}: Column '{column}' does not exist."
                    )

                if function not in SUPPORTED_AGGREGATIONS:
                    errors.append(
                        f"Operation {index}: Unsupported aggregation '{function}'."
                    )

        elif operation_type == "remove_duplicates":

            pass

        else:

            errors.append(
                f"Operation {index}: Unsupported operation '{operation_type}'."
            )

    return errors


def apply_filter(df, column, operator, value):

    series = df[column]

    if operator == "equals":
        return df[
            series.astype(str).str.lower() == str(value).lower()
        ]

    elif operator == "not_equals":
        return df[
            series.astype(str).str.lower() != str(value).lower()
        ]

    elif operator == "contains":
        return df[
            series.astype(str).str.contains(
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


def perform_aggregation(df, aggregation):

    column = aggregation["column"]
    function = aggregation["function"]
    alias = aggregation["alias"]

    series = df[column]

    if function in ("mean", "average"):
        value = series.mean()

    elif function == "sum":
        value = series.sum()

    elif function == "min":
        value = series.min()

    elif function == "max":
        value = series.max()

    elif function == "count":
        value = series.count()

    elif function == "count_distinct":
        value = series.nunique()

    elif function == "median":
        value = series.median()

    elif function == "std":
        value = series.std()

    elif function == "variance":
        value = series.var()

    else:
        raise ValueError(
            f"Unsupported aggregation function: {function}"
        )

    return alias, value


def apply_aggregate(df, aggregations):

    result = {}

    for aggregation in aggregations:

        alias, value = perform_aggregation(
            df,
            aggregation
        )

        result[alias] = value

    return pd.DataFrame([result])


def apply_group_by(df, group_columns, aggregations):

    aggregation_dict = {}

    rename_map = {}

    for aggregation in aggregations:

        column = aggregation["column"]
        function = aggregation["function"]
        alias = aggregation["alias"]

        if function == "average":
            function = "mean"

        if function == "count_distinct":

            aggregation_dict[column] = "nunique"

        else:

            aggregation_dict[column] = function

        rename_map[(column, function)] = alias

    result = (
        df
        .groupby(group_columns, dropna=False)
        .agg(aggregation_dict)
        .reset_index()
    )

    # Flatten MultiIndex columns if necessary
    if isinstance(result.columns, pd.MultiIndex):

        flattened_columns = []

        for column in result.columns:

            if isinstance(column, tuple):
                flattened_columns.append(
                    "_".join(
                        str(item)
                        for item in column
                        if str(item) != ""
                    )
                )
            else:
                flattened_columns.append(str(column))

        result.columns = flattened_columns

    # Rename generated aggregation columns
    generated_columns = [
        column
        for column in result.columns
        if column not in group_columns
    ]

    for aggregation, generated_column in zip(
        aggregations,
        generated_columns
    ):

        alias = aggregation["alias"]

        result = result.rename(
            columns={
                generated_column: alias
            }
        )

    return result


def apply_transformation(df, plan):

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

        if operation_type == "select_columns":

            columns = operation.get(
                "columns",
                []
            )

            result = result[columns]

        elif operation_type == "drop_columns":

            columns = operation.get(
                "columns",
                []
            )

            result = result.drop(
                columns=columns
            )

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

            if pd.api.types.is_numeric_dtype(
                result[column]
            ):

                try:
                    value = float(value)

                except (
                    ValueError,
                    TypeError
                ):
                    pass

            result = apply_filter(
                result,
                column,
                operator,
                value
            )

        elif operation_type == "remove_duplicates":

            result = result.drop_duplicates()

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

        elif operation_type == "limit":

            count = operation.get(
                "count"
            )

            result = result.head(
                count
            )

        elif operation_type == "aggregate":

            aggregations = operation.get(
                "aggregations",
                []
            )

            result = apply_aggregate(
                result,
                aggregations
            )

        elif operation_type == "group_by":

            group_columns = operation.get(
                "group_columns",
                []
            )

            aggregations = operation.get(
                "aggregations",
                []
            )

            result = apply_group_by(
                result,
                group_columns,
                aggregations
            )

    return result.reset_index(
        drop=True
    )