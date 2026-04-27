from playwright.sync_api import sync_playwright


BASE_URL = "https://flexilock.xyz"

TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword123"


def test_homepage_loads():
    """
    Test whether the FlexiLock homepage can be opened.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(BASE_URL, wait_until="networkidle")

        content = page.content()
        title = page.title()

        assert "FlexiLock" in title or "FlexiLock" in content

        browser.close()


def test_login_page_loads():
    """
    Test whether the login page loads and contains username/password inputs.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(f"{BASE_URL}/login/", wait_until="networkidle")

        assert page.locator("input[name='username']").is_visible()
        assert page.locator("input[name='password']").is_visible()

        browser.close()


def test_user_login():
    """
    Test login using a prepared test account.
    Replace TEST_USERNAME and TEST_PASSWORD before running this test.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(f"{BASE_URL}/login/", wait_until="networkidle")

        page.fill("input[name='username']", TEST_USERNAME)
        page.fill("input[name='password']", TEST_PASSWORD)
        page.click("button[type='submit']")

        page.wait_for_load_state("networkidle")

        page_content = page.content().lower()
        page_url = page.url.lower()

        assert "logout" in page_content or "dashboard" in page_url or "dashboard" in page_content

        browser.close()


def test_lockers_api():
    """
    Test whether the locker status API returns JSON data.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        response = page.request.get(f"{BASE_URL}/api/lockers/")

        assert response.status == 200

        data = response.json()

        assert "lockers" in data
        assert isinstance(data["lockers"], list)

        browser.close()


def test_qr_verify_api_invalid_token():
    """
    Test QR verification API using an invalid token.
    The server should reject it.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        response = page.request.post(
            f"{BASE_URL}/api/test-verify-qr/",
            data={
                "token": "invalid-test-token"
            }
        )

        assert response.status in [200, 400, 401, 403]

        data = response.json()

        assert data.get("valid") is False or "error" in data

        browser.close()