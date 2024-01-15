from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_dentistas_from_unimed_odonto(driver):

    driver.get("https://www.unimedodonto.com.br/guia-odonto")

    form_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "form"))
    )

    input_elements = form_element.find_elements(By.TAG_NAME, "input")

    for input_element in input_elements:
        label = input_element.find_element(By.XPATH, f'../label') # label[@for="{input_element.get_attribute("id")}"]
        print(f"Label Text:", label.text)

