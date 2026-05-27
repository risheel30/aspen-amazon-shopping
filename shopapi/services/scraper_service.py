import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def extract_asin(url):
    m = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", url)
    if m:
        return m.group(1)
    return None


def parse_price(text):
    if not text:
        return None
    cleaned = re.sub(r"[^0-9.,]", "", text)
    cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def detect_currency(text):
    if not text:
        return None
    if "$" in text:
        return "USD"
    if "₹" in text or "Rs" in text or "INR" in text:
        return "INR"
    if "£" in text:
        return "GBP"
    if "€" in text:
        return "EUR"
    return None


def fetch_product(url):
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
    html = response.text
    return parse_product_html(html, url)


def parse_product_html(html, url):
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.select_one("#productTitle")
    title = title_el.get_text(strip=True) if title_el else None

    price_text = None
    price_el = soup.select_one("span.a-price span.a-offscreen")
    if price_el:
        price_text = price_el.get_text(strip=True)

    list_price_text = None
    list_el = soup.select_one("span.a-price.a-text-price span.a-offscreen")
    if list_el:
        list_price_text = list_el.get_text(strip=True)

    brand = None
    brand_el = soup.select_one("#bylineInfo")
    if brand_el:
        brand = brand_el.get_text(strip=True)

    seller = None
    seller_el = soup.select_one("#sellerProfileTriggerId")
    if seller_el:
        seller = seller_el.get_text(strip=True)

    availability = None
    avail_el = soup.select_one("#availability span")
    if avail_el:
        availability = avail_el.get_text(strip=True)

    rating = None
    rating_el = soup.select_one("span.a-icon-alt")
    if rating_el:
        m = re.search(r"([0-9.]+)\s*out of", rating_el.get_text(strip=True))
        if m:
            rating = float(m.group(1))

    review_count = None
    rc_el = soup.select_one("#acrCustomerReviewText")
    if rc_el:
        m = re.search(r"([0-9,]+)", rc_el.get_text(strip=True))
        if m:
            review_count = int(m.group(1).replace(",", ""))

    bullets = []
    for li in soup.select("#feature-bullets ul li span.a-list-item"):
        text = li.get_text(strip=True)
        if text:
            bullets.append(text)

    description = None
    desc_el = soup.select_one("#productDescription")
    if desc_el:
        description = desc_el.get_text(" ", strip=True)

    images = []
    main_img = soup.select_one("#landingImage")
    if main_img and main_img.get("src"):
        images.append({"url": main_img["src"], "is_main": True, "position": 0})
    for idx, img in enumerate(soup.select("#altImages img"), start=1):
        src = img.get("src") or ""
        if src and src not in [i["url"] for i in images]:
            images.append({"url": src, "is_main": False, "position": idx})

    specs = []
    for row in soup.select("#productDetails_techSpec_section_1 tr"):
        th = row.select_one("th")
        td = row.select_one("td")
        if th and td:
            specs.append({"key": th.get_text(strip=True), "value": td.get_text(" ", strip=True)})
    for row in soup.select("#productDetails_detailBullets_sections1 tr"):
        th = row.select_one("th")
        td = row.select_one("td")
        if th and td:
            specs.append({"key": th.get_text(strip=True), "value": td.get_text(" ", strip=True)})

    variants = []
    for li in soup.select("#variation_size_name li"):
        val = li.get("title") or li.get_text(strip=True)
        asin = li.get("data-defaultasin")
        if val:
            variants.append({"kind": "size", "value": val, "asin": asin})
    for li in soup.select("#variation_color_name li"):
        val = li.get("title") or li.get_text(strip=True)
        asin = li.get("data-defaultasin")
        if val:
            variants.append({"kind": "color", "value": val, "asin": asin})

    return {
        "asin": extract_asin(url),
        "url": url,
        "title": title,
        "brand": brand,
        "seller": seller,
        "availability": availability,
        "price_amount": parse_price(price_text),
        "price_currency": detect_currency(price_text),
        "list_price_amount": parse_price(list_price_text),
        "rating": rating,
        "review_count": review_count,
        "description": description,
        "feature_bullets": bullets,
        "images": images,
        "specs": specs,
        "variants": variants,
    }
