import os
import requests, json, time, random
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api.models.unimed_model import Dentista, DentistaUpdate, URLCrawled
from api.repositories.unimed_repository import UnimedRepository

load_dotenv()
unimed_repository = UnimedRepository()

class UnimedController():

    def get_dentistas_from_unimed_odonto(self):

        planos_unimed = [
            804, 453, 374,
            789, 788, 738, 743, 791, 790, 785, 742, 100, 805, 741,
        #     825, 826, 827, 828,
        #     730, 731, 732, 322, 323, 324,
        #     459643099, 78, 459649098, 75, 459637094, 459640094, 459631095, 111, 459633091, 348, 344, 343, 342, 11, 8, 70, 5, 114, 102, 119, 43, 2, 133, 112, 41, 117, 120, 61, 52, 17, 77, 14, 79, 46, 80, 66, 55, 81, 29, 124, 110, 26, 49, 74, 58, 82, 408,
        #     459645095, 459648090, 459642091, 19, 31, 459636096, 459639091, 98, 459632093, 338, 333, 334, 821, 455, 461, 786, 728, 727, 823, 396, 393, 399, 395, 400, 392, 398, 397, 401, 394, 10, 7, 132, 4, 125, 113, 129, 39, 1, 459630097, 40, 83, 60, 51, 67, 16, 96, 13, 131, 45, 84, 99, 54, 28, 121, 25, 128, 116, 48, 85, 57, 101, 63, 411, 410, 409, 403, 109, 105, 421, 420, 419, 418, 417, 415, 416, 402, 108, 106, 407, 107, 405,
        #     733,
        #     384, 385, 386, 387, 735, 739, 792, 364, 366, 456, 459,
        #     819, 820, 822,
        #     37, 38,
        #     459652098, 459650091, 459644097, 459647091, 36, 86, 459638092, 459641092, 91, 459635098, 459634090, 724, 460, 454, 358, 354, 355, 357, 457, 351, 353, 12, 9, 69, 352, 6, 115, 76, 97, 103, 73, 65, 44, 126, 3, 42, 62, 53, 21, 24, 18, 68, 15, 127, 87, 47, 118, 88, 89, 56, 122, 90, 33, 30, 72, 27, 130, 92, 50, 123, 93, 64, 94, 59, 95,
        #     388, 389, 390, 391, 368, 370,
        #     734, 740, 729, 380, 382, 807,
        #     782, 781, 783, 793, 780,
        ]

        points = [
            (-25.530635, -48.529835)
        ]

        try:
            urls_crawled = []
            try:
                urls_from_repository = unimed_repository.get_urls_crawled()
                urls_models = [URLCrawled(**{**document, '_id': str(document['_id'])}) for document in urls_from_repository]
                urls_crawled = [model.url for model in urls_models]
            except:
                pass

            for plano in planos_unimed:
                url = []
                url.append(os.getenv('URL_UNIMED'))
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
                        data = self.__get_data(url_search)
                        error = data['errors']

                        if error:
                            print(error)
                            return {'msg': error}

                        content = data['data']
                        dentistas = content['list']

                        for dentista in dentistas:
                            dentista_model = Dentista(**dentista)
                            dentista_exist = unimed_repository.find_dentista(dentista_model.cro, dentista_model.uf_cro)

                            if dentista_exist != None and '_id' in dentista_exist:
                                inserted = unimed_repository.update_dentista(
                                    dentista_exist["_id"],
                                    dentista_model.model_dump(exclude={'id'})
                                )
                            else:
                                inserted = unimed_repository.insert_dentista(dentista_model.model_dump(exclude={'id'}))

                        url_model = URLCrawled(**{'url': url_search})
                        inserted = unimed_repository.save_url_crawled(url_model.model_dump(exclude={'id'}))

                        if inserted:
                            urls_crawled.append(url_search)

                        time.sleep(random.randint(3, 9))

                        if page >= int(content['quantidadePaginas']):
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
