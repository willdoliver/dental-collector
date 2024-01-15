from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from fastapi import FastAPI, HTTPException
from api.unimed import *
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()

chrome_opt = webdriver.ChromeOptions()
# chrome_opt.add_argument('--headless')
# chrome_opt.add_argument('--disable-extensions')
# chrome_opt.add_argument('--disable-gpu')
chrome_opt.add_argument('--no-sandbox')

@app.get("/get_dentistas_from_unimed")
def get_dentistas():

    chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'driver', os.getenv('CHROMEDRIVERFILE'))
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_opt)
    table_return = get_dentistas_from_unimed_odonto(driver)
    driver.close()
    return table_return.to_json(orient="records")
    

@app.get("/")
def hello():
    return {'status': 'alive'}