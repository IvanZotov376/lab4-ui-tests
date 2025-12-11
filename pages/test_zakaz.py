from selenium import webdriver #модуль автоматизации для браузера
from selenium.webdriver.common.by import By #модуль для поиска элементов на странице
from selenium.webdriver.support.ui import WebDriverWait #класс для ожидания в браузере
from selenium.webdriver.support import expected_conditions as EC #набор условий
import time #модуль для работы со временем
import os #работа с адресацией

class BasePage:
    def __init__(self, driver): #инициализация страницы
        self.driver = driver #экземпляр драйвера
        self.wait = WebDriverWait(driver, 10) #ожидание открытия браузера
    def find_element(self, by, value): #функция поиска элемента
        return self.wait.until(EC.presence_of_element_located((by, value)))
    def find_clickable_element(self, by, value): #функция поиска интерактивного элемента
        return self.wait.until(EC.element_to_be_clickable((by, value)))
    def click(self, by, value): #функция клика 
        element = self.find_clickable_element(by, value) #поиск элемента по значению
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)#прокрутка при поиске
        time.sleep(0.5)
        element.click()
    def send_keys(self, by, value, text):#функиця ввода
        element = self.find_element(by, value)
        element.clear()
        element.send_keys(text)

class ContactPage(BasePage): #реализация паттерна
    # Локаторы
    FULL_NAME_INPUT = (By.ID, "full-name")
    PHONE_INPUT = (By.ID, "phone")
    ADDRESS_INPUT = (By.ID, "address")
    AGREEMENT_CHECKBOX = (By.ID, "agreement-checkbox")
    CHECKOUT_BUTTON = (By.ID, "checkout-btn")
    # Локаторы для ошибок
    FULL_NAME_ERROR = (By.ID, "full-name-error")
    PHONE_ERROR = (By.ID, "phone-error")
    ADDRESS_ERROR = (By.ID, "address-error")
    AGREEMENT_ERROR = (By.ID, "agreement-error")
    def __init__(self, driver): # Инициализирует self.driver и self.wait через родительский класс
        super().__init__(driver)
        self.driver = driver
        #далее функции ввода данных
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
            self.driver.execute_script("arguments[0].click();", checkbox)
    
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

def debug_form_state(driver, page):
    """Функция для отладки состояния формы"""
    print("\nДИАГНОСТИКА ФОРМЫ ")
    form_data = page.get_form_data()#проверка данных формы
    print(f"Данные формы: {form_data}")
    #проверка наличия данных в форме
    try:
        cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
        print(f"Товаров в корзине: {len(cart_items)}")
        if len(cart_items) == 0:
            print("Ошибка: корзина пуста")
            # проверка отображения пустой корзины
            empty_cart = driver.find_elements(By.CLASS_NAME, "empty-cart")
            if empty_cart:
                print("✓ Отображается сообщение о пустой корзине")
    except Exception as e:
        print(f"Ошибка при проверке корзины: {e}")
    try:#проверка кнопки оформления заказа
        checkout_btn = driver.find_element(By.ID, "checkout-btn")
        print(f"Кнопка оформления: enabled={checkout_btn.is_enabled()}, displayed={checkout_btn.is_displayed()}")
    except Exception as e:
        print(f"Ошибка при проверке кнопки: {e}")
    
    print("ОКОНЧАНИЕ ДИАГНОСТИКИ\n")

