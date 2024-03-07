from datetime import datetime

class LogfileHelper:
    def get_log_file(operadora):
        formatted_datetime = datetime.now().strftime("%Y_%m_%d")

        if operadora == 'amil':
            return 'logs/log_amil_'+formatted_datetime
        elif operadora == 'metlife':
            return 'logs/log_metlife_'+formatted_datetime
        elif operadora == 'odontoprev':
            return 'logs/log_odontoprev_'+formatted_datetime
        elif operadora == 'unimed':
            return 'logs/log_unimed_'+formatted_datetime
        elif operadora == 'uniodonto':
            return 'logs/log_uniodonto_'+formatted_datetime
