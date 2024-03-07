import os
import traceback, logging
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from api.models.uniodonto_model import DentistaModel as uniodontoDentistaModel
from api.repositories.amil.amil_dentistas_repository import DentistaRepository as AmilRepository
from api.repositories.metlife.metlife_dentistas_repository import DentistaRepository as MetlifeRepository
from api.repositories.odontoprev.odontoprev_dentistas_repository import DentistaRepository as OdontoprevRepository
from api.repositories.unimed.unimed_dentista_repository import DentistaRepository as UnimedRepository
from api.repositories.uniodonto.uniodonto_dentistas_repository import DentistaRepository as UniodontoRepository

from api.helpers.logger_message_helper import LoggerMessageHelper
from dotenv import load_dotenv

load_dotenv()
amil_repository = AmilRepository()
metlife_repository = MetlifeRepository()
odontoprev_repository = OdontoprevRepository()
unimed_repository = UnimedRepository()
uniodonto_repository = UniodontoRepository()

class ETLController():

    def create_tables(self):
        return {
            'status': True, 
            'msg': 'In Construction'
        }

    def sync_data(self):
        log_file = 'logs/log_etl_' + datetime.now().strftime("%Y_%m_%d")
        LoggerMessageHelper.log_message(log_file, 'Sync Data Started')

        try:
            sources = {
                'crawler_dentistas_amil' : {
                    'repository': amil_repository,
                },
                'crawler_dentistas_metlife' : {
                    'repository': metlife_repository,
                },
                'crawler_dentistas_odontoprev' : {
                    'repository': odontoprev_repository,
                },
                'crawler_dentistas_unimed' : {
                    'repository': unimed_repository,
                },
                'crawler_dentistas_uniodonto' : {
                    'repository': uniodonto_repository,
                }
            }

            for table, repository in sources.items():
                LoggerMessageHelper.log_message(log_file, f'Starting table {table}')

                all_dentistas = repository['repository'].find_dentistas()
                df_dentistas = self.transform(all_dentistas, table)
                self.load(df_dentistas, table)
                LoggerMessageHelper.log_message(log_file, f'Data inserted on table {table}')

        except Exception as e:
            full_traceback = traceback.format_exc()
            logging.error(f'except error: {full_traceback}')

            LoggerMessageHelper.log_message(log_file, f'except error: {full_traceback}')

        finally:
            print('Finish')
            LoggerMessageHelper.log_message(log_file, 'Finish')
            return {
                'status': True,
                'msg': 'Finish'
            }

    def transform(self, all_dentistas: list, table_name: str) -> pd.DataFrame:
        dentistas_list = [person.__dict__ for person in all_dentistas]
        df = pd.DataFrame.from_records(dentistas_list, exclude=['_sa_instance_state'])

        if 'unimed' in table_name:
            df['areas_atuacao'] = df['areas_atuacao'].str.replace('|', ',')
        return df

    def load(self, df: pd.DataFrame, table_name: str) -> None:
        # DATABASE_URL = os.getenv("URI_MYSQL_DENTAL")
        DATABASE_URL = os.getenv("URI_MYSQL_LIFE")
        engine = create_engine(DATABASE_URL)

        df.to_sql(
            name=table_name,
            con=engine,
            index=False,
            if_exists='replace'
        )
