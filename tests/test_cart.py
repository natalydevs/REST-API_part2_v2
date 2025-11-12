# tests/test_cart.py
import requests
from allure_commons._allure import step
from allure_commons.types import AttachmentType
from selene import browser, have
import allure

from conftest import BASE_URL


def test_cart_has_1_item_after_adding_single_product():
    product_id = 31  # 14.1-inch Laptop
    session = requests.Session()

    with step("Инициализировать guest-сессию"):
        session.get(BASE_URL)

    url = f"{BASE_URL}/addproducttocart/catalog/{product_id}/1/1"
    payload = {f"addtocart_{product_id}.EnteredQuantity": "1"}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*",
    }

    with step("Добавить товар в корзину через API"):
        # лог запроса (консоль + allure)
        print(f"REQUEST: POST {url}\nHEADERS: {headers}\nPAYLOAD: {payload}")
        allure.attach(
            body=f"POST {url}\n\nHEADERS:\n{headers}\n\nPAYLOAD:\n{payload}",
            name="API request",
            attachment_type=AttachmentType.TEXT,
        )

        response = session.post(url, data=payload, headers=headers)

        # лог ответа
        allure.attach(body=response.text, name="API response", attachment_type=AttachmentType.TEXT)
        assert response.status_code == 200
        assert '"success":true' in response.text.lower()

    with step("Проверить cookie гостя"):
        nop_customer = session.cookies.get("Nop.customer")
        allure.attach(body=str(nop_customer), name="Nop.customer", attachment_type=AttachmentType.TEXT)
        assert nop_customer is not None

    with step("Открыть сайт и проверить, что в корзине (1)"):
        browser.open("/")
        browser.driver.delete_all_cookies()
        browser.driver.add_cookie({"name": "Nop.customer", "value": nop_customer, "path": "/"})
        browser.open("/")
        browser.element(".cart-qty").should(have.text("(1)"))


def test_cart_has_2_items_after_adding_same_product_twice():
    product_id = 31  # простой товар без опций
    session = requests.Session()

    with step("Инициализировать guest-сессию"):
        session.get(BASE_URL)

    url = f"{BASE_URL}/addproducttocart/catalog/{product_id}/1/1"
    payload = {f"addtocart_{product_id}.EnteredQuantity": "1"}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*",
    }

    with step("Добавить товар 1-й раз"):
        print(f"REQUEST #1: POST {url}\nHEADERS: {headers}\nPAYLOAD: {payload}")
        allure.attach(
            body=f"POST {url}\n\nHEADERS:\n{headers}\n\nPAYLOAD:\n{payload}",
            name="Request #1",
            attachment_type=AttachmentType.TEXT,
        )
        r1 = session.post(url, data=payload, headers=headers)
        allure.attach(r1.text, "Response #1", AttachmentType.TEXT)
        assert r1.status_code == 200
        assert '"success":true' in r1.text.lower()
        assert "(1)" in r1.text

    with step("Добавить товар 2-й раз"):
        print(f"REQUEST #2: POST {url}\nHEADERS: {headers}\nPAYLOAD: {payload}")
        allure.attach(
            body=f"POST {url}\n\nHEADERS:\n{headers}\n\nPAYLOAD:\n{payload}",
            name="Request #2",
            attachment_type=AttachmentType.TEXT,
        )
        r2 = session.post(url, data=payload, headers=headers)
        allure.attach(r2.text, "Response #2", AttachmentType.TEXT)
        assert r2.status_code == 200
        assert '"success":true' in r2.text.lower()
        assert "(2)" in r2.text

    with step("Проверить, что в корзине (2)"):
        nop_customer = session.cookies.get("Nop.customer")
        assert nop_customer is not None
        browser.open("/")
        browser.driver.delete_all_cookies()
        browser.driver.add_cookie({"name": "Nop.customer", "value": nop_customer, "path": "/"})
        browser.open("/")
        browser.element(".cart-qty").should(have.text("(2)"))


def test_invalid_product_does_not_change_cart_count():
    invalid_product_id = 999_999
    session = requests.Session()

    with step("Инициализировать guest-сессию"):
        session.get(BASE_URL)

    url = f"{BASE_URL}/addproducttocart/catalog/{invalid_product_id}/1/1"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*",
    }

    with step("Попробовать добавить невалидный товар"):
        print(f"REQUEST: POST {url}\nHEADERS: {headers}\nPAYLOAD: None")
        allure.attach(
            body=f"POST {url}\n\nHEADERS:\n{headers}\n\nPAYLOAD:\nNone",
            name="Invalid product request",
            attachment_type=AttachmentType.TEXT,
        )
        response = session.post(url, headers=headers)
        allure.attach(response.text, "Invalid product response", AttachmentType.TEXT)
        assert response.status_code == 200
        assert '"success":false' in response.text.lower()

    with step("Проверить, что корзина пуста"):
        nop_customer = session.cookies.get("Nop.customer")
        assert nop_customer is not None
        browser.open("/")
        browser.driver.delete_all_cookies()
        browser.driver.add_cookie({"name": "Nop.customer", "value": nop_customer, "path": "/"})
        browser.open("/")
        browser.element(".cart-qty").should(have.text("(0)"))
