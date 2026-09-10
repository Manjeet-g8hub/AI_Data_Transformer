import streamlit as st
import pandas as pd


# =========================================================
# MIME TYPE FUNCTION
# =========================================================

def get_mime_type(output_format):

    mime_types = {

        "csv":
            "text/csv",

        "excel":
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet",

        "json":
            "application/json",

        "sql":
            "text/plain",

        "txt":
            "text/plain"
    }


    return mime_types.get(
        output_format,
        "application/octet-stream"
    )

from converters.file_reader import read_uploaded_file
from converters.file_writer import (
    dataframe_to_bytes,
    get_file_extension
)

from ai.ai_client import (
    create_transformation_plan
)

from utils.transformation_engine import (
    apply_transformation
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Data Transformer",
    page_icon="🔄",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🔄 AI Data Transformer")

st.write(
    "Upload a file, describe the transformation you want "
    "in natural language, and download the transformed data."
)


# =========================================================
# FILE UPLOAD
# =========================================================

st.subheader("1. Upload your data")

uploaded_file = st.file_uploader(
    "Choose a CSV, Excel, or TXT file",
    type=[
        "csv",
        "xlsx",
        "xls",
        "txt"
    ]
)


if uploaded_file is not None:

    # =====================================================
    # READ FILE
    # =====================================================

    try:

        df = read_uploaded_file(
            uploaded_file
        )

    except Exception as e:

        st.error(
            f"Unable to read the uploaded file: {e}"
        )

        st.stop()


    # =====================================================
    # FILE INFORMATION
    # =====================================================

    st.success(
        f"File loaded successfully: "
        f"{uploaded_file.name}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Rows",
            len(df)
        )

    with col2:

        st.metric(
            "Columns",
            len(df.columns)
        )

    with col3:

        st.metric(
            "File Size",
            f"{uploaded_file.size / 1024:.1f} KB"
        )


    # =====================================================
    # DATA PREVIEW
    # =====================================================

    st.subheader("2. Data Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


    # =====================================================
    # COLUMN INFORMATION
    # =====================================================

    with st.expander("View column information"):

        column_info = pd.DataFrame({

            "Column": df.columns,

            "Data Type": [
                str(df[column].dtype)
                for column in df.columns
            ],

            "Missing Values": [
                int(df[column].isna().sum())
                for column in df.columns
            ],

            "Unique Values": [
                int(df[column].nunique())
                for column in df.columns
            ]
        })

        st.dataframe(
            column_info,
            use_container_width=True
        )


    # =====================================================
    # USER INSTRUCTION
    # =====================================================

    st.subheader("3. Describe the transformation")

    user_instruction = st.text_area(

        "What would you like to do with this data?",

        placeholder=(
            "Example:\n"
            "Keep only customers from Delhi, "
            "remove duplicate records, "
            "and keep customer_id, name and email."
        ),

        height=130
    )


    # =====================================================
    # OUTPUT FORMAT
    # =====================================================

    output_format = st.selectbox(

        "4. Select output format",

        [
            "CSV",
            "Excel",
            "JSON",
            "SQL",
            "TXT"
        ]
    )


    # =====================================================
    # TRANSFORM BUTTON
    # =====================================================

    transform_button = st.button(
        "🚀 Transform Data",
        type="primary",
        use_container_width=True
    )


    if transform_button:

        if not user_instruction.strip():

            st.warning(
                "Please describe the transformation "
                "you want to perform."
            )

            st.stop()


        # =================================================
        # STEP 1 — ASK GEMINI FOR PLAN
        # =================================================

        with st.spinner(
            "🤖 AI is understanding your request..."
        ):

            try:

                plan = create_transformation_plan(

                    df=df,

                    user_instruction=user_instruction,

                    output_format=output_format
                )

            except Exception as e:

                st.error(
                    f"AI transformation planning failed: {e}"
                )

                st.stop()


        # =================================================
        # DISPLAY AI PLAN
        # =================================================

        st.subheader("5. AI Transformation Plan")

        if plan.get("summary"):

            st.info(
                plan["summary"]
            )


        # Show validation errors from AI

        validation_errors = plan.get(
            "validation_errors",
            []
        )


        if validation_errors:

            st.error(
                "The AI identified the following issues:"
            )

            for error in validation_errors:

                st.write(
                    f"❌ {error}"
                )

            st.stop()


        # Show operations

        operations = plan.get(
            "operations",
            []
        )


        if operations:

            st.json(
                operations
            )

        else:

            st.info(
                "No data transformation is required. "
                "The AI will only apply the requested output format."
    )


        # =================================================
        # STEP 2 — EXECUTE PLAN
        # =================================================

        with st.spinner(
            "⚙️ Applying transformation to your data..."
        ):

            try:

                transformed_df = apply_transformation(

                    df,

                    plan
                )

            except Exception as e:

                st.error(
                    f"Transformation failed: {e}"
                )

                st.stop()


        # =================================================
        # TRANSFORMATION RESULTS
        # =================================================

        st.subheader("6. Transformation Result")


        result_col1, result_col2 = st.columns(2)


        with result_col1:

            st.metric(
                "Original Rows",
                len(df)
            )


        with result_col2:

            st.metric(
                "Transformed Rows",
                len(transformed_df)
            )


        st.dataframe(
            transformed_df.head(20),
            use_container_width=True
        )


        # =================================================
        # OUTPUT FILE
        # =================================================

        st.subheader("7. Download Result")


        # Use AI-selected format

        final_output_format = plan.get(
            "output_format",
            output_format
        ).lower()


        try:

            file_bytes = dataframe_to_bytes(

            transformed_df,

            final_output_format,

    
    delimiter=plan.get(
        "delimiter",
        ""
    )
)

            extension = get_file_extension(
                final_output_format
            )

        except Exception as e:

            st.error(
                f"Could not create output file: {e}"
            )

            st.stop()


        # Create download filename

        original_name = uploaded_file.name

        original_base = (
            original_name
            .rsplit(".", 1)[0]
        )


        download_filename = (
            f"{original_base}_transformed"
            f"{extension}"
        )


        st.download_button(

            label=(
                f"⬇️ Download "
                f"{download_filename}"
            ),

            data=file_bytes,

            file_name=download_filename,

            mime=get_mime_type(
                final_output_format
            ),

            use_container_width=True
        )

