from urllib.request import urlretrieve
import os
from pathlib import Path
from get_match_ids import get_protocol_links
from urllib.request import Request, urlopen

LEAGUE_ID = "leagueid17792"



def download_protocol(url: str, match_id) -> None:
    headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    }

    # --- shf_a ---
    out_sha_a = Path(os.path.expanduser(f"./data/protocols/shf_a/{match_id}_shf_a.pdf"))
    out_sha_a.parent.mkdir(parents=True, exist_ok=True)

    if not out_sha_a.exists():
        req = Request(url + "shf_a", headers=headers)
        with urlopen(req) as r, open(out_sha_a, "w") as f:
            f.write(r.read())

    # --- shf_m ---
    out_sha_m = Path(os.path.expanduser(f"./data/protocols/shf_m/{match_id}_shf_m.pdf"))
    out_sha_m.parent.mkdir(parents=True, exist_ok=True)

    if not out_sha_m.exists():
        req = Request(url + "shf_m", headers=headers)
        with urlopen(req) as r, open(out_sha_m, "w") as f:
            f.write(r.read())
    

if __name__ == "__main__":
    match_ids = open("./data/protocols/match_ids.txt").read().splitlines()
    #match_ids = get_protocol_links("https://www.profixio.com/app/leagueid17792/category/1171266?segment=historikk")
    for match_id in match_ids:
        url = f"https://www.profixio.com/app/{LEAGUE_ID}/match/{match_id}/protocol/"
        download_protocol(url, match_id)
    