import os
import tempfile

_TMP_DB = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP_DB.close()
os.environ["SHOP_DB_URL"] = f"sqlite:///{_TMP_DB.name}"
os.environ["SHOP_API_KEY"] = "test-key"

import pytest

from shopapi.db import reset_db
from shopapi.main import app as flask_app
import shopapi.services.scraper_service as scraper_mod


@pytest.fixture(autouse=True)
def _reset_db_between_tests():
    reset_db()
    yield


@pytest.fixture
def app():
    return flask_app


@pytest.fixture
def client():
    return flask_app.test_client()


@pytest.fixture
def auth_valid():
    return {"X-API-Key": "test-key"}


@pytest.fixture
def auth_invalid():
    return {"X-API-Key": "wrong-key"}


SAMPLE_PRODUCT_HTML = """
<html><body>
<span id="productTitle">Sony WH-1000XM5 Headphones</span>
<span class="a-price"><span class="a-offscreen">$348.00</span></span>
<span class="a-price a-text-price"><span class="a-offscreen">$399.99</span></span>
<a id="bylineInfo">Visit the Sony Store</a>
<a id="sellerProfileTriggerId">Amazon.com</a>
<div id="availability"><span>In Stock</span></div>
<span class="a-icon-alt">4.6 out of 5 stars</span>
<span id="acrCustomerReviewText">12,345 ratings</span>
<div id="feature-bullets"><ul>
<li><span class="a-list-item">Industry leading noise cancellation</span></li>
<li><span class="a-list-item">Up to 30 hours battery life</span></li>
</ul></div>
<div id="productDescription"><p>Premium wireless headphones with great sound.</p></div>
<img id="landingImage" src="https://m.media-amazon.com/images/I/main.jpg" />
<div id="altImages">
<img src="https://m.media-amazon.com/images/I/alt1.jpg" />
<img src="https://m.media-amazon.com/images/I/alt2.jpg" />
</div>
<table id="productDetails_techSpec_section_1">
<tr><th>Color</th><td>Black</td></tr>
<tr><th>Weight</th><td>250 g</td></tr>
</table>
<ul id="variation_color_name">
<li title="Black" data-defaultasin="B0AAA00001"></li>
<li title="Silver" data-defaultasin="B0AAA00002"></li>
</ul>
</body></html>
"""


ROBOT_CHECK_HTML = """
<html><head><title>Robot Check</title></head><body>
<h4>Enter the characters you see below</h4>
<p>Sorry, we just need to make sure you're not a robot.</p>
</body></html>
"""


class FakeResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


@pytest.fixture
def fake_amazon_ok(monkeypatch):
    def _get(url, headers=None, timeout=None):
        return FakeResponse(200, SAMPLE_PRODUCT_HTML)

    monkeypatch.setattr(scraper_mod.requests, "get", _get)
