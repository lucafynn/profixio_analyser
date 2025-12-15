import pdfplumber
import pandas as pd
import re
import os
import camelot
import numpy as np

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes the extracted DataFrame from the PDF.
    """
    # drop first row
    df = df.iloc[1:].reset_index(drop=True)
    # Drop Spelare aktiverad
    df = df[df["Händelse"] != "Spelare aktiverad"]
    # Replace all cells with empty strings with NaN
    df.replace("", np.nan, inplace=True)
    # Drop Start and slut messages i.e. whenever the team is empty
    df = df[df["Lag"].notna()]

    print(df.head())
    return df

def merge_pdf_tables_to_df(pdf_path: str) -> pd.DataFrame:
    """
    Extracts match event data from a handball match PDF and returns a pandas DataFrame.
    """


    # Read the PDF
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')

    dfs = []
    for i, table in enumerate(tables):
        df = table.df.copy()

        # Drop completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Remove first row/column for first table
        df = df.iloc[1:, 1:]
        df.reset_index(drop=True, inplace=True)

        if df.columns.size == 5:
            df.insert(
                loc=1,
                column="score",
                value=df.iloc[:, 1].str.extract(r"(\d{1,2}-\d{1,2})")[0]
            )
            df.iloc[:, 2] = df.iloc[:, 2].str.replace(r"\d{1,2}-\d{1,2}", "", regex=True).str.strip()
        df.columns = ["Tid", "Mål", "Lag", "Händelse", "Nr", "Spelare"]
        dfs.append(df)
    # Combine all tables
    df_combined = pd.concat(dfs, ignore_index=True)

    starters = df_combined.query('Händelse == "Spelare aktiverad" and Tid == "0:00"')
    print(clean_df(df_combined))

if __name__ == "__main__":
    protocol_files = [os.path.join("./data/protocols/shf_a", f) for f in os.listdir("./data/protocols/shf_a") if f.endswith(".pdf")]
    df_shf_a = merge_pdf_tables_to_df(protocol_files[0])  # Assuming we're processing the first file
