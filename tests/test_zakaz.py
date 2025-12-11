from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def find_element(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))
    
    def find_clickable_element(self, by, value):
        return self.wait.until(EC.element_to_be_clickable((by, value)))
    
    def click(self, by, value):
        element = self.find_clickable_element(by, value)
        element.click()
    
    def send_keys(self, by, value, text):
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)

class ContactPage(BasePage):
    # Локаторы
    FULL_NAME_INPUT = (By.ID, "full-name")
    PHONE_INPUT = (By.ID, "phone")
    ADDRESS_INPUT = (By.ID, "address")
    AGREEMENT_CHECKBOX = (By.ID, "agreement-checkbox")
    CHECKOUT_BUTTON = (By.ID, "checkout-btn")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
    
    def fill_full_name(self, name):
        self.send_keys(*self.FULL_NAME_INPUT, name)
    
    def fill_phone_simple(self, phone):
        """Ввод номера телефона"""
        phone_field = self.find_element(*self.PHONE_INPUT)
        phone_field.clear()
        phone_field.send_keys(phone)
    
    def fill_address(self, address):
        self.send_keys(*self.ADDRESS_INPUT, address)
    
    def check_agreement(self):
        checkbox = self.find_element(*self.AGREEMENT_CHECKBOX)
        if not checkbox.is_selected():
            checkbox.click()
    
    def submit_form(self):
        self.click(*self.CHECKOUT_BUTTON)
    
    def get_form_data(self):
        """Получаем текущие данные из формы для отладки"""
        return {
            'name': self.find_element(*self.FULL_NAME_INPUT).get_attribute('value'),
            'phone': self.find_element(*self.PHONE_INPUT).get_attribute('value'),
            'address': self.find_element(*self.ADDRESS_INPUT).get_attribute('value'),
            'agreement': self.find_element(*self.AGREEMENT_CHECKBOX).is_selected()
        }

def setup_driver(headless=True):
    """Настройка драйвера для CI (без webdriver-manager)"""
    chrome_options = Options()
    
    if headless:
        # Используем новый headless режим
        chrome_options.add_argument('--headless=new')
    else:
        chrome_options.add_argument('--headless')  # Стандартный headless для локального запуска
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Для CI используем системный chromedriver
    # В GitHub Actions он будет установлен по пути /usr/local/bin/chromedriver
    # Для локального запуска можно использовать 'chromedriver' (если в PATH)
    service = Service('/usr/local/bin/chromedriver')
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Ошибка при создании драйвера: {e}")
        print("Пробуем использовать драйвер без указания пути...")
        # Альтернативный вариант
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Для режима с GUI
    if not headless:
        driver.maximize_window()
    
    return driver

def debug_form_state(driver, page):
    """Функция для отладки состояния формы"""
    print("\n" + "="*60)
    print("ДИАГНОСТИКА ФОРМЫ")
    print("="*60)
    
    form_data = page.get_form_data()
    print(f"Данные формы: {form_data}")
    
    # Проверка наличия данных в форме
    try:
        cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
        print(f"Товаров в корзине: {len(cart_items)}")
        if len(cart_items) == 0:
            print("Внимание: корзина пуста")
    except Exception as e:
        print(f"Ошибка при проверке корзины: {e}")
    
    try:
        checkout_btn = driver.find_element(By.ID, "checkout-btn")
        print(f"Кнопка оформления: enabled={checkout_btn.is_enabled()}")
    except Exception as e:
        print(f"Ошибка при проверке кнопки: {e}")
    
    print("="*60 + "\n")

