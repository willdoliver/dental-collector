import os
import re
import time
import random
import traceback, logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import WebDriverException, TimeoutException, UnexpectedAlertPresentException, NoSuchElementException
from api.models.metlife_model import DentistaModel
from api.models.metlife_summary_data_model import SummaryDataModel
from api.repositories.metlife.metlife_dentistas_repository import DentistaRepository
from api.repositories.metlife.metlife_sumary_data_repository import SummaryDataRepository
from dotenv import load_dotenv

from selenium.webdriver.chrome.options import Options
chrome_opt = Options()
# chrome_opt.add_experimental_option("detach", True)

# chrome_opt = webdriver.ChromeOptions()
chrome_opt.add_argument('--headless')
# chrome_opt.add_argument('--disable-popup-blocking')
# chrome_opt.add_argument('--disable-extensions')
chrome_opt.add_argument('--disable-gpu')
chrome_opt.add_argument('--no-sandbox')

load_dotenv()
metlife_repository = DentistaRepository()
summary_data_repository = SummaryDataRepository()

class MetLifeController():

    def find_dentistas_from_metlife(self):
        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'driver', os.getenv('CHROMEDRIVERFILE'))
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_opt)
        page_limit = 10

        try:
            driver.get("https://redecredenciada.metlife.com.br")

            self.select_todos(driver)
            ufs, uf_element = self.get_ufs(driver)

            for uf_index in range(len(ufs)):
                if uf_index + 1 < len(ufs): # avoid out of index
                    uf = ufs[uf_index+2].text
                    print(uf)

                    # TODO: Remove
                    if uf in ['AL', 'AM', 'AP', 'BA']:
                        continue

                    uf_element.select_by_index(uf_index+2)

                    cities, city_element = self.get_cities(driver)
                    now = datetime.now()

                    if len(cities) <= 1:
                        continue

                    for city_index in range(len(cities)):
                        if city_index + 1 < len(cities): # avoid out of index
                            city = cities[city_index+1].text

                            if city in [
                                'ACOPIARA',
                                'AQUIRAZ',
                                'ARACATI',
                                'BOA VIAGEM',
                                'CAMOCIM',
                                'CASCAVEL',
                                'CAUCAIA',
                                'CEDRO',
                                'CRATEÚS',
                                'CRATO',
                                'EUSÉBIO',
                            ]:
                                continue

                            print(uf, " - ", city)
                            city_element.select_by_index(city_index+1)

                            time.sleep(2)
                            search = driver.find_element(By.ID, "btnBuscaAvancada")
                            search.click()

                            try:
                                WebDriverWait(driver, 10).until(
                                    lambda driver: len(driver.find_elements(By.XPATH, "//div[@id='divResultado']/b")) > 1
                                )
                            except TimeoutException as e:
                                city_done = summary_data_repository.find_data(uf, city)
                                if city_done == None:
                                    self.add_summary_data(uf, city, 0)
                                    continue
                                else:
                                    continue

                            except UnexpectedAlertPresentException as e:
                                print('Refreshing page')
                                self.refresh_page(driver, uf_index, city_index)
                                continue

                            except Exception as e:
                                full_traceback = traceback.format_exc()
                                logging.error(f"divResultado error: {full_traceback}")
                                continue


                            result_prev = driver.find_element(By.ID, "divResultado")
                            result_prev = result_prev.text
                            print("result_prev: ", str(result_prev))                        

                            try:
                                count_dentistas = int(result_prev.split(' ')[-2])
                                print("count_dentistas: ", str(count_dentistas))

                                city_done = summary_data_repository.find_data(uf, city)

                                if city_done != None:
                                    city_done = city_done.__dict__
                                    if city_done['count_dentistas'] == count_dentistas:
                                        print('Skipping city...')
                                        continue
                                    else:
                                        print('In database: ', str(city_done['count_dentistas']))

                                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "liButtonMais")))
                                count_pagination = self.get_count_pagination(driver)

                                time.sleep(2)
                                loop_limit = 10
                                count = 0
                                while count_pagination < count_dentistas and\
                                    count_dentistas > page_limit and\
                                    count <= loop_limit\
                                :
                                    try:
                                        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "btnMaisResultados")))
                                        more_items = driver.find_element(By.ID, "btnMaisResultados")
                                        driver.execute_script("arguments[0].click();", more_items)
                                        time.sleep(2)
                                    except TimeoutException as e:
                                        break
                                    except Exception as e:
                                        full_traceback = traceback.format_exc()
                                        logging.error(f"btnMaisResultados error: {full_traceback}")
                                        print({'msg': e})
                                        pass

                                    count_pagination_new = self.get_count_pagination(driver)

                                    if count_pagination_new == count_dentistas:
                                        pass

                                    if count_pagination == count_pagination_new or count_pagination_new == 0:
                                        count_pagination = count_pagination_new
                                        count += 1
                                    else:
                                        count = 0

                                while True:
                                    if len(driver.find_elements(By.CLASS_NAME, "liList")) < count_dentistas:
                                        print('waiting data...')
                                        time.sleep(1)
                                    else:
                                        break

                                    if count == 10: # Not possible to load all from page, save the current data
                                        pass

                                dentistas = driver.find_elements(By.CLASS_NAME, "liList")

                                for dentista in dentistas:
                                    print("dentista.text: ", dentista.text)
                                    dentista_data = dentista.text.split('\n')
                                    print(dentista_data)

                                    # Outliers
                                    if len(dentista_data) < 3:
                                        continue
                                    elif len(dentista_data[1].split(' ')) > 1:
                                        dentista_data.insert(1, '')

                                    cep = dentista_data[3].split(',')[0]
                                    dentista = {
                                        'nome': dentista_data[0],
                                        'cro': re.sub(r'\D', '', dentista_data[3].split(',')[1]),
                                        'uf': uf,
                                        'cpf_cnpj': re.sub(r'\D', '', dentista_data[3].split(',')[2]),
                                        'tipo_estabelecimento': dentista_data[5].split(':')[-1].strip(),
                                        'logradouro': dentista_data[2] + ' ' + cep,
                                        'cidade': city,
                                        'especialidade': dentista_data[1].strip().replace(',',''),
                                        'telefone': re.sub(r'\D', '', dentista_data[4]),
                                        'created_at': now
                                    }

                                    dentista_exist = metlife_repository.find_dentista(dentista['cro'], uf, dentista['especialidade'])

                                    if dentista_exist != None:
                                        dentista_exist = dentista_exist.__dict__
                                        dentista['updated_at'] = now
                                        dentista_model = DentistaModel.model_validate(dentista)

                                        inserted = metlife_repository.update_dentista(
                                            dentista_exist["id"],
                                            dentista_exist["especialidade"],
                                            dentista_model
                                        )
                                    else:
                                        dentista['created_at'] = now
                                        dentista_model = DentistaModel.model_validate(dentista)
                                        inserted = metlife_repository.insert_dentista(dentista_model)

                                self.add_summary_data(uf, city, count_dentistas)

                            except Exception as e:
                                full_traceback = traceback.format_exc()
                                logging.error(f"An error occurred in data collection flow: {full_traceback}")
                                return {'msg': e}
                            

        except WebDriverException as e:
            print(f"An Web Driver Error occurred: {e}")

        finally:
            # Close the browser window
            driver.quit()
            print('finish')

    def get_dentistas_metlife(self):
        return []
    
    def get_count_pagination(self, driver):
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "liButtonMais")))
            pagination = driver.find_element(By.CLASS_NAME, "liButtonMais").text
            time.sleep(1)
            count_pagination = int(pagination.split(' ')[4].strip())
            print('Clicked to get more, count_pagination: ', count_pagination)
            return count_pagination
        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f"liButtonMais error: {full_traceback}")
            # print({'msg': e})
            return 0

    def add_summary_data(self, uf, city, count_dentistas):
        summary_data = SummaryDataModel(**{
            'uf': uf,
            'cidade': city,
            'count_dentistas': count_dentistas,
            'created_at': datetime.now()
        })

        summary_data_model = SummaryDataModel.model_validate(summary_data)
        summary_inserted = summary_data_repository.insert_data(summary_data_model)

    def select_todos(self, driver):
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnBuscaAvancada")))

        plano_element = driver.find_element(By.ID, "optPlano")
        plano_element = Select(plano_element)
        plano_element.select_by_index(1)

        especialidade_element = driver.find_element(By.ID, "optEspecialidade")
        especialidade_element = Select(especialidade_element)
        especialidade_element.select_by_index(1)

    def get_ufs(self, driver):
        uf_element = driver.find_element(By.ID, "optUF")

        WebDriverWait(driver, 10).until(
            lambda driver: len(driver.find_elements(By.XPATH, "//select[@id='optUF']/option")) > 1
        )

        uf_element = Select(uf_element)
        ufs = uf_element.options

        if len(ufs) <= 1:
            return {'message': 'ok'}
        else:
            return ufs, uf_element
        
    def get_cities(self, driver):
        city_element = driver.find_element(By.ID, "optCidades")
        time.sleep(2)

        WebDriverWait(driver, 10).until(
            lambda driver: len(driver.find_elements(By.XPATH, "//select[@id='optCidades']/option")) > 1
        )

        city_element = Select(city_element)
        cities = city_element.options

        return cities, city_element
    
    def refresh_page(self, driver, uf_index, city_index):
        driver.refresh()
        time.sleep(3)
        print('select todos')
        self.select_todos(driver)
        time.sleep(3)

        print('getting ufs')
        ufs, uf_element = self.get_ufs(driver)
        time.sleep(3)

        uf_element.select_by_index(uf_index+2)
        time.sleep(3)

        print('getting cities')
        cities, city_element = self.get_cities(driver)
        time.sleep(3)

        print('selecting city')
        city_element.select_by_index(city_index+1)
        time.sleep(3)
        print('done except')