import pandas as pd
from converters.file_writer import dataframe_to_bytes, get_file_extension


# Sample transformed data
df = pd.DataFrame({
    "customer_id": [1001, 1004, 1005],
    "name": ["Rahul", "Neha", "Rahul"],
    "email": [
        "rahul@gmail.com",
        "neha@gmail.com",
        "rahul2@gmail.com"
    ]
})


# Test pipe-separated TXT
file_bytes = dataframe_to_bytes(
    df,
    "txt",
    delimiter="|"
)


# Save temporary output
with open("test_output.txt", "wb") as f:
    f.write(file_bytes)


print("FILE WRITER SUCCESSFUL")
print("Output file: test_output.txt")
print("Extension:", get_file_extension("txt"))


# Display generated content
print("\nGenerated TXT content:")
print(file_bytes.decode("utf-8"))