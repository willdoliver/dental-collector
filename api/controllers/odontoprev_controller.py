import time
import traceback, logging
from datetime import datetime
from bs4 import BeautifulSoup
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from api.models.odontoprev_model import DentistaModel
from api.models.odontoprev_summary_data_model import SummaryDataModel
from api.repositories.odontoprev.odontoprev_dentistas_repository import DentistaRepository
from api.repositories.odontoprev.odontoprev_sumary_data_repository import SummaryDataRepository
from api.helpers.logger_message_helper import LoggerMessageHelper
from api.helpers.logfile_helper import LogfileHelper
from dotenv import load_dotenv

chrome_opt = Options()
chrome_opt.add_argument('--headless')
chrome_opt.add_argument('--disable-gpu')
chrome_opt.add_argument('--no-sandbox')

load_dotenv()
odontoprev_repository = DentistaRepository()
summary_data_repository = SummaryDataRepository()

class OdontoprevController():

    def get_dentistas_odontoprev(self):
        return {
            'status': True, 
            'msg': 'In Construction'
        }

    def find_dentistas_from_odontoprev(self):
        log_file = LogfileHelper.get_log_file('odontoprev')
        LoggerMessageHelper.log_message(log_file, 'Started')

        chromedriver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'driver', os.getenv('CHROMEDRIVERFILE'))
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_opt)

        try:
            driver.get('https://www.odontoprev.com.br/redecredenciada/selecaoUf?cdMarca=1&produtoAns=428329320')
            ufs = self.get_ufs(driver)
            print(ufs)
            LoggerMessageHelper.log_message(log_file, ufs)

            for uf in ufs:
                print(uf)
                LoggerMessageHelper.log_message(log_file, uf)

                driver.get(f'https://www.odontoprev.com.br/redecredenciada/selecaoLocal?cdMarca=1&produtoAns=428329320&token=&pesquisaP=false&uf={uf}')
                cities = self.get_cities(driver)

                for city_key, city_name in cities.items():
                    print(uf, ' - ', city_name)
                    LoggerMessageHelper.log_message(log_file, uf + ' - ' + city_name)
                    count_dentistas_city = 0

                    city_done = self.get_city_done(uf, city_name)
                    if city_done is not None:
                        print('Skipping city')
                        LoggerMessageHelper.log_message(log_file, 'Skipping city')
                        continue

                    driver.get(f'https://www.odontoprev.com.br/redecredenciada/buscaRedeCredenciada?cdMarca=1&produtoAns=427893720&uf={uf}&token=&pesquisaP=false&municipio={city_key}&especialidade=0&bairro=0')

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    table_list = soup.find_all('table', {'cellspacing': '0'})

                    for i in range(len(table_list)):
                        item = table_list[i]
                        print(f"Index: {i}, Value: {item}")
                        LoggerMessageHelper.log_message(log_file, f"Index: {i}, Value: {item}")

                        dentista_data = self.format_dentista_data(item)

                        if dentista_data == {}:
                            print('Problem formatting dentista data!')
                            LoggerMessageHelper.log_message(log_file, 'Problem formatting dentista data!')
                            continue
                        else:
                            dentista_data['uf'] = uf
                            dentista_data['cidade'] = city_name
                            count_dentistas_city += 1
                        print(dentista_data)
                        LoggerMessageHelper.log_message(log_file, dentista_data)
                        
                        dentista_exist = odontoprev_repository.find_dentista(
                            dentista_data['cro'],
                            dentista_data['uf'],
                            dentista_data['especialidade']
                        )

                        now = datetime.now()
                        if dentista_exist is not None:
                            dentista_exist = dentista_exist.__dict__
                            dentista_data['updated_at'] = now
                            dentista_model = DentistaModel.model_validate(dentista_data)

                            updated = odontoprev_repository.update_dentista(
                                dentista_exist['id'],
                                dentista_model
                            )
                        else:
                            dentista_data['created_at'] = now
                            dentista_model = DentistaModel.model_validate(dentista_data)
                            inserted = odontoprev_repository.insert_dentista(dentista_model)

                    self.save_city_done(uf, city_name, count_dentistas_city)
                time.sleep(random.randint(3,6))

        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except error: {full_traceback}')

            LoggerMessageHelper.log_message(
                log_file,
                f'except error: {full_traceback}'
            )

        finally:
            print('Finish')
            LoggerMessageHelper.log_message(log_file, 'Finish')

    def get_ufs(self, driver):
        try:
            ufs_options = Select(driver.find_element(By.ID, 'cboUf'))
            ufs = [option.get_attribute('value') for option in ufs_options.options if option.get_attribute('value')]
            return ufs
        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except get_ufs error: {full_traceback}')

            LoggerMessageHelper.log_message(
                LogfileHelper.get_log_file('odontoprev'),
                f'except get_ufs error: {full_traceback}'
            )

    def get_cities(self, driver):
        try:
            cities = {}
            cities_options = Select(driver.find_element(By.ID, 'municipio'))

            for option in cities_options.options:
                if (option.get_attribute('value') == '0'):
                    continue
                cities[option.get_attribute('value')] = option.get_attribute('text')

            return cities
        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except get_cities error: {full_traceback}')

            LoggerMessageHelper.log_message(
                LogfileHelper.get_log_file('odontoprev'),
                f'except get_cities error: {full_traceback}'
            )

    def get_city_done(self, uf, city):
        try:
            return summary_data_repository.find_data(uf, city)
        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except get_city_done error: {full_traceback}')

            LoggerMessageHelper.log_message(
                LogfileHelper.get_log_file('odontoprev'),
                f'except get_city_done error: {full_traceback}'
            )

    def save_city_done(self, uf, city, count_dentistas):
        try:
            now = datetime.now()
            city_done = self.get_city_done(uf, city)

            if city_done is not None:
                city_done = city_done.__dict__
                summary_data_repository.update_data(
                    uf,
                    city,
                    SummaryDataModel.model_validate({
                        'uf': uf,
                        'cidade': city,
                        'count_dentistas': int(city_done['count_dentistas']) + int(count_dentistas),
                        'updated_at': now
                    })
                )
            else:
                summary_data_repository.insert_data(
                    SummaryDataModel.model_validate({
                        'uf': uf,
                        'cidade': city,
                        'count_dentistas': int(count_dentistas),
                        'created_at': now
                    })
                )

        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except save_city_done error: {full_traceback}')

            LoggerMessageHelper.log_message(
                LogfileHelper.get_log_file('odontoprev'),
                f'except save_city_done error: {full_traceback}'
            )

    def format_dentista_data(self, item):
        try:
            cro = item.select_one('.textopreto10:-soup-contains("Nº CRO:")').text
            cro = cro.replace('Nº CRO:', '').strip()
            nome = item.select_one('.textopreto10:-soup-contains("Doutor(a):")').text
            nome = nome.replace('Doutor(a):', '').strip()
            especialidade = item.select_one('.textopreto10:-soup-contains("Especialidade:")').text
            especialidade = especialidade.replace('Especialidade:', '').strip()
            endereco = item.select_one('.textopreto10:-soup-contains("Endereço:")').text
            endereco = endereco.replace('Endereço:', '').strip()
            bairro = item.select_one('.textopreto10:-soup-contains("Bairro:")').text
            bairro = bairro.replace('Bairro:', '').strip()
            telefones = item.select_one('.textopreto10:-soup-contains("Telefones:")').text
            telefones = telefones.replace('Telefones:', '').strip()
            cep = item.select_one('.textopreto10:-soup-contains("CEP:")').text
            cep = cep.replace('CEP:', '').strip()
            tipo_estabelecimento = item.select_one('.textopreto10:-soup-contains("Tipo Estabelecimento:")').text
            tipo_estabelecimento = tipo_estabelecimento.replace('Tipo Estabelecimento:', '').strip()
            nome_fantasia = item.select_one('.textopreto10:-soup-contains("Nome Fantasia:")').text
            nome_fantasia = nome_fantasia.replace('Nome Fantasia:', '').strip()

            return {
                "nome": nome,
                "nome_fantasia": nome_fantasia,
                "cro": cro,
                "especialidade": especialidade,
                "logradouro": endereco + " " + bairro + " "+ cep,
                "telefone": telefones,
                "tipo_estabelecimento": tipo_estabelecimento,
            }

        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except format_dentista_data error: {full_traceback}')

            LoggerMessageHelper.log_message(
                LogfileHelper.get_log_file('odontoprev'),
                f'except format_dentista_data error: {full_traceback}'
            )

            return {}
