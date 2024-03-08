import os
import re
import time
import traceback, logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import WebDriverException, TimeoutException, UnexpectedAlertPresentException
from api.models.metlife_model import DentistaModel
from api.models.metlife_summary_data_model import SummaryDataModel
from api.repositories.metlife.metlife_dentistas_repository import DentistaRepository
from api.repositories.metlife.metlife_summary_data_repository import SummaryDataRepository
from api.helpers.logger_message_helper import LoggerMessageHelper
from api.helpers.logfile_helper import LogfileHelper
from dotenv import load_dotenv

from selenium.webdriver.chrome.options import Options
chrome_opt = Options()

chrome_opt.add_argument('--headless')
chrome_opt.add_argument('--disable-gpu')
chrome_opt.add_argument('--no-sandbox')
chrome_opt.add_argument('--window-size=1920,1080')

load_dotenv()
metlife_repository = DentistaRepository()
summary_data_repository = SummaryDataRepository()

class MetLifeController():

    def find_dentistas_from_metlife(self):
        log_file = LogfileHelper.get_log_file('metlife')
        LoggerMessageHelper.log_message(log_file, 'Started')
        
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
                    try:
                        uf = ufs[uf_index+1].text
                    except:
                        print('stale in state')
                        LoggerMessageHelper.log_message(log_file, 'stale in state')
                        ufs, uf_element = self.get_ufs(driver)
                        uf = ufs[uf_index+1].text

                    print(uf)
                    LoggerMessageHelper.log_message(log_file, uf)

                    # TODO: Remove
                    # if uf in ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'TO']:
                    #     continue

                    uf_element.select_by_index(uf_index+1)

                    cities, city_element = self.get_cities(driver)
                    now = datetime.now()

                    if len(cities) <= 1:
                        continue

                    for city_index in range(len(cities)):
                        if city_index + 1 < len(cities): # avoid out of index
                            try:
                                city = cities[city_index+1].text
                            except:
                                print('stale in city')
                                LoggerMessageHelper.log_message(log_file, 'stale in city')
                                cities, city_element = self.get_cities(driver)
                                city = cities[city_index+1].text

                            print(uf + " - " + city)
                            LoggerMessageHelper.log_message(log_file, uf + " - " + city)
                            city_element.select_by_index(city_index+1)

                            time.sleep(2)
                            try:
                                search = driver.find_element(By.ID, "btnBuscaAvancada")
                                search.click()
                            except Exception as e:
                                print('Refreshing page 1')
                                LoggerMessageHelper.log_message(log_file, 'Refreshing page 1')
                                self.refresh_page(driver, uf_index, city_index)

                            try:
                                WebDriverWait(driver, 10).until(
                                    lambda driver: len(driver.find_elements(By.XPATH, "//div[@id='divResultado']/b")) > 1
                                )
                            except TimeoutException as e:
                                print('Aborting city because TimeoutException')
                                LoggerMessageHelper.log_message(log_file, 'Aborting city because TimeoutException')
                                self.add_summary_data(uf, city)
                                continue

                            except UnexpectedAlertPresentException as e:
                                print('Aborting city because UnexpectedAlertPresentException')
                                LoggerMessageHelper.log_message(log_file, 'Aborting city because UnexpectedAlertPresentException')
                                self.add_summary_data(uf, city)
                                continue

                            except Exception as e:
                                full_traceback = traceback.format_exc()
                                logging.error(f"divResultado error: {full_traceback}")
                                LoggerMessageHelper.log_message(log_file, f"divResultado error: {full_traceback}")
                                continue

                            result_prev = driver.find_element(By.ID, "divResultado")
                            result_prev = result_prev.text
                            print('result_prev: ', str(result_prev))
                            LoggerMessageHelper.log_message(log_file, f'result_prev: {result_prev}')

                            try:
                                count_dentistas = int(result_prev.split(' ')[-2])
                                print("count_dentistas: ", str(count_dentistas))
                                LoggerMessageHelper.log_message(log_file, f'count_dentistas: {count_dentistas}')

                                city_done = summary_data_repository.find_data_range_date(uf, city)
                                if city_done is None:
                                    print('Skipping city...')
                                    LoggerMessageHelper.log_message(log_file, 'Skipping city')
                                    continue

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
                                        LoggerMessageHelper.log_message(log_file, f'msg:  {e}')
                                        pass

                                    count_pagination_old = count_pagination
                                    count_pagination = self.get_count_pagination(driver)
                                    print(f'Debug {count_pagination_old} - {count_pagination} - {count}')
                                    LoggerMessageHelper.log_message(log_file, f'Debug {count_pagination_old} - {count_pagination} - {count}')

                                    if count_pagination == count_dentistas:
                                        pass

                                    if count_pagination == count_pagination_old or count_pagination == 0:
                                        count += 1

                                while True:
                                    if len(driver.find_elements(By.CLASS_NAME, "liList")) < count_dentistas:
                                        print('waiting data...')
                                        LoggerMessageHelper.log_message(log_file, 'waiting data...')
                                        time.sleep(1)

                                    if count == 10: # Not possible to load all from page, save the current data
                                        pass
                                    else:
                                        break

                                dentistas = driver.find_elements(By.CLASS_NAME, "liList")

                                for dentista in dentistas:
                                    # print("dentista.text: ", dentista.text)
                                    dentista_data = dentista.text.split('\n')
                                    print(dentista_data)
                                    LoggerMessageHelper.log_message(log_file, f'dentista_data: {dentista_data}')

                                    # Outliers
                                    if len(dentista_data) < 3:
                                        continue
                                    # specialist case and not specialist with empty specialist field
                                    elif dentista_data[1] == '' and len(dentista_data) >= 7:
                                        dentista_data.pop(1)

                                    cep = dentista_data[3].split(',')[0]
                                    try:
                                        dentista = {
                                            'nome': dentista_data[0],
                                            'cro': re.sub(r'\D', '', dentista_data[3].split(',')[1]),
                                            'uf': uf,
                                            'cpf_cnpj': re.sub(r'\D', '', dentista_data[3].split(',')[2]),
                                            'tipo_estabelecimento': dentista_data[5].split(':')[-1].strip(),
                                            'logradouro': dentista_data[2] + ' ' + cep,
                                            'cidade': city,
                                            'especialidade': dentista_data[1].strip().replace(',',''),
                                            'telefone': re.sub(r'Telefone: ', '', dentista_data[4]),
                                            'created_at': now
                                        }
                                    except Exception as e:
                                        LoggerMessageHelper.log_message(log_file, 'error parsing dentista_data')
                                        continue

                                    print(dentista)
                                    LoggerMessageHelper.log_message(log_file, f'dentista: {dentista}')

                                    dentista_exist = metlife_repository.find_dentista(dentista['cro'], uf, dentista['especialidade'])

                                    if dentista_exist != None:
                                        dentista_exist = dentista_exist.__dict__
                                        dentista['updated_at'] = now
                                        dentista_model = DentistaModel.model_validate(dentista)

                                        inserted = metlife_repository.update_dentista(
                                            dentista_exist['id'],
                                            dentista_exist['especialidade'],
                                            dentista_model
                                        )
                                    else:
                                        dentista['created_at'] = now
                                        dentista_model = DentistaModel.model_validate(dentista)
                                        inserted = metlife_repository.insert_dentista(dentista_model)

                                self.add_summary_data(uf, city, count_dentistas)

                            except Exception as e:
                                full_traceback = traceback.format_exc()
                                logging.error(f'An error occurred in data collection flow: {full_traceback}')
                                LoggerMessageHelper.log_message(log_file, f'msg: {e}')
                                return {'msg': e}

        except WebDriverException as e:
            print(f'An Web Driver Error occurred: {e}')
            LoggerMessageHelper.log_message(log_file, f'An Web Driver Error occurred: {e}')

        finally:
            # Close the browser window
            driver.quit()
            print('finish')
            LoggerMessageHelper.log_message(log_file, 'Finish')

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
            print({'msg': e})
            return 0

    def add_summary_data(self, uf, city, count_dentistas = 0):
        city_done = summary_data_repository.find_data(uf, city)

        if city_done is not None:
            summary_data = SummaryDataModel(**{
                'uf': uf,
                'cidade': city,
                'count_dentistas': count_dentistas,
                'updated_at': datetime.now()
            })
            summary_data_model = SummaryDataModel.model_validate(summary_data)
            summary_updated = summary_data_repository.update_data(uf, city, summary_data_model)

        else:
            summary_data = SummaryDataModel(**{
                'uf': uf,
                'cidade': city,
                'count_dentistas': count_dentistas,
                'created_at': datetime.now()
            })
            summary_data_model = SummaryDataModel.model_validate(summary_data)
            summary_inserted = summary_data_repository.insert_data(summary_data_model)

    def select_todos(self, driver):
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

        uf_element.select_by_index(uf_index+1)
        time.sleep(3)

        print('getting cities')
        cities, city_element = self.get_cities(driver)
        time.sleep(3)

        print('selecting city')
        city_element.select_by_index(city_index+1)
        time.sleep(3)

        print('click to search again')
        search = driver.find_element(By.ID, "btnBuscaAvancada")
        search.click()
        time.sleep(3)
        print('refresh done')