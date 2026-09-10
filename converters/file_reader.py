import pandas as pd
from io import BytesIO


def read_uploaded_file(uploaded_file):
    """
    Read an uploaded CSV, Excel, or TXT file
    and return a pandas DataFrame.
    """

    file_name = uploaded_file.name.lower()

    # -------------------------------------------------
    # CSV
    # -------------------------------------------------

    if file_name.endswith(".csv"):

        try:
            df = pd.read_csv(uploaded_file)

        except UnicodeDecodeError:

            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                encoding="latin1"
            )

    # -------------------------------------------------
    # Excel
    # -------------------------------------------------

    elif file_name.endswith((".xlsx", ".xls")):

        df = pd.read_excel(uploaded_file)

    # -------------------------------------------------
    # TXT
    # -------------------------------------------------

    elif file_name.endswith(".txt"):

        uploaded_file.seek(0)

        try:
            df = pd.read_csv(
                uploaded_file,
                sep=None,
                engine="python"
            )

        except Exception:

            uploaded_file.seek(0)

            content = uploaded_file.read().decode(
                "utf-8",
                errors="replace"
            )

            lines = content.splitlines()

            df = pd.DataFrame({
                "text": lines
            })

    # -------------------------------------------------
    # Unsupported file
    # -------------------------------------------------

    else:

        raise ValueError(
            "Unsupported file format. "
            "Please upload CSV, Excel, or TXT."
        )

    return df