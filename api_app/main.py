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
    feed = page.locator('div[role="feed"]')
    feed.wait_for(timeout=15000)

    # 1) Scroll karke saare results load karo
    prev = 0
    for _ in range(30):
        feed.evaluate("el => el.scrollBy(0, el.scrollHeight)")
        page.wait_for_timeout(1500)
        count = page.locator('div[role="feed"] a[href*="/maps/place/"]').count()
        if count == prev:
            break
        prev = count

    # 2) Har card se structured data
    phone_re = re.compile(r"(\+?\d[\d\s\-()]{7,}\d)")
    status_re = re.compile(
        r"^(Open|Closed|Opens|Closes|Temporarily closed|Permanently closed)", re.I
    )
    closed_re = re.compile(
        r"^(Closed|Temporarily closed|Permanently closed)", re.I
    )

    businesses = []
    seen = set()
    links = page.locator('div[role="feed"] a[href*="/maps/place/"]')

    for i in range(links.count()):
        link = links.nth(i)
        name = (link.get_attribute("aria-label") or "").strip()
        url = link.get_attribute("href")
        if not name or url in seen:
            continue
        seen.add(url)

        card = link.locator("xpath=..")  # card = a tag ka parent
        text = card.inner_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        # rating + reviews
        rating = reviews = None
        img = card.locator('span[role="img"]')
        if img.count():
            label = img.first.get_attribute("aria-label") or ""
            m = re.search(r"([\d.,]+)\s*stars?\s*([\d.,]+)?", label)
            if m:
                rating = float(m.group(1).replace(",", "."))
                reviews = int(re.sub(r"\D", "", m.group(2))) if m.group(2) else 0

        # status, category, address, phone
        status = category = address = phone = None
        def clean_part(s):
            s = unicodedata.normalize("NFKC", s)
            s = re.sub(r"[\u200b-\u200f\u2060\ufeff\ue000-\uf8ff]", "", s)  # zero-width + private-use icons
            return s.strip()
        for line in lines:
            if line == name or re.fullmatch(r"(Website|Directions)", line):
                continue
            if re.match(r"^(\d[.,]\d\(|No reviews)", line):  # rating line
                continue

            # phone kisi bhi line mein ho sakta hai
            pm = phone_re.search(line)
            if pm and phone is None and not re.fullmatch(r"[\d.,()]+", line):
                phone = pm.group(1).strip()
                line = line.replace(pm.group(1), "").strip(" ·")

            if not line:
                continue

            if status is None and status_re.match(line):
                status = line.split("·")[0].strip()
                continue

            if category is None:
                parts = [clean_part(p) for p in line.split("·")]
                parts = [p for p in parts if p]
                if parts:
                    category = parts[0]
                    if len(parts) > 1:
                        address = parts[1]
                continue

        # Closed wale skip
        if status and closed_re.match(status):
            continue

        web = card.locator('a[data-value="Website"]')
        coords = re.search(r"!3d(-?[\d.]+)!4d(-?[\d.]+)", url or "")

        businesses.append(
            {
                "name": name,
                "rating": rating,
                "reviews": reviews,
                "category": category,
                "address": address,
                "status": status,
                "phone": phone,
                "website": web.first.get_attribute("href") if web.count() else None,
                "lat": float(coords.group(1)) if coords else None,
                "lng": float(coords.group(2)) if coords else None,
                "maps_url": url,
                "raw_text": text,  # check karne ke baad hata dena
            }
        )

    data = {
        "search_query": search_location,
        "google_maps_url": page.url,
        "page_title": page.title(),
        "total": len(businesses),
        "businesses": businesses,
    }

    with open("companies.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(businesses)} businesses")
    return data

if __name__ == "__main__":
    functionlocationgoogle()
