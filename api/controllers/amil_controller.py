import os
import re
import time
import random
import requests, json
import traceback, logging
from datetime import datetime
from api.models.amil_model import DentistaModel
from api.models.amil_summary_data_model import SummaryDataModel
from api.repositories.amil.amil_dentistas_repository import DentistaRepository
from api.repositories.amil.amil_summary_data_repository import SummaryDataRepository
from api.helpers.logger_message_helper import LoggerMessageHelper
from api.helpers.logfile_helper import LogfileHelper
from dotenv import load_dotenv

load_dotenv()
amil_repository = DentistaRepository()
summary_data_repository = SummaryDataRepository()

class AmilController():

    def get_dentistas_amil(self):
        return {
            'status': True, 
            'msg': 'In Construction'
        }

    def find_dentistas_from_amil(self):
        log_file = LogfileHelper.get_log_file('amil')
        LoggerMessageHelper.log_message(log_file, 'Started')

        try:
            ufs = self.get_ufs()
            for uf in ufs:
                uf = uf['Uf']
                print(uf)
                LoggerMessageHelper.log_message(log_file, uf)

                cities = self.get_cities(uf)
                print(cities)
                LoggerMessageHelper.log_message(log_file, cities)
                for city in cities:
                    city = city["Municipio"]
                    print(uf + " - " + city)
                    LoggerMessageHelper.log_message(log_file, uf + " - " + city)

                    city_done = summary_data_repository.find_data_range_date(uf, city)
                    if (city_done is None):
                        print("Skipping city...")
                        LoggerMessageHelper.log_message(log_file, "Skipping city...")
                        continue

                    especialidades = self.get_especialidades(uf, city, "TODOS OS BAIRROS")
                    print(especialidades)
                    LoggerMessageHelper.log_message(log_file, especialidades)

                    if len(especialidades) == 0:
                        continue

                    for especialidade in especialidades:
                        especialidade = especialidade['NIVEL2_ELEMENTODIVULGACAO']
                        print(especialidade)
                        LoggerMessageHelper.log_message(log_file, f'especialidade: {especialidade}')

                        dentistas_data = self.get_dentistas(uf, city, especialidade)
                        if (len(dentistas_data) == 0):
                            continue

                        now = datetime.now()
                        for dent in dentistas_data:
                            print(dent)
                            LoggerMessageHelper.log_message(log_file, f'dent: {dent}')
                            address = str(dent["enderecoRedeCredenciada"][0]["logradouro"])\
                                + ", " + str(dent["enderecoRedeCredenciada"][0]["numero"])\
                                + ", " + str(dent["enderecoRedeCredenciada"][0]["cep"])

                            bairro = None
                            if dent["enderecoRedeCredenciada"][0]["bairroRedeCredenciada"] is not None:
                                bairro = str(dent["enderecoRedeCredenciada"][0]["bairroRedeCredenciada"])

                            telefone = None
                            if dent["enderecoRedeCredenciada"][0]["telefones"] is not None:
                                telefone = dent["enderecoRedeCredenciada"][0]["telefones"].replace(';',',')[:-1]

                            dentista = {
                                'nome_dentista': dent["nomePrestador"],
                                'nome_fantasia': dent["nomeFantasia"],
                                'cro': dent["registroConselhoProfissional"],
                                'uf': uf,
                                'email': dent["email"],
                                'cpf_cnpj': str(dent["documento"]),
                                'tipo_estabelecimento': dent["tipoPessoa"],
                                'logradouro': address,
                                'bairro': bairro,
                                'cidade': city,
                                'especialidade': especialidade,
                                'telefone': telefone,
                            }
                            print(dentista)
                            LoggerMessageHelper.log_message(log_file, f'dentista: {dentista}')

                            dentista_exist = amil_repository.find_dentista(dentista['cro'], uf, dentista['especialidade'])

                            if dentista_exist != None:
                                dentista_exist = dentista_exist.__dict__
                                dentista['updated_at'] = now
                                dentista_model = DentistaModel.model_validate(dentista)

                                updated = amil_repository.update_dentista(
                                    dentista_exist["id"],
                                    dentista_exist["especialidade"],
                                    dentista_model
                                )
                            else:
                                dentista['created_at'] = now
                                dentista_model = DentistaModel.model_validate(dentista)
                                inserted = amil_repository.insert_dentista(dentista_model)

                        city_done = summary_data_repository.find_data(uf, city)
                        if (city_done is not None):
                            city_done = city_done.__dict__
                            summary_data = {
                                "uf": uf,
                                "cidade": city,
                                "count_dentistas": city_done["count_dentistas"] + len(dentistas_data),
                                "updated_at": now,
                            }
                            summary_data_model = SummaryDataModel.model_validate(summary_data)
                            data_updated = summary_data_repository.update_data(uf, city, summary_data_model)
                        else:
                            summary_data = {
                                "uf": uf,
                                "cidade": city,
                                "count_dentistas": len(dentistas_data),
                                "created_at": now,
                            }
                            summary_data_model = SummaryDataModel.model_validate(summary_data)
                            data_inserted = summary_data_repository.insert_data(summary_data_model)
                        time.sleep(random.randint(2,4))

        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f"except error: {full_traceback}")
            LoggerMessageHelper.log_message(log_file, full_traceback)

        finally:
            print('finish')
            LoggerMessageHelper.log_message(log_file, "Finish")

    def __get_headers(self):
        return {
            'User-Agent': 'PostmanRuntime/7.36.3',
            'Accept': '*/*',
            'Content-Type': 'application/json'
        }

    def get_ufs(self):
        headers = self.__get_headers()
        url = "https://www.amil.com.br/institucional/api/InstitucionalMiddleware/RedeCredenciadaEstado/801/DENTAL"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return {"errors": "Error when requesting ufs"}
        
    def get_cities(self, uf):
        headers = self.__get_headers()
        url = "https://www.amil.com.br/institucional/api/InstitucionalMiddleware/RedeCredenciadaMunicipio/801/DENTAL/" + uf

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return {"errors": "Error when requesting cities"}

    def get_especialidades(self, uf, city, bairro):
        headers = self.__get_headers()
        url = "https://www.amil.com.br/institucional/api/InstitucionalMiddleware/RedeCredenciadaEspecialidade/801/DENTAL/"\
            + uf + "/"\
            + city.replace(" ", "%20") + "/"\
            + bairro.replace(" ", "%20") + "/DENTAL"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return [{"errors": "Error when requesting especialidades"}]
        
    def get_dentistas(self, uf, city, especialidade):
        headers = self.__get_headers()
        url = "https://www.amil.com.br/institucional/api/InstitucionalMiddleware/RedeCredenciadaCredenciado"
        payload = json.dumps({
            "contexto": "DENTAL",
            "modalidade": "DENTAL",
            "operadora": "DENTAL",
            "tipoServico": "DENTAL",
            "codigoRede": 801,
            "uf": uf,
            "municipio": city,
            "bairro": "TODOS OS BAIRROS",
            "especialidade": especialidade
        })

        response = requests.post(url, headers=headers, data=payload)
        try:
            if response.status_code == 200:
                return json.loads(response.content.decode('utf-8'))
            else:
                return []
        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f"except error: {full_traceback}")

            LoggerMessageHelper.log_message(LogfileHelper.get_log_file('amil'), full_traceback)
            return []
