import pdfplumber
import pandas as pd
import re
import os
import numpy as np
from pathlib import Path

def assert_correct_table_structure(df: pd.DataFrame):
    #TODO: implement
    pass

def save_df_to_csv(df: pd.DataFrame, output_path: str):
    df.to_csv(output_path, index=False)

def clean_shf_a_protocol(df: pd.DataFrame) -> pd.DataFrame:
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

    return df

def extract_tables_from_shf_a(pdf_path: str) -> pd.DataFrame:
    """
    Alternative method to extract tables using tabula-py.
    """
    starter_df = pd.DataFrame()
    table_df = pd.DataFrame()
    exprected_line_nr=1

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            #print(text)

            # iterate over all lines in text
            for line in text.split('\n'):
                if line[0].isdigit():
                    line_nr = re.findall(r"^\d{1,3}", line)[0]
                    #print(f"line_nr: {line_nr}, exprected_line_nr: {exprected_line_nr}")
                    assert line_nr is not None
                    assert int(line_nr) == int(exprected_line_nr)
                    exprected_line_nr += 1
                    try:
                        full_pattern = r"\d{1,3} (\d{1,2}:\d{1,2}) (\d{1,2}-\d{1,2})?(.*)(Mål|Utvisning|Tilldömd|7-m miss|Direkt rött kort|Mål 7-m) (\d{1,2}) (.*)"
                        matches = re.findall(full_pattern, line)
                        if "Spelare aktiverad" in line and "0:00" in line:
                            #TODO: rewrite this
                            pattern = r"\d{1,2}\s0:00\s(.*)\sSpelare\saktiverad(\s\d{1,2})\s(.*)"
                            match = re.search(pattern, line)
                            new_row = {'Lag': match.group(1), 'Nr': match.group(2), 'Spelare': match.group(3)}
                            starter_df = pd.concat([starter_df, pd.DataFrame([new_row])], ignore_index=True)

                        if matches and len(matches)==1:
                            match = matches[0]
                            new_row = {
                                'Tid': match[0], 
                                'Mål': match[1].strip() if match[2] else "", 
                                'Lag': match[2].strip(), 
                                'Händelse': match[3].strip(), 
                                'Nr': match[4].strip(), 
                                'Spelare': match[5].strip()
                                }
                            table_df = pd.concat([table_df, pd.DataFrame([new_row])], ignore_index=True)
                    except Exception as e:
                        print(f"Error processing line in file {pdf_path}: {line}. Error: {e}")
                        continue

        clean = clean_shf_a_protocol(table_df)
        return clean, starter_df      
                    
if __name__ == "__main__":
    protocol_files = [os.path.join("./data/protocols/shf_a", f) for f in os.listdir("./data/protocols/shf_a") if f.endswith(".pdf")]
    for protocol_file in protocol_files:
        df, starter_df = extract_tables_from_shf_a(protocol_file)
        output_csv_path = Path(protocol_file.replace(".pdf", ".csv").replace("protocols", "tabular_data"))
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        save_df_to_csv(df, output_csv_path)
