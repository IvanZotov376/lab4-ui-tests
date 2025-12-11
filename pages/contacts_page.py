from .base_page import BasePage
from selenium.webdriver.common.by import By

class ContactPage(BasePage):
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
        return {
            'name': self.find_element(*self.FULL_NAME_INPUT).get_attribute('value'),
            'phone': self.find_element(*self.PHONE_INPUT).get_attribute('value'),
            'address': self.find_element(*self.ADDRESS_INPUT).get_attribute('value'),
            'agreement': self.find_element(*self.AGREEMENT_CHECKBOX).is_selected()
        }