def test_successful_order_submission():
    """Позитивный тест: успешное оформление заказа"""
    print("="*60)
    print("ТЕСТ: Успешное оформление заказа")
    print("="*60)
    
    # Используем headless режим для CI
    is_ci = os.environ.get('CI') == 'true'
    driver = setup_driver(headless=is_ci)
    contact_page = ContactPage(driver)
    
    try:
        # Получаем путь к HTML файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"file://{os.path.join(current_dir, '../test_data/zakaz.html')}"
        
        print(f"Открытие страницы: {file_path}")
        driver.get(file_path)
        time.sleep(2)  # Даем время на загрузку
        
        # Диагностика перед заполнением
        debug_form_state(driver, contact_page)
        
        print("Заполнение формы...")
        
        # Заполняем форму
        contact_page.fill_full_name("Иван Иванов")
        time.sleep(0.5)
        
        # Вводим телефон
        contact_page.fill_phone_simple("89041234567")
        time.sleep(0.5)
        
        contact_page.fill_address("г. Москва, ул. Примерная, д. 1, кв. 1")
        time.sleep(0.5)
        
        # Прокручиваем к чекбоксу
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        
        # Отмечаем чекбокс
        contact_page.check_agreement()
        time.sleep(0.5)
        
        # Диагностика после заполнения
        debug_form_state(driver, contact_page)
        
        print("Отправка формы...")
        
        # Прокручиваем к кнопке оформления
        checkout_btn = driver.find_element(By.ID, "checkout-btn")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_btn)
        time.sleep(0.5)
        
        # Нажимаем кнопку
        checkout_btn.click()
        time.sleep(3)  # Ждем обработки
        
        # Проверяем наличие alert
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"Alert найден! Текст: {alert_text}")
            
            # Проверяем содержание alert
            if "Заказ оформлен" in alert_text:
                print("✓ ТЕСТ ПРОЙДЕН: заказ успешно оформлен")
                alert.accept()
                return True
            else:
                print(f"✗ Alert не содержит ожидаемый текст: {alert_text}")
                alert.accept()
                return False
                
        except Exception as e:
            print(f"✗ Alert не появился: {e}")
            
            # Делаем скриншот для отладки
            screenshot_path = "test_failure.png"
            driver.save_screenshot(screenshot_path)
            print(f"Скриншот сохранен: {screenshot_path}")
            
            return False
            
    except Exception as e:
        print(f"✗ Критическая ошибка: {e}")
        driver.save_screenshot("critical_error.png")
        return False
        
    finally:
        driver.quit()
        print("Драйвер закрыт")
        print("="*60 + "\n")

def test_form_validation():
    """Тест валидации формы (отрицательный сценарий)"""
    print("="*60)
    print("ТЕСТ: Валидация формы (проверка ошибок)")
    print("="*60)
    
    # Используем headless режим для CI
    is_ci = os.environ.get('CI') == 'true'
    driver = setup_driver(headless=is_ci)
    contact_page = ContactPage(driver)
    
    try:
        # Получаем путь к HTML файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"file://{os.path.join(current_dir, '../test_data/zakaz.html')}"
        
        print(f"Открытие страницы: {file_path}")
        driver.get(file_path)
        time.sleep(2)
        
        print("Заполнение формы без имени...")
        
        # Заполняем все поля кроме имени
        contact_page.fill_phone_simple("89041234567")
        time.sleep(0.5)
        
        contact_page.fill_address("г. Москва, ул. Примерная, д. 1, кв. 1")
        time.sleep(0.5)
        
        # Прокручиваем и отмечаем чекбокс
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        contact_page.check_agreement()
        time.sleep(0.5)
        
        print("Отправка формы...")
        contact_page.submit_form()
        time.sleep(2)
        
        # Проверяем ошибки
        errors_found = []
        
        try:
            name_error = driver.find_element(By.ID, "full-name-error")
            if name_error.is_displayed():
                errors_found.append("name")
                print(f"✓ Ошибка имени отображается: {name_error.text}")
            else:
                print("✗ Ошибка имени не отображается")
        except Exception as e:
            print(f"✗ Не удалось найти ошибку имени: {e}")
        
        # Проверяем, что нет других ошибок
        try:
            phone_error = driver.find_element(By.ID, "phone-error")
            if phone_error.is_displayed():
                errors_found.append("phone")
                print(f"✗ Неожиданная ошибка телефона: {phone_error.text}")
        except:
            pass  # Ошибка телефона не должна отображаться
        
        try:
            address_error = driver.find_element(By.ID, "address-error")
            if address_error.is_displayed():
                errors_found.append("address")
                print(f"✗ Неожиданная ошибка адреса: {address_error.text}")
        except:
            pass  # Ошибка адреса не должна отображаться
        
        print(f"Найдены ошибки: {errors_found}")
        
        # Тест пройден, если есть только ошибка имени
        if errors_found == ["name"]:
            print("✓ ТЕСТ ПРОЙДЕН: валидация работает корректно")
            return True
        else:
            print(f"✗ ТЕСТ НЕ ПРОЙДЕН: ожидалась только ошибка имени, а найдены: {errors_found}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка в тесте валидации: {e}")
        return False
        
    finally:
        driver.quit()
        print("Драйвер закрыт")
        print("="*60 + "\n")

