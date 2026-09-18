import pandas as pd
from io import BytesIO


# =========================================================
# DATAFRAME TO BYTES
# =========================================================

def dataframe_to_bytes(
    df,
    output_format,
    delimiter=None
):

    output_format = output_format.lower().strip()


    # =====================================================
    # CSV
    # =====================================================

    if output_format == "csv":

        return df.to_csv(
            index=False
        ).encode("utf-8")


    # =====================================================
    # EXCEL
    # =====================================================

    elif output_format in [
        "excel",
        "xlsx",
        "xls"
    ]:

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ):

            df.to_excel(
                buffer,
                index=False,
                sheet_name="Data"
            )

        return buffer.getvalue()


    # =====================================================
    # JSON
    # =====================================================

    elif output_format == "json":

        return df.to_json(
            orient="records",
            indent=4,
            date_format="iso"
        ).encode("utf-8")


    # =====================================================
    # SQL — SELECT ONLY
    # =====================================================

    elif output_format == "sql":

        table_name = "transformed_data"


        # -------------------------------------------------
        # Create SELECT column list
        # -------------------------------------------------

        columns = ",\n    ".join(
            f"`{column}`"
            for column in df.columns
        )


        sql_query = (
            f"SELECT\n"
            f"    {columns}\n"
            f"FROM `{table_name}`;"
        )


        return sql_query.encode("utf-8")


    # =====================================================
    # TXT
    # =====================================================

    elif output_format == "txt":

        if delimiter is None or delimiter == "":

            delimiter = "\t"


        return df.to_csv(
            index=False,
            sep=delimiter
        ).encode("utf-8")


    # =====================================================
    # UNSUPPORTED FORMAT
    # =====================================================

    else:

        raise ValueError(
            f"Unsupported output format: {output_format}"
        )


# =========================================================
# FILE EXTENSION
# =========================================================

def get_file_extension(output_format):

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
            f"Unsupported output format: {output_format}"
        )


    return extensions[output_format]