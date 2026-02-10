import pandas as pd
from pathlib import Path
from tqdm import tqdm
import os

from fetch_protocols import download_protocol, get_protocol_links, LEAGUE_ID
from make_tabular_data import extract_information, save_df_to_csv

if __name__ == "__main__":
    match_ids = get_protocol_links("https://www.profixio.com/app/leagueid17792/category/1171266?segment=historikk")
    for match_id in tqdm(match_ids, desc="Downloading match protocols"):
        url = f"https://www.profixio.com/app/{LEAGUE_ID}/match/{match_id}/protocol/"
        download_protocol(url, match_id)
    
    assert len(match_ids) == sum(1 for f in os.listdir("./data/protocols/shf_a") if f.lower().endswith(".pdf") and os.path.isfile(os.path.join("./data/protocols/shf_a", f)))
    
    protocol_dir = Path("./data/protocols/shf_a")
    output_base_dir = Path("./data/tabular_data")
    output_base_dir.mkdir(parents=True, exist_ok=True)
 
    protocol_files = list(protocol_dir.glob("*.pdf"))
    full_meta_info = []
    for protocol_file in tqdm(protocol_files, desc="Processing protocols into tabular data"):
        df, meta_info = extract_information(str(protocol_file))
        full_meta_info.append(meta_info)

        output_csv_path = output_base_dir / (protocol_file.stem + ".csv")
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        save_df_to_csv(df, output_csv_path)
    meta_info_df = pd.DataFrame(full_meta_info, columns=full_meta_info[0].keys())
    save_df_to_csv(meta_info_df, "./data/meta_info.csv")

    