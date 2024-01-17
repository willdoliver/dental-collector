import os
import requests, json
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api.models.unimedModel import Dentista, DentistaUpdate

load_dotenv()

def get_dentistas_from_unimed_odonto():

    # planos_unimed = [
    #     804, 453, 374,
    #     789, 788, 738, 743, 791, 790, 785, 742, 100, 805, 741,
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
    # ]

    planos_unimed = [804, 453]

    points = [
        (-25.530635, -48.529835),
        (-96.530635, -78.529835)
    ]

    urls_crawled = []

    try:
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
                url_search = '&'.join(url)
                url_search += '&latitude='+str(point[0])
                url_search += '&longitude='+str(point[1])
                url_search += '&numeroPagina='+str(page)

                while True:
                    url_search = url_search[:-1]+str(page)
                    print(url_search)

                    if url_search in urls_crawled:
                        page += 1
                        continue

                    data = get_data('local') # url_search
                    error = data['errors']
                    content = data['data']

                    if error:
                        print(error)
                        exit                        

                    dentistas = content['list']
                
                    for dentista in dentistas:
                        # print(json.dumps(dentista, indent=3))
                        teste = Dentista(**dentista)
                        print(teste)
                        break

                    urls_crawled.append(url_search)

                    if page == 3: # content['quantidadePaginas']
                        break
                    else:
                        page += 1
                        continue
    except Exception as e:
        print(e)


def get_data(origin):
    if origin == 'local':
        with open('api/examples/unimed_example.json', 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    else:
        data = requests.get(origin)
        if data.status_code == 200:
            return json.loads(data.content.decode('utf-8'))