from playwright.sync_api import sync_playwright
import re
import unicodedata

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

        functionextractlocations(page)
        browser.close()
        # Location Input → Google Maps Search → Wait for Results → Extract Visible Text → Save/Process


def functionextractlocations(page):
    page_url = page.url
    title = page.title()

    page.wait_for_timeout(3000)
    extracted_text = page.locator("body").inner_text(timeout=15000)

    # Normalize text
    text = unicodedata.normalize("NFKC", extracted_text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)

    # Remove common Google Maps UI garbage
    garbage_labels = {
        "rating",
        "you're seeing a limited view of google maps. see more",
" layers",
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
        "map data ©2026 globaltermsprivacySend Product Feedback".casefold(),
    }

    cleaned_lines = []
    seen_lines = set()

    for line in text.splitlines():
        # Remove Google Maps result-correction text
        if re.match(r"^Showing results for .* Search instead for ", line, re.IGNORECASE):
            continue

        # Remove embedded Google Maps icon symbols
        line = line.replace("", "").replace("", "").strip()

        if not line:
            continue
        line = line.strip()

        if not line:
            continue

        if line.casefold() in garbage_labels:
            continue

        if re.fullmatch(r"[^\w\s]+", line):
            continue

        key = line.casefold()
        if key not in seen_lines:
            seen_lines.add(key)
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    print("Google Maps URL:", page_url)
    print("Page Title:", title)
    print("Cleaned Results Text:")
    print(cleaned_text)

    return cleaned_text


if __name__ == "__main__":
    functionlocationgoogle()
