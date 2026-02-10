from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import time


def get_protocol_links(url, save=False) -> list[str]:
    driver = webdriver.Chrome()
    driver.get(url)
    match_ids = set()
    last_count = 0

    while True:
        links = driver.find_elements(By.XPATH, "//a[contains(@href,'/protocol/shf_a')]")

        for link in links:
            href = link.get_attribute("href")
            match = re.search(r"/match/(\d+)/", href)
            if match:
                match_ids.add(match.group(1))

        # stop when no new matches appear
        if len(match_ids) == last_count:
            break

        last_count = len(match_ids)

        # scroll down to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
    driver.quit()
    if save:
        path = Path("./data/protocols/match_ids.txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open("./data/protocols/match_ids.txt", "w") as f:
            for mid in match_ids:
                f.write(f"{mid}\n")
    return list(match_ids)

# If run as a script, create a driver, open the league page and print found links.
if __name__ == "__main__":
    found = get_protocol_links("https://www.profixio.com/app/leagueid17792/category/1171266?segment=historikk", save=True)
    print(f"Found {len(found)} matches:")
    for mid in found:
        print(mid)

