import pandas as pd
from io import BytesIO


def dataframe_to_bytes(
    df,
    output_format,
    delimiter=None
):
    """
    Convert a pandas DataFrame into downloadable bytes
    based on the requested output format.
    """

    output_format = output_format.lower().strip()

    # -----------------------------------------
    # CSV
    # -----------------------------------------

    if output_format == "csv":

        return (
            df.to_csv(index=False)
            .encode("utf-8")
        )

    # -----------------------------------------
    # Excel
    # -----------------------------------------

    elif output_format in ["excel", "xlsx", "xls"]:

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Data"
            )

        return buffer.getvalue()

    # -----------------------------------------
    # JSON
    # -----------------------------------------

    elif output_format == "json":

        return (
            df.to_json(
                orient="records",
                indent=4
            )
            .encode("utf-8")
        )

    # -----------------------------------------
    # SQL
    # -----------------------------------------

    elif output_format == "sql":

        sql_statements = []

        table_name = "transformed_data"

        for _, row in df.iterrows():

            columns = ", ".join(
                f"`{column}`"
                for column in df.columns
            )

            values = []

            for value in row:

                if pd.isna(value):

                    values.append("NULL")

                elif isinstance(value, str):

                    escaped_value = (
                        value.replace("'", "''")
                    )

                    values.append(
                        f"'{escaped_value}'"
                    )

                else:

                    values.append(
                        str(value)
                    )

            value_string = ", ".join(values)

            sql = (
                f"INSERT INTO `{table_name}` "
                f"({columns}) "
                f"VALUES ({value_string});"
            )

            sql_statements.append(sql)

        return (
            "\n".join(sql_statements)
            .encode("utf-8")
        )

    # -----------------------------------------
    # TXT
    # -----------------------------------------

    elif output_format == "txt":

        # Default TXT delimiter is tab
        if delimiter is None or delimiter == "":
            delimiter = "\t"

        return (
            df.to_csv(
                index=False,
                sep=delimiter
            )
            .encode("utf-8")
        )

    else:

        raise ValueError(
            f"Unsupported output format: "
            f"{output_format}"
        )


def get_file_extension(output_format):
    """
    Return the appropriate file extension.
    """

    output_format = output_format.lower().strip()

    extensions = {
        "csv": ".csv",
        "excel": ".xlsx",
        "xlsx": ".xlsx",
        "xls": ".xlsx",
        "json": ".json",
        "sql": ".sql",
        "txt": ".txt"
    }

    if output_format not in extensions:

        raise ValueError(
            f"Unsupported output format: "
            f"{output_format}"
        )

    return extensions[output_format]