from urllib.request import urlretrieve
import os
from pathlib import Path
from get_match_ids import get_protocol_links

LEAGUE_ID = "leagueid17792"



def download_protocol(url: str, match_id) -> None:
    out_sha_a = Path(os.path.expanduser(f"./data/protocols/shf_a/{match_id}_shf_a.pdf"))
    out_sha_m = Path(os.path.expanduser(f"./data/protocols/shf_m/{match_id}_shf_m.pdf"))
    out_sha_a.parent.mkdir(parents=True, exist_ok=True)
    out_sha_m.parent.mkdir(parents=True, exist_ok=True)
    try:
        urlretrieve(url + "shf_a", str(out_sha_a))
        urlretrieve(url + "shf_m", str(out_sha_m))
        #print(f"Saved to {output_path}")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    #match_ids = open("./data/match_ids.txt").read().splitlines()
    match_ids = get_protocol_links("https://www.profixio.com/app/leagueid17792/category/1171266?segment=historikk")
    for match_id in match_ids:
        url = f"https://www.profixio.com/app/{LEAGUE_ID}/match/{match_id}/protocol/"
        download_protocol(url, match_id)