from playwright.sync_api import sync_playwright

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

    print("Google Maps URL:", page_url)
    print("Page Title:", title)
    print("Extracted Results Text:")
    print(extracted_text)

    return extracted_text
#Raw Text Extraction → Text Cleaning → 
# Har Business ko Separate Record mein Identify karna →
#  Name, Rating, Reviews, Category, Address, Opening Hours, 
# Phone, Website, Google Maps URL ko Extract karna → 
# Missing Information ko null rakhna → Har Business ko Separate JSON Object mein Store karna → JSON Validation → Database/CRM mein Save karna.

if __name__ == "__main__":
    functionlocationgoogle()

