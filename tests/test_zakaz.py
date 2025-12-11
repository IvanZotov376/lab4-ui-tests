from pages.contact_page import ContactPage
from selenium import webdriver
import os
import time

def test_successful_order_submission():
    """Позитивный тест: успешное оформление заказа"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    contact_page = ContactPage(driver)
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"file://{os.path.join(current_dir, '../test_data/zakaz.html')}"
        
        driver.get(file_path)
        time.sleep(3)
        
        # Заполнение формы
        contact_page.fill_full_name("Иван")
        contact_page.fill_phone_simple("89041234567")
        contact_page.fill_address("г. Москва, ул. Примерная, д. 1, кв. 1")
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        contact_page.check_agreement()
        time.sleep(1)
        
        # Отправка формы
        checkout_btn = driver.find_element_by_id("checkout-btn")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_btn)
        time.sleep(1)
        checkout_btn.click()
        
        time.sleep(3)
        
        # Проверка успешного оформления
        alert = driver.switch_to.alert
        alert_text = alert.text
        alert.accept()
        
        assert "Заказ оформлен" in alert_text, "Не удалось оформить заказ"
        
    finally:
        driver.quit()

def test_form_validation():
    """Тест валидации формы"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    contact_page = ContactPage(driver)
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"file://{os.path.join(current_dir, '../test_data/zakaz.html')}"
        
        driver.get(file_path)
        time.sleep(3)
        
        # Заполнение формы без имени
        contact_page.fill_phone_simple("89041234567")
        contact_page.fill_address("г. Москва, ул. Примерная, д. 1, кв. 1")
        contact_page.check_agreement()
        
        contact_page.submit_form()
        time.sleep(2)
        
        # Проверка ошибки
        name_error = driver.find_element_by_id("full-name-error")
        assert name_error.is_displayed(), "Ошибка имени не отображается"
        
    finally:
        driver.quit()