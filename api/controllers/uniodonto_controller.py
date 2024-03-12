import time
import requests, json
import traceback, logging
import random
from datetime import datetime
from bs4 import BeautifulSoup

from api.models.uniodonto_model import DentistaModel
from api.models.uniodonto_summary_data_model import SummaryDataModel
from api.repositories.uniodonto.uniodonto_dentistas_repository import DentistaRepository
from api.repositories.uniodonto.uniodonto_summary_data_repository import SummaryDataRepository
from api.helpers.logger_message_helper import LoggerMessageHelper
from api.helpers.logfile_helper import LogfileHelper
from dotenv import load_dotenv

load_dotenv()
uniodonto_repository = DentistaRepository()
summary_data_repository = SummaryDataRepository()

class UniodontoController():

    def get_dentistas_uniodonto(self):
        return {
            'status': True, 
            'msg': 'In Construction'
        }

    def find_dentistas_from_uniodonto(self):
        log_file = LogfileHelper.get_log_file('uniodonto')
        LoggerMessageHelper.log_message(log_file, 'Started')

        try:
            ufs = self.get_ufs()

            for uf_id, uf in ufs.items():
                uf = self.format_uf(uf)

                cities = self.get_cities(uf_id)
                cities = cities["d"]

                for city in cities:
                    city_id = city["idCidade"]
                    city_name = city["nomeCidade"]
                    print(uf, ' - ', city_name)
                    LoggerMessageHelper.log_message(log_file, uf + ' - ' + city_name)

                    city_done = summary_data_repository.find_data_range_date(uf, city_name)
                    if city_done is None:
                        print('Skipping city...')
                        LoggerMessageHelper.log_message(log_file, 'Skipping city...')
                        continue

                    now = datetime.now()
                    page = 1
                    while True:
                        dentistas_data = self.get_dentistas(uf_id, city_id, page)
                        soup = BeautifulSoup(dentistas_data, 'html.parser')

                        list_group_items = soup.select('.list-group-item.list-group-item-rede')

                        for item in list_group_items:
                            name = item.find('h4', class_='list-group-item-heading').text.strip()
                            cro_cnpj = item.find('p', class_='list-group-item-text').text.strip()
                            tipo_estabelecimento = item.select_one('.panel-default:-soup-contains("Tipo de estabelecimento") .panel-body').text.strip()
                            atuacao = item.select_one('.panel-default:-soup-contains("Atuação") .panel-body').text.strip()
                            detail_data = item.select_one('.panel-default:-soup-contains("Endereço") .table-endereco')

                            if '.' in cro_cnpj:
                                continue
                            else:
                                cro_cnpj = cro_cnpj[10:-2].strip()
                                atuacao = atuacao.replace('(E)', '')
                                rows = []
                                rows.append([td.get_text(strip=True) for td in detail_data.find_all('td')])

                                bairro = None
                                if (rows[0][0]).split(',')[-3] is not None:
                                    bairro = (rows[0][0]).split(',')[-4]

                            dentista = {
                                "nome": name,
                                "cro": cro_cnpj,
                                "tipo_estabelecimento": tipo_estabelecimento,
                                "especialidade": atuacao,
                                "logradouro": rows[0][0],
                                "bairro": bairro,
                                "telefone": rows[0][1],
                                "cidade": city_name,
                                "uf": uf,
                                "created_at": now
                            }
                            print(dentista)
                            LoggerMessageHelper.log_message(log_file, dentista)

                            dentista_exist = uniodonto_repository.find_dentista(dentista['cro'], uf, dentista['especialidade'])

                            if dentista_exist != None:
                                dentista_exist = dentista_exist.__dict__
                                dentista['updated_at'] = now
                                dentista_model = DentistaModel.model_validate(dentista)

                                updated = uniodonto_repository.update_dentista(
                                    dentista_exist["id"],
                                    dentista_model
                                )
                            else:
                                dentista['created_at'] = now
                                dentista_model = DentistaModel.model_validate(dentista)
                                inserted = uniodonto_repository.insert_dentista(dentista_model)

                        city_done = summary_data_repository.find_data(uf, city_name)
                        if (city_done is not None):
                            city_done = city_done.__dict__
                            summary_data = {
                                "uf": uf,
                                "cidade": city_name,
                                "count_dentistas": city_done["count_dentistas"] + len(list_group_items),
                                "updated_at": now,
                            }
                            summary_data_model = SummaryDataModel.model_validate(summary_data)
                            data_updated = summary_data_repository.update_data(uf, city_name, summary_data_model)
                        else:
                            summary_data = {
                                "uf": uf,
                                "cidade": city_name,
                                "count_dentistas": len(list_group_items),
                                "created_at": now
                            }
                            summary_data_model = SummaryDataModel.model_validate(summary_data)
                            data_inserted = summary_data_repository.insert_data(summary_data_model)
                        time.sleep(random.randint(2,4))

                        page += 1
                        if len(list_group_items) == 0:
                            break

        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except error: {full_traceback}')

            LoggerMessageHelper.log_message(log_file, f'except error: {full_traceback}')

        finally:
            print('Finish')
            LoggerMessageHelper.log_message(log_file, 'Finish')

    def __get_headers(self):
        return {
            'User-Agent': 'PostmanRuntime/7.36.3',
            'Accept': '*/*',
            'Content-Type': 'application/json',
        }

    def get_ufs(self):
        return {
            1: "Acre",
            2: "Alagoas",
            4: "Amapá",
            3: "Amazonas",
            5: "Bahia",
            6: "Ceará",
            7: "Distrito Federal",
            8: "Espírito Santo",
            9: "Goiás",
            10: "Maranhão",
            13: "Mato Grosso",
            12: "Mato Grosso do Sul",
            11: "Minas Gerais",
            14: "Pará",
            15: "Paraíba",
            18: "Paraná",
            16: "Pernambuco",
            17: "Piauí",
            19: "Rio de Janeiro",
            20: "Rio Grande do Norte",
            23: "Rio Grande do Sul",
            22: "Rondônia",
            21: "Roraima",
            24: "Santa Catarina",
            26: "São Paulo",
            25: "Sergipe",
            27: "Tocantins"
        }

    def get_cities(self, uf_id):
        try:
            headers = self.__get_headers()
            url = "https://www2.uniodonto.coop.br/Institucional/BuscaDentista.aspx/ComboCidade"
            payload = json.dumps({'Operadora': '', 'idEstado': uf_id})

            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                return json.loads(response.content.decode('utf-8'))
            else:
                return {"errors": "Error when requesting cities"}
        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except get_cities error: {full_traceback}')

            LoggerMessageHelper.log_message(
                LogfileHelper.get_log_file('uniodonto'),
                f'except get_cities error: {full_traceback}'
            )

    def get_dentistas(self, uf_id, city_id, page):
        try:
            url = "https://www2.uniodonto.coop.br/Institucional/BuscaDentista.aspx/ComboCidade"

            payload = {
                'ctl_hidden': str(page),
                'ddlEstado': str(uf_id),
                'ddlCidade': str(city_id),
                'ddlBairro': '0',
                'hdf_estado': str(uf_id),
                'hdf_cidade': str(city_id),
                '__VIEWSTATE': '/wEPDwULLTExMDA4NzYxNDYPFhgeCHRpcG9SZWRlAgEeC3VybEFwaUxvY2FsBURodHRwczovL2FwaS5vZG9udG9zZmVyYS5jb20uYnIvdjMvMzE0MzE1L3JlZGUtYnVzY2FyLWRlbnRpc3RhLWxvY2FsLx4EcmVkZWUeDW5vbWVQcmVzdGFkb3JlHgtjb2RTaW5ndWxhcmQeAnVmZR4Lc2l0ZURvbWluaW8FHmh0dHBzOi8vd3d3Mi51bmlvZG9udG8uY29vcC5ich4GdXJsQXBpBT5odHRwczovL2FwaS5vZG9udG9zZmVyYS5jb20uYnIvdjMvMzE0MzE1L3JlZGUtYnVzY2FyLWRlbnRpc3RhLx4GZXN0YWRvZR4MYmxuUG9zdENvbWJvaB4GY2lkYWRlZR4FcGxhbm9lFgICAw9kFgICBQ9kFgJmD2QWEGYPFgIeBFRleHQFIFByb2Zpc3Npb25haXMgZW0gQWxhZ29hczwvc21hbGw+ZAIBDxAPFgYeDkRhdGFWYWx1ZUZpZWxkBQZjb2RpZ28eDURhdGFUZXh0RmllbGQFCWRlc2NyaWNhbx4LXyFEYXRhQm91bmRnZBAVHAlTZWxlY2lvbmUEQWNyZQdBbGFnb2FzBkFtYXDDoQhBbWF6b25hcwVCYWhpYQZDZWFyw6EQRGlzdHJpdG8gRmVkZXJhbA9Fc3DDrXJpdG8gU2FudG8GR29pw6FzCU1hcmFuaMOjbwtNYXRvIEdyb3NzbxJNYXRvIEdyb3NzbyBkbyBTdWwMTWluYXMgR2VyYWlzBVBhcsOhCFBhcmHDrWJhB1BhcmFuw6EKUGVybmFtYnVjbwZQaWF1w60OUmlvIGRlIEphbmVpcm8TUmlvIEdyYW5kZSBkbyBOb3J0ZRFSaW8gR3JhbmRlIGRvIFN1bAlSb25kw7RuaWEHUm9yYWltYQ5TYW50YSBDYXRhcmluYQpTw6NvIFBhdWxvB1NlcmdpcGUJVG9jYW50aW5zFRwAATEBMgE0ATMBNQE2ATcBOAE5AjEwAjEzAjEyAjExAjE0AjE1AjE4AjE2AjE3AjE5AjIwAjIzAjIyAjIxAjI0AjI2AjI1AjI3FCsDHGdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2cWAQICZAICDxAPFgYfDQUGY29kaWdvHw4FCWRlc2NyaWNhbx8PZ2QQFRIFVG9kYXMJQXJhcGlyYWNhB0F0YWxhaWEMQm9jYSBkYSBNYXRhCENvcnVyaXBlD0RlbG1pcm8gR291dmVpYQdNYWNlacOzEE1hcmVjaGFsIERlb2Rvcm8UTWF0cml6IGRlIENhbWFyYWdpYmUGTXVyaWNpFFBhbG1laXJhIGRvcyDDjW5kaW9zBlBlbmVkbwtQb3J0byBDYWx2bwlSaW8gTGFyZ28SU2FudGFuYSBkbyBJcGFuZW1hFlPDo28gTWlndWVsIGRvcyBDYW1wb3MGU2F0dWJhE1VuacOjbyBkb3MgUGFsbWFyZXMVEgEwAjMxAjMyAjQ3Ajc0Ajc3AzExMgMxMTcDMTIxAzEyNwMxMzgDMTQ2BTI2ODY5AzE2MwMxNjgDMTc1AzE3OQMxOTAUKwMSZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnFgECCWQCAw8QDxYGHw0FDWludF9pZF9iYWlycm8fDgUOc3RyX25vbV9iYWlycm8fD2dkEBUCBVRvZG9zDkNydXogZGFzIEFsbWFzFQIBMAUyNDc3MRQrAwJnZ2RkAgUPEGRkFgFmZAIGDxAPFgYfDQUGY29kaWdvHw4FCWRlc2NyaWNhbx8PZ2QQFRQsQ2lydXJnaWEgZSBUcmF1bWF0b2xvZ2lhIEJ1Y28tTWF4aWxvLUZhY2lhaXMLRGVudMOtc3RpY2EvRGlzZnVuw6fDo28gVMOqbXBvcm8tTWFuZGlidWxhciBlIERvci1Pcm9mYWNpYWwKRW5kb2RvbnRpYQ1Fc3RvbWF0b2xvZ2lhGEhhcm1vbml6YcOnw6NvIE9yb2ZhY2lhbA5JbXBsYW50b2RvbnRpYQ9PZG9udG9nZXJpYXRyaWEXT2RvbnRvbG9naWEgZG8gVHJhYmFsaG8RT2RvbnRvbG9naWEgTGVnYWw1T2RvbnRvbG9naWEgcGFyYSBQYWNpZW50ZXMgY29tIE5lY2Vzc2lkYWRlcyBFc3BlY2lhaXMPT2RvbnRvcGVkaWF0cmlhCk9ydG9kb250aWEhT3J0b3BlZGlhIEZ1bmNpb25hbCBkb3MgTWF4aWxhcmVzD1BhdG9sb2dpYSBCdWNhbAtQZXJpb2RvbnRpYRtQcsOzdGVzZSBCdWNvLU1heGlsby1GYWNpYWwSUHLDs3Rlc2UgRGVudMOhcmlhJ1JhZGlvbG9naWEgT2RvbnRvbMOzZ2ljYSBlIEltYWdpbm9sb2dpYQ9TYcO6ZGUgQ29sZXRpdmEVFAExATIBMwE0ATUCMjABNwIxMQE5ATgCMTACMTICMTMCMTQCMTUCMTYCMTcCMTgBNgIxORQrAxRnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2RkAgoPEA8WBh8NBQZjb2RpZ28fDgUJZGVzY3JpY2FvHw9nZBAVAQVUb2RvcxUBATAUKwMBZ2RkAhIPZBYCAgEPFgIeC18hSXRlbUNvdW50AgEWAgIBD2QWDmYPFQEfSVNBQkVMTEUgSkFOSU5FIFZJRUlSQSBETyBDQVJNT2QCAQ8WAh8MBWQ8aW1nIHNyYz0iL2ltYWdlcy9lc3BlY2lhbGlzdGEuZ2lmIiBhbHQ9IlTDrXR1bG8gZGUgRXNwZWNpYWxpc3RhIiB0aXRsZT0iVMOtdHVsbyBkZSBFc3BlY2lhbGlzdGEiIC8+ZAICDxUCBzAyNTUyQUwVQ2zDrW5pY2EvQ29uc3VsdMOzcmlvZAIDDxYCHxACAhYCAgIPZBYCAgEPFgIfDAUsIERlbnTDrXN0aWNhLCA8c3Ryb25nPk9ydG9kb250aWEoRSk8L3N0cm9uZz5kAgUPFgIfEAIBFgICAQ9kFgRmDxUKFVIuIERSLiBDRVNBUiBTT0JSSU5ITwI1NBUgLSBQUkFDQSBQQURSRSBDSUNFUk8OQ3J1eiBkYXMgQWxtYXMGTXVyaWNpAkFMCTU3ODIwLTAwMA4oODIpIDk5MTc2MzczNgAAZAIBDw8WBB4ISW1hZ2VVcmwFK34vQXBwX1RoZW1lcy9Vb0JyYXNpbC9JbWFnZXMvZ29vZ2xlbWFwcy5wbmceC05hdmlnYXRlVXJsBVFodHRwOi8vbWFwcy5nb29nbGUuY29tLmJyL21hcHM/cT1SLiBEUi4gQ0VTQVIgU09CUklOSE8sIDU0LCBNdXJpY2ksIEFMLCA1NzgyMC0wMDBkZAIGDxUCBTQ2MTg5BTQ2MTg5ZAIHDxYCHxACChYUAgEPZBYCZg8VBCsgQ09MRVRJVk8gRU1QUkVTQVJJQUwgVU5JT0RPTlRPIEVNUFJFU0FSSUFMCTQ2NDYxODExNRRDb2xldGl2byBFbXByZXNhcmlhbAVBdGl2b2QCAg9kFgJmDxUEJFBMQU5PIENPTEVUSVZPIEVNUFJFU0FSSUFMIFVOSU9ET05UTwk0MDg1NjA5OTQUQ29sZXRpdm8gRW1wcmVzYXJpYWwFQXRpdm9kAgMPZBYCZg8VBCRQTEFOTyBDT0xFVElWTyBQT1IgQURFU8ODTyBVTklPRE9OVE8JNDYxMDU1MDk1FENvbGV0aXZvIHBvciBBZGVzw6NvBUF0aXZvZAIED2QWAmYPFQQtUExBTk8gVU5JT0RPTlRPIFBBUkNFUklBIENPTEVUSVZPIEVNUFJFU0FSSUFMCTQxNjIxODk5OBRDb2xldGl2byBFbXByZXNhcmlhbAVBdGl2b2QCBQ9kFgJmDxUELVBMQU5PIFVOSU9ET05UTyBQQVJDRVJJQSBDT0xFVElWTyBQT1IgQURFU8ODTwk0NjI0MzAxMDEUQ29sZXRpdm8gcG9yIEFkZXPDo28FQXRpdm9kAgYPZBYCZg8VBCdQTEFOTyBVTklPRE9OVE8gUEFSQ0VSSUEgUEVTU09BIEbDjVNJQ0EJNzAzNzk3OTkwE0luZGl2aWR1YWwvRmFtaWxpYXIFQXRpdm9kAgcPZBYCZg8VBCVVTklPRE9OVE8gQ09MRVRJVk8gUE9SIEFERVPDg08gTUFTVEVSCTQ2ODIzMTEyORRDb2xldGl2byBwb3IgQWRlc8OjbwVBdGl2b2QCCA9kFgJmDxUECFVOSU9QTEFOCTQzMzI1NjAwMxNJbmRpdmlkdWFsL0ZhbWlsaWFyBUF0aXZvZAIJD2QWAmYPFQQTVU5JT1BMQU4gT1JUT0RPTlRJQQk0NjQ2MTYxMTkTSW5kaXZpZHVhbC9GYW1pbGlhcgVBdGl2b2QCCg9kFgJmDxUEFVVOSU9QTEFOIE9SVE9Ew5ROVElDTwk0NDAwODAwMjETSW5kaXZpZHVhbC9GYW1pbGlhcgVBdGl2b2QYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgQFEGx0YkVzcGVjaWFsaWRhZGUFDWNoa0VtZXJnZW5jaWEFDGNoa18yNF9ob3JhcwUIbHRiUGxhbm92oj7+pOnAudtBwK2//ZYFihFDKaMYgIa9GrrGaARpZw==',
                '__VIEWSTATEGENERATOR': '6B9C8298'
            }

            headers = {
                'Cookie': 'ASP.NET_SessionId=vox2zg32gbamwnzbgrsohoky'
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            # with open("output_page_response.html", "w", encoding="utf-8") as file:
            #     file.write(response.text)

            if response.status_code == 200:
                return response.text
            else:
                return []
        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except get_cities error: {full_traceback}')

            LoggerMessageHelper.log_message(
                LogfileHelper.get_log_file('uniodonto'),
                f'except get_cities error: {full_traceback}'
            )

    def format_uf(self, uf_name):
        ufs = {
            "AC": "Acre",
            "AL": "Alagoas",
            "AP": "Amapá",
            "AM": "Amazonas",
            "BA": "Bahia",
            "CE": "Ceará",
            "DF": "Distrito Federal",
            "ES": "Espírito Santo",
            "GO": "Goiás",
            "MA": "Maranhão",
            "MT": "Mato Grosso",
            "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais",
            "PA": "Pará",
            "PB": "Paraíba",
            "PR": "Paraná",
            "PE": "Pernambuco",
            "PI": "Piauí",
            "RJ": "Rio de Janeiro",
            "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul",
            "RO": "Rondônia",
            "RR": "Roraima",
            "SC": "Santa Catarina",
            "SP": "São Paulo",
            "SE": "Sergipe",
            "TO": "Tocantins"
        }

        for uf_sigla, uf in ufs.items():
            if uf_name == uf:
                return uf_sigla
