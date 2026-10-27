from playwright.sync_api import sync_playwright
import re
import unicodedata
import json

# Manual Location Input → Playwright Browser Launch → Geolocation Permission Setup → Google Maps Search → Results URL, Page Title aur Location Output.


def functionlocationgoogle(location_input=None):
    """
    Location Input → Browser Geolocation / Manual Search
    → Google Maps Search → Browser Results
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            geolocation={"latitude": 31.5204, "longitude": 74.3587},
            permissions=["geolocation"],
        )
        page = context.new_page()

        if location_input and location_input.strip():
            search_location = location_input.strip()
        else:
            page.goto("https://www.google.com/maps")
            print("Browser mein location permission allow karein.")
            search_location = input("Enter location manually: ").strip()

        if not search_location:
            print("Error: Location required.")
            browser.close()
            return

        page.goto("https://www.google.com/maps")
        page.get_by_role("combobox").first.fill(search_location)
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)

        print("Search location:", search_location)
        print("Google Maps URL:", page.url)
        print("Search page title:", page.title())

        functionextractlocations(page, search_location)
        browser.close()
        # Location Input → Google Maps Search → Wait for Results → Extract Visible Text → Save/Process


def functioncleantext(extracted_text):
    text = unicodedata.normalize("NFKC", extracted_text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)

    blocks = re.split(r"\n\s*Directions\s*\n", text + "\n")
    open_blocks = []
    for block in blocks:
        if re.search(
            r"^\s*(Closed|Temporarily closed|Permanently closed)\b",
            block,
            re.IGNORECASE | re.MULTILINE,
        ):
            continue
        open_blocks.append(block)
    text = "\n".join(open_blocks)

    garbage_labels = {
        "rating",
        "you're seeing a limited view of google maps. see more",
        "layers",
        "500 m",
        "hours",
        "all filters",
        "saved",
        "recents",
        "get app",
        "results",
        "share",
        "sign in",
        "directions",
        "website",
        "search this area",
        "update results when map moves",
        "map data ©2026 globaltermsprivacysend product feedback",
    }

    cleaned_lines = []
    seen_lines = set()
    for line in text.splitlines():
        if re.match(
            r"^Showing results for .* Search instead for ", line, re.IGNORECASE
        ):
            continue
        line = line.replace("", "").replace("", "").strip()
        if not line:
            continue
        if line.casefold() in garbage_labels:
            continue
        if re.fullmatch(r"[^\w\s]+", line):
            continue
        if re.fullmatch(r"\d+(\.\d+)?\s?(km|m|mi|ft)", line, re.IGNORECASE):
            continue
        key = line.casefold()
        if key not in seen_lines:
            seen_lines.add(key)
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def functionextractlocations(page, search_location):

    page_url = page.url
    title = page.title()

    page.wait_for_timeout(3000)
    extracted_text = page.locator("body").inner_text(timeout=15000)

    cleaned_text = functioncleantext(extracted_text)
    data = {
        "businesses": [],
        "google_maps_url": page_url,
        "page_title": title,
        "search_query": search_location,
        "extracted_text": cleaned_text,
    }

    print("Google Maps URL:", page_url)
    print("Page Title:", title)
    print("Cleaned Results Text:")
    print(cleaned_text)
    with open("companies.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return data


if __name__ == "__main__":
    functionlocationgoogle()
