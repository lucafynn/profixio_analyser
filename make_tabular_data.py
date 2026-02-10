import pdfplumber
import pandas as pd
import re
import os
import numpy as np
from pathlib import Path
from rapidfuzz import fuzz

PRINTED_WARNINGS = set()


def assert_correct_table_structure(df: pd.DataFrame):
    # TODO: implement
    pass

def save_df_to_csv(df: pd.DataFrame, output_path: str):
    df.to_csv(output_path, index=False, encoding="utf-8")

def match_team(lag, home, away, threshold=50):
    if pd.isna(lag):
        return None, 0

    scores = {
        home: fuzz.token_sort_ratio(lag, home),
        away: fuzz.token_sort_ratio(lag, away),
    }

    best_team = max(scores, key=scores.get)
    best_score = scores[best_team]

    if best_score < threshold:
        msg = f"\nLoose match between {lag} and {best_team} with score {round(best_score,2)}"
        if msg not in PRINTED_WARNINGS:
            print(msg)
            PRINTED_WARNINGS.add(msg)

    return best_team


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

    return df


def extract_information(pdf_path: str) -> pd.DataFrame:
    """
    Alternative method to extract tables using tabula-py.
    """
    table_df = pd.DataFrame()
    exprected_line_nr = 1

    match_id = re.findall(r"(\d*)_shf_a", Path(pdf_path).stem)[0]

    # Get the home and away team
    shf_m_path = pdf_path.replace("shf_a", "shf_m")
    home_team = ""
    away_team = ""
    with pdfplumber.open(shf_m_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            match = re.search(r"A\s+(?P<home>.+?)\s+B\s+(?P<away>.+?)\s+resultat", text)
            if match:
                home_team = match.group("home").strip()
                away_team = match.group("away").strip()
            else:
                print(f"Could not find team names in file: {shf_m_path}")

    starters = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            # iterate over all lines in text
            for line in text.split("\n"):
                if line[0].isdigit():
                    line_nr = re.findall(r"^\d{1,3}", line)[0]
                    # print(f"line_nr: {line_nr}, exprected_line_nr: {exprected_line_nr}")
                    assert line_nr is not None
                    assert int(line_nr) == int(exprected_line_nr)
                    exprected_line_nr += 1

                    if "Spelare aktiverad" in line:
                        match = re.findall(
                            r"\d{1,3} \d{1,2}:\d{1,2} (.*) Spelare aktiverad \d{1,2} (.*)",
                            line,
                        )[0]
                        team = match_team(match[0].strip(), home_team, away_team)
                        if team not in starters.keys():
                            starters[team] = []

                        starters[team].append(match[1].strip())
                        assert len(starters.keys()) <= 2
                    else:
                        try:
                            full_pattern = r"\d{1,3} (\d{1,2}:\d{1,2}) (\d{1,2}-\d{1,2})?(.*)(Mål|Utvisning|Tilldömd|7-m miss|Direkt rött kort|Mål 7-m| ) (\d{1,2}) (.*)"
                            matches = re.findall(full_pattern, line)

                            if matches and len(matches) == 1:
                                match = matches[0]
                                new_row = {
                                    "Tid": match[0],
                                    "Mål": match[1].strip() if match[2] else "",
                                    "Lag": match[2].strip(),
                                    "Händelse": match[3].strip(),
                                    "Nr": match[4].strip(),
                                    "Spelare": match[5].strip(),
                                }
                                table_df = pd.concat(
                                    [table_df, pd.DataFrame([new_row])],
                                    ignore_index=True,
                                )
                        except Exception as e:
                            print(
                                f"Error processing line in file {pdf_path}: {line}. Error: {e}"
                            )
                            continue

        clean = clean_shf_a_protocol(table_df)

        # Match Lag (may be different in shf_a) to correct value
        clean["Lag"] = clean.apply(
            lambda row: pd.Series(match_team(row["Lag"], home_team, away_team)), axis=1
        )

        clean.insert(0, "match_id", match_id)

        meta_info = {
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "starter_home_team": str(starters[home_team]),
            "starter_away_team": str(starters[away_team]),
        }
        return clean, meta_info


if __name__ == "__main__":
    protocol_dir = Path("./data/protocols/shf_a")
    output_base_dir = Path("./data/tabular_data")
    output_base_dir.mkdir(parents=True, exist_ok=True)
 
    protocol_files = list(protocol_dir.glob("*.pdf"))
    full_meta_info = []
    for protocol_file in protocol_files:
        df, meta_info = extract_information(str(protocol_file))
        full_meta_info.append(meta_info)

        output_csv_path = output_base_dir / (protocol_file.stem + ".csv")
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        save_df_to_csv(df, output_csv_path)
    meta_info_df = pd.DataFrame(full_meta_info, columns=full_meta_info[0].keys())
    save_df_to_csv(meta_info_df, "./data/meta_info.csv")
