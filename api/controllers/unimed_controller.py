import os
import requests, json, time, random
from dotenv import load_dotenv
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api.models.unimed_model import DentistaModel, URLCrawledModel
from api.repositories.unimed.dentista_repository import DentistaRepository, DentistaOrm
from api.repositories.unimed.urls_crawled_repository import URLsCrawledRepository, URLsCrawledOrm

load_dotenv()
urls_crawled_repository = URLsCrawledRepository()
dentista_repository = DentistaRepository()

class UnimedController():

    def get_dentistas_from_unimed_odonto(self):

        planos_unimed = [
            # 804, 453, 374,
            # 789, 788, 738, 743, 791, 790, 785, 742, 100, 805, 741,
            # 825, 826, 827, 828,
            # 730, 731, 732, 322, 323, 324,
            # 459643099, 78, 459649098, 75, 459637094, 459640094, 459631095, 111, 459633091, 348, 344, 343, 342, 11, 8, 70, 5, 114, 102, 119, 43, 2, 133, 112, 41, 117, 120, 61, 52, 17, 77, 14, 79, 46, 80, 66, 55, 81, 29, 124, 110, 26, 49, 74, 58, 82, 408,
            # 459645095,
            # 459648090, 459642091, 19, 31, 459636096, 459639091, 98, 459632093, 338, 333, 334, 821, 455, 461, 786, 728, 727, 823, 396, 393, 399, 395, 400, 392, 398, 397, 401, 394, 10, 7, 132, 4, 125, 113, 129, 39, 1, 459630097, 40, 83, 60, 51, 67, 16, 96, 13, 131, 45, 84, 99, 54, 28, 121, 25, 128, 116, 48, 85, 57, 101, 63, 411, 410, 409, 403, 109, 105, 421, 420, 419, 418, 417, 415, 416, 402, 108, 106, 407, 107, 405,
            733,
            # 384, 385, 386, 387, 735, 739, 792, 364, 366, 456, 459,
            # 819, 820, 822,
            # 37, 38,
            # 459652098, 459650091, 459644097, 459647091, 36, 86, 459638092, 459641092, 91, 459635098, 459634090, 724, 460, 454, 358, 354, 355, 357, 457, 351, 353, 12, 9, 69, 352, 6, 115, 76, 97, 103, 73, 65, 44, 126, 3, 42, 62, 53, 21, 24, 18, 68, 15, 127, 87, 47, 118, 88, 89, 56, 122, 90, 33, 30, 72, 27, 130, 92, 50, 123, 93, 64, 94, 59, 95,
            # 388, 389, 390, 391, 368, 370,
            # 734, 740, 729, 380, 382, 807,
            # 782, 781, 783, 793, 780,
        ]

        points = [
            (-25.530635, -48.529835)
        ]

        try:
            urls_crawled = []
            try:
                urls_from_repository = urls_crawled_repository.get_urls()
                urls_crawled = [model.url for model in urls_from_repository]
            except Exception as e:
                exit(e)

            for plano in planos_unimed:
                url = []
                url.append(os.getenv('URL_MONGO_UNIMED'))
                url.append('isRedeCredenciada=true')
                url.append('quantidaderegistrosPagina=100')
                url.append('codigoAreaAtuacao=0')
                url.append('raioKm=100')
                url.append('paginarResultado=true')
                url.append('codigoPlano='+str(plano))

                for point in points:
                    page = 1
                    url_point = '&'.join(url)
                    url_point += '&latitude='+str(point[0])
                    url_point += '&longitude='+str(point[1])

                    while True:
                        url_search = url_point + '&numeroPagina='+str(page)

                        if url_search in urls_crawled:
                            print("Skipping: " + url_search)
                            page += 1
                            continue

                        print("Searching: " + url_search)
                        data = self.__get_data('local')
                        error = data['errors']

                        if error:
                            print(error)
                            return {'msg': error}

                        content = data['data']
                        dentistas = content['list']
                        now = datetime.now()

                        for dentista in dentistas:
                            address = dentista['locaisAtendimento'][0]['endereco']

                            if address is not None:
                                dentista['logradouro'] = address['logradouro']
                                dentista['bairro'] = address['bairro']
                                dentista['cidade'] = address['cidade']
                                dentista['uf'] = address['uf']
                                dentista['latitude'] = address['latitude']
                                dentista['longitude'] = address['longitude']

                            phones = dentista['locaisAtendimento'][0]['telefone']
                            if phones is not None:
                                dentista['telefone'] = '|'.join([f"({phone['ddd']}){phone['numero']}" for phone in phones])

                            areas = dentista['locaisAtendimento'][0]['areasAtuacao']
                            if areas is not None:
                                dentista['areas_atuacao'] = '|'.join([f"{area['descricaoAreaAtuacao']}" for area in areas])

                            email = dentista['locaisAtendimento'][0]['email']
                            if email is not None:
                                dentista['email'] = email

                            dentista['created_at'] = now
                            dentista['data_atualizacao'] = dentista['dataAtualizacao']

                            dentista.pop('locaisAtendimento')
                            dentista.pop('dataAtualizacao')

                            dentista_model = DentistaModel.model_validate(dentista)
                            dentista_exist = dentista_repository.find_dentista(dentista_model.cro, dentista_model.cro_uf)

                            dentista_exist = dentista_exist.__dict__
                            if dentista_exist != None and 'id' in dentista_exist:
                                inserted = dentista_repository.update_dentista(
                                    dentista_exist["id"],
                                    dentista_model
                                )
                            else:
                                inserted = dentista_repository.insert_dentista(dentista)

                        if 'quantidadePaginas' in content\
                            and content['quantidadePaginas'] is not None\
                            and page >= int(content['quantidadePaginas']):
                            url_model = URLCrawledModel(**{
                                'url': url_search,
                                'plano': plano,
                                'latitude': str(point[0]),
                                'longitude': str(point[1]),
                                'numero_pagina': page,
                                'created_at': now
                            })
                            print(url_model)
                            inserted = urls_crawled_repository.save_url_crawled(url_model)

                            if inserted:
                                urls_crawled.append(url_search)

                            time.sleep(random.randint(9, 30))
                            break
                        elif 'quantidadePaginas' in content and content['quantidadePaginas'] is None:
                            break
                        else:
                            page += 1
                            continue
            return {'msg': 'ok'}
        except Exception as e:
            return {'msg': str(e)}

    def get_dentistas_unimed(self):
        content = {}
        try:
            dentistas = unimed_repository.find_dentistas()

            dentista_model = [Dentista(**{**dentista, '_id': str(dentista['_id'])}) for dentista in dentistas]

            content['status'] = True
            content['count'] = len(dentista_model)
            content['data'] = dentista_model
        except Exception as e:
            content['status'] = False
            content['msg'] = str(e)
            print(e)

        return content

    def get_dentista_unimed(self, cro_num, cro_uf):
        content = {}
        try:
            dentistas = unimed_repository.find_dentista(cro_num, cro_uf)

            dentista_model = [Dentista(**{**dentista, '_id': str(dentista['_id'])}) for dentista in dentistas]

            content['status'] = True
            content['count'] = len(dentista_model)
            content['data'] = dentista_model
        except Exception as e:
            content['status'] = False
            content['msg'] = str(e)
            print(e)

        return content

    def __get_data(self, origin):
        if origin == 'local':
            with open('api/examples/unimed_example.json', 'r', encoding='utf-8') as json_file:
                return json.load(json_file)
        else:
            data = requests.get(origin)
            if data.status_code == 200:
                return json.loads(data.content.decode('utf-8'))
            else:
                return {"errors": "Error when requesting page"}

    def update_unimed_urls(self):
        try:
            documents = unimed_repository.get_urls()

            elements_updated = 0
            for document in documents:
                document_id = document['_id']

                url = document['url'].split('&')
                plano = url[6].split('=')[-1]
                latitude = url[7].split('=')[-1]
                longitude = url[8].split('=')[-1]
                numeroPagina = url[9].split('=')[-1]

                data_to_update =  {
                    'plano': plano,
                    'latitude': latitude,
                    'longitude': longitude,
                    'pagina': int(numeroPagina),
                }
                print(data_to_update)

                result = unimed_repository.update_url(document_id, data_to_update)

                print('Update result: '+ str(result.modified_count))
                elements_updated += 1

            return str(elements_updated) +' documents updated successfully', 200
        except Exception as e:
            print(str(e))
            return 'Internal Server Error', 500