def test_successful_order_submission():
    """Позитивный тест: успешное оформление заказа"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    contact_page = ContactPage(driver)
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"file://{os.path.join(current_dir, 'zakaz.html')}"
        
        print(f"Открытие страницы: {file_path}")
        driver.get(file_path)#получение пути для открытия
        time.sleep(3)  # ВРЕМЯ НА ЗАГРУЗКУ
        # Диагностика перед заполнением
        debug_form_state(driver, contact_page)
        print("Заполнение формы")
        # далее заполнение данных
        contact_page.fill_full_name("Иван")
        time.sleep(1)
        # Вводим телефон простым способом
        contact_page.fill_phone_simple("89041234567")
        time.sleep(1)
        contact_page.fill_address("г. Москва, ул. Примерная, д. 1, кв. 1")
        time.sleep(1)
        # Прокручиваем к чекбоксу и отмечаем его
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        contact_page.check_agreement()
        time.sleep(1)
        
        # Диагностика после заполнения
        debug_form_state(driver, contact_page)
        
        print("Отправка формы")
        # Прокручиваем к кнопке и нажимаем
        checkout_btn = driver.find_element(By.ID, "checkout-btn")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkout_btn)
        time.sleep(1)
        
        # Пробуем разные способы клика
        print("Попытка 1")
        checkout_btn.click()
        # Ждем возможного alert
        print("Ожидание сообщения")
        time.sleep(5)
        # Проверяем наличие alert
        try:#работа с модальными окнами
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"Окно найдено! Текст: {alert_text}")
            # Закрытие alert
            alert.accept()
            print("Окно закрыто")
            # Проверяем содержание alert
            if "Заказ оформлен" in alert_text: #при успешном оформлении
                print("Тест пройден: заказ успешно оформлен")
                return True
            else:
                print(f"Alert не содержит ожидаемый текст: {alert_text}")
                return False
        except Exception as e:
            print(f"Alert не появился: {e}")
            
            # Пробуем альтернативный способ клика
            print("Пробуем клик через JavaScript...")
            driver.execute_script("arguments[0].click();", checkout_btn)
            time.sleep(5)
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"AСообщение найдено после JS клика! Текст: {alert_text}")
                alert.accept()
                return True
            except:
                print("Сообщение не появилось даже после JS клика")
                # Сохранение скриншота об ошибке
                driver.save_screenshot("no_alert_error.png")
                print("Скриншот сохранен: no_alert_error.png")
                return False
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        driver.save_screenshot("critical_error.png")
        return False
    finally:
        driver.quit() #выход из браузера

def test_form_validation():
    """Тест валидации формы"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    contact_page = ContactPage(driver)
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"file://{os.path.join(current_dir, 'zakaz.html')}"
        print(f"Открытие страницы {file_path}")
        driver.get(file_path)
        time.sleep(3)
        
        print("Заполнение формы")
        
        # Заполняем все поля кроме имени
        contact_page.fill_phone_simple("89041234567")
        contact_page.fill_address("г. Москва, ул. Примерная, д. 1, кв. 1")
        
        # Прокручиваем и отмечаем чекбокс
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        contact_page.check_agreement()
        time.sleep(1)
        
        print("Отправка формы...")
        contact_page.submit_form()
        time.sleep(2)
    
        errors = []#проверка на ошибки
        try:
            name_error = driver.find_element(By.ID, "full-name-error")
            if name_error.is_displayed():
                errors.append("name")
                print(f"Ошибка имени: {name_error.text}")
        except:
            pass
            
        try:
            phone_error = driver.find_element(By.ID, "phone-error")
            if phone_error.is_displayed():
                errors.append("phone")
                print(f"Ошибка телефона: {phone_error.text}")
        except:
            pass
            
        try:
            address_error = driver.find_element(By.ID, "address-error")
            if address_error.is_displayed():
                errors.append("address")
                print(f"Ошибка адреса: {address_error.text}")
        except:
            pass
        
        print(f"Найдены ошибки: {errors}")
        
        # Проверяем, что есть ошибка имени
        if "name" in errors:
            print("Тест валидации пройден")
            return True
        else:
            print("Ошибка имени не найдена")
            return False
            
    except Exception as e:
        print(f"Ошибка в тесте валидации: {e}")
        return False
    finally:
        driver.quit()

def simple_smoke_test():
    """Тест 1"""
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = f"file://{os.path.join(current_dir, 'zakaz.html')}"
        
        print(f"Запуск теста №1...")
        print(f"Открытие {file_path}")
        driver.get(file_path)
        time.sleep(3)
        
        # Проверяем основные элементы
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
                print(f"{description} ЕСТЬ")
            except Exception as e:
                print(f"{description} ОТСУТСТВУЕТ: {e}")
                all_elements_found = False
        
        # Проверяем заголовок
        title = driver.title
        print(f"Заголовок страницы: {title}")
        
        #Проверка наличия товаров в корзине
        try:
            cart_items = driver.find_elements(By.CLASS_NAME, "cart-item")
            empty_cart = driver.find_elements(By.CLASS_NAME, "empty-cart")
            
            if cart_items:
                print(f"В корзине товаров: {len(cart_items)}")
            elif empty_cart:
                print("Корзина пуста")
            else:
                print("Не удалось определить состояние корзины")
                
        except Exception as e:
            print(f"Ошибка при проверке корзины: {e}")
        
        return all_elements_found
        
    except Exception as e:
        print(f"Ошибка в тесте: {e}")
        return False
    finally:
        driver.quit()

# Запуск тестов
if __name__ == "__main__":
    print("Запуск тестов формы оформления заказа")
    print("=" * 60)
    
    results = []
    
    #Первый тест
    print("\nТест №1")
    smoke_result = simple_smoke_test()
    results.append(("Открытие страницы", smoke_result))
    
    if smoke_result:
        print("\nТест №2")
        order_result = test_successful_order_submission()
        results.append(("Оформление заказа", order_result))
        
        print("\nТест №3")
        validation_result = test_form_validation()
        results.append(("Валидация формы", validation_result))
    else:
        print("\nПервый тест не пройден, тестирование закончено")#недопуск до следующих тестов
        results.append(("Оформление заказа", False))
        results.append(("Валидация формы", False))
    for test_name, result in results:
        status = " ПРОЙДЕН" if result else " НЕ ПРОЙДЕН"
        print(f"{test_name}: {status}")
    # Общий результат
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\nВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
    else:
        print(f"\nВСЕГО ТЕСТОВ: {sum(result for _, result in results)}/{len(results)}")
        print("Проверьте скриншоты и логи для диагностики")