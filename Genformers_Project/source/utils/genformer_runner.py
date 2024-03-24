import os, sys
import openai
from source.utils.constants import Constants
from source.extraction.genFormerExtraction import GenFormerExtraction
import configparser


def genformer_runner(filename):
    os.environ[Constants.APP_HOME] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    config_file_path = os.path.join(os.environ[Constants.APP_HOME], Constants.CONFIG_FILE)
    config = configparser.ConfigParser()
    config.read(config_file_path)
    openai.api_type = config.get(Constants.CREDENTIALS, Constants.API_TYPE)
    openai.api_base = config.get(Constants.CREDENTIALS, Constants.API_BASE)
    openai.api_version = config.get(Constants.CREDENTIALS, Constants.API_VERSION)
    openai.api_key = config.get(Constants.CREDENTIALS, Constants.API_KEY)
    data_path = os.path.join(os.environ[Constants.APP_HOME], Constants.DATA)
    endpoint = config.get(Constants.CREDENTIALS, Constants.ENDPOINT)
    key = config.get(Constants.CREDENTIALS, Constants.KEY)
    ouptut = run_genformer(data_path=data_path, endpoint=endpoint, key=key,
                      filename=filename)
    return ouptut


def run_genformer(data_path, endpoint, key, filename):
    cls_obj = GenFormerExtraction(data_path, endpoint, key, filename)
    output = cls_obj.run()
    # print(output)
    return output


# if __name__ == '__main__':
#     genformer_runner()