def simple_smoke_test():
    """Простой smoke-тест: проверка доступности страницы и элементов"""
    print("="*60)
    print("ТЕСТ: Smoke test (базовая проверка)")
    print("="*60)
    
    # Используем headless режим для CI
    is_ci = os.environ.get('CI') == 'true'
    driver = setup_driver(headless=is_ci)
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"file://{os.path.join(current_dir, '../test_data/zakaz.html')}"
        
        print(f"Открытие страницы: {file_path}")
        driver.get(file_path)
        time.sleep(2)
        
        print("Проверка основных элементов...")
        
        # Элементы для проверки
        elements_to_check = [
            ("full-name", "Поле имени"),
            ("phone", "Поле телефона"),
            ("address", "Поле адреса"),
            ("checkout-btn", "Кнопка оформления"),
            ("agreement-checkbox", "Чекбокс согласия")
        ]
        
        all_elements_found = True
        
        for element_id, description in elements_to_check:
            try:
                element = driver.find_element(By.ID, element_id)
                if element.is_displayed():
                    print(f"✓ {description} найден и отображается")
                else:
                    print(f"✗ {description} найден, но не отображается")
                    all_elements_found = False
            except Exception as e:
                print(f"✗ {description} не найден: {e}")
                all_elements_found = False
        
        # Проверяем заголовок страницы
        title = driver.title
        print(f"Заголовок страницы: {title}")
        
        # Проверяем наличие товаров в корзине
        try:
            cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
            
            if cart_items:
                print(f"✓ В корзине товаров: {len(cart_items)}")
            else:
                # Проверяем, есть ли сообщение о пустой корзине
                empty_cart = driver.find_elements(By.CLASS_NAME, "empty-cart")
                if empty_cart:
                    print("✓ Корзина пуста (ожидаемое состояние)")
                else:
                    print("⚠ Не удалось определить состояние корзины")
                    
        except Exception as e:
            print(f"⚠ Ошибка при проверке корзины: {e}")
        
        if all_elements_found:
            print("✓ SMOKE TEST ПРОЙДЕН: все основные элементы присутствуют")
        else:
            print("✗ SMOKE TEST НЕ ПРОЙДЕН: некоторые элементы отсутствуют")
        
        return all_elements_found
        
    except Exception as e:
        print(f"✗ Ошибка в smoke test: {e}")
        return False
        
    finally:
        driver.quit()
        print("Драйвер закрыт")
        print("="*60 + "\n")

# Запуск тестов
if __name__ == "__main__":
    print("\n" + "="*60)
    print("ЗАПУСК ТЕСТОВ ФОРМЫ ОФОРМЛЕНИЯ ЗАКАЗА")
    print("="*60 + "\n")
    
    results = []
    
    # Запускаем smoke test
    print("[1/3] Запуск smoke test...")
    smoke_result = simple_smoke_test()
    results.append(("Smoke test", smoke_result))
    
    if smoke_result:
        # Если smoke test прошел, запускаем основные тесты
        print("\n[2/3] Запуск теста оформления заказа...")
        order_result = test_successful_order_submission()
        results.append(("Оформление заказа", order_result))
        
        print("\n[3/3] Запуск теста валидации формы...")
        validation_result = test_form_validation()
        results.append(("Валидация формы", validation_result))
    else:
        print("\n✗ Smoke test не пройден, пропускаем остальные тесты")
        results.append(("Оформление заказа", False))
        results.append(("Валидация формы", False))
    
    # Вывод результатов
    print("\n" + "="*60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    passed_count = 0
    for test_name, result in results:
        status = "✓ ПРОЙДЕН" if result else "✗ НЕ ПРОЙДЕН"
        print(f"{test_name:25} {status}")
        if result:
            passed_count += 1
    
    print("-" * 60)
    print(f"Всего тестов: {len(results)}")
    print(f"Пройдено: {passed_count}/{len(results)}")
    
    if passed_count == len(results):
        print("\n🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
    else:
        print(f"\n⚠ ПРОВАЛЕНО: {len(results) - passed_count} тест(ов)")
        print("Проверьте скриншоты и логи для диагностики")
    
    print("="*60)