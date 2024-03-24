from source.extraction.genFormer import GenFormer
from source.utils.constants import Constants


class GenFormerExtraction(GenFormer):
    def __init__(self, data_path, endpoint, key, file_name):
        super().__init__(data_path, endpoint, key, file_name)

    def run(self):
        try:
            if self.file_name.split(".")[0] == Constants.BILL_OF_EXCHANGE:
                # input = self.get_input_data()
                output = self.get_genai_extraction()
                return output
            elif self.file_name.split(".")[0] == Constants.INVOICE:
                # input = self.get_input_data()
                output = self.get_genai_extraction()
                return output
            elif self.file_name.split(".")[0] == Constants.BILL_OF_LADING:
                # input = self.get_input_data()
                # output = self.get_bill_of_lading(input)
                # print(output)
                output = self.get_genai_extraction()
                return output
            elif self.file_name.split(".")[0] == Constants.PACKAGING:
                # input = self.get_input_data()
                output = self.get_genai_extraction()
                return output
            elif self.file_name.split(".")[0] in Constants.PDF_DOC_LIST:
                output = self.get_genai_extraction()
                return output
            elif self.file_name.split(".")[0] in Constants.QUESTION_ANSWER:
                # input = self.get_input_data()
                # output = self.get_qa(input)
                output = self.get_genai_extraction()
                return output
            elif self.file_name.split(".")[0] == Constants.RESUME:
                # input = self.get_input_data()
                # output = self.get_resume(input)
                # print(output)
                output = self.get_genai_extraction()
                return output
            else:
                # input = self.get_input_data()
                output = self.get_genai_extraction()
                return output

        except Exception as e:
            print("Exception generated  due to following error -{}".format(e))

