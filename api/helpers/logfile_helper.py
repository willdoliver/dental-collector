from datetime import datetime

class LogfileHelper:
    def get_log_file(operadora):
        formatted_datetime = datetime.now().strftime("%Y_%m_%d")

        if operadora == 'amil':
            return 'log_amil_'+formatted_datetime
        elif operadora == 'metlife':
            return 'log_metlife_'+formatted_datetime
        elif operadora == 'odontoprev':
            return 'log_odontoprev_'+formatted_datetime
        elif operadora == 'unimed':
            return 'log_unimed_'+formatted_datetime
        elif operadora == 'uniodonto':
            return 'log_uniodonto_'+formatted_datetime
