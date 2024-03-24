import abc
from source.utils.constants import Constants
from azure.ai.formrecognizer import FormRecognizerClient, DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os, re, json
import openai
import pandas as pd
from io import StringIO


class GenFormer(abc.ABC):
    def __init__(self, data_path, endpoint, key, filename):
        # self.service = service
        self.data_path = data_path
        self.user_prompt = None
        # self.operation = operation
        self.file_name = filename
        self.endpoint = endpoint
        self.key = key
        self.form_recognizer = FormRecognizerClient(endpoint, AzureKeyCredential(key))

    def get_input_data(self):
        data_file_path = os.path.join(self.data_path, Constants.INPUT, self.file_name.split(".")[0] + Constants.EXTENSION)
        with open(data_file_path, encoding='utf-8') as f:
            input_txt = f.read()
        return input_txt

    def get_extraction_data(self):
        json_output_path = os.path.join(self.data_path, Constants.JSON_OUTPUT)
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        file_path = os.path.join(self.data_path, Constants.INPUT, self.file_name)
        json_name = self.file_name.split(".")[0] + '.json'
        json_path = os.path.join(json_output_path, json_name)

        file_type = self.file_name.split(".")[1]
        if file_type == 'pdf':
            content_type = 'application/pdf'

        if file_type in ['jpeg', 'png', 'tiff']:
            content_type = f'image/{file_type}'

        if not os.path.isfile(json_path):
            with open(file_path, 'rb') as pdf:
                result = self.form_recognizer.begin_recognize_content(pdf, content_type=content_type, pages=[1,2])
            print('Success: Data extraction from pdf using Azure FR')

            tables = []
            lines = []
            for page in result.result():
                pdict = page.to_dict()
                page_tables = []
                page_num = "page-" + str(page.page_number)
                for line_item in pdict.get('lines'):
                    if not re.match('^[\W_]+$', line_item['text']):
                        lines.append(line_item['text'])
                if page.tables:
                    for table_item in pdict.get('tables'):
                        cells = []
                        table_info = {'page_number': table_item['page_number'],
                                      'rows': table_item['row_count'],
                                      'columns': table_item['column_count'],
                                      'y_position': table_item['bounding_box'][0]['y']}

                        table_info['type'] = 'table'
                        for cell in table_item['cells']:
                            cell_info = {'row': cell['row_index'], 'column': cell['column_index'],
                                         'row_span': cell['row_span'],
                                         'column_span': cell['column_span'], 'header': cell['is_header'],
                                         'page_number': cell['page_number'],
                                         'text': cell['text'], 'y_position': cell['bounding_box'][0]['y']
                                         }
                            cells.append(cell_info)
                        table_info['cells'] = cells
                        page_tables.append(table_info)
                    tables.extend(page_tables)
            data_dict = {'Lines': lines, 'Tables': tables}
            with open(json_path, 'w') as tb:
                tb.write(json.dumps(data_dict))
            print('Success: Processed data stored successfully in json')
        else:
            print('Skipped FR: Duplicated File Uploaded, Using the extracted json')
        with open(json_path) as f:
            content = json.load(f)

        response = openai.ChatCompletion.create(
            engine="genformers_gpt",
            messages=[
                {"role": "system", "content": '''You are an Data Extractor expert./
                 Based upon provided user_prompt,/
                 If Financial Statements are uploaded perform below tasks:
                
                 1 - Extract balance sheet if present from the input data/
                 2 - Extract equity statement if present from the input data and include it in balance sheet/
                 3 - Extract income statement if present from the input data/
                 4 - Extract the cashflow statement if present from the input data,/
                 5 - The headers of the table contains key header with value true and row value 0,/
                 6 - The table contains three columns Line_Item and years found in table header,/
                 7 - Remove Special characters from the year columns./
                 
                 Input: 
                 [{"page_number": 1, "rows": 24, "columns": 3, "y_position": 2.3618, "type": "table", 
                 "cells": [{"row": 0, "column": 0, "row_span": 1, "column_span": 1, "header": true, "page_number": 1, "text": "", "y_position": 2.3562}, {"row": 0, "column": 1, "row_span": 1, "column_span": 1, "header": true, "page_number": 1, "text": "2003", "y_position": 2.351}, {"row": 0, "column": 2, "row_span": 1, "column_span": 1, "header": true, "page_number": 1, "text": "2004", "y_position": 2.351}, {"row": 1, "column": 0, "row_span": 1, "column_span": 1, "header": false, "page_number": 1, "text": "Sales", "y_position": 2.5482}, {"row": 1, "column": 1, "row_span": 1, "column_span": 1, "header": false, "page_number": 1, "text": "", "y_position": 2.5482}, {"row": 1, "column": 2, "row_span": 1, "column_span": 1, "header": false, "page_number": 1, "text": "", "y_position": 2.5482}, {"row": 2, "column": 0, "row_span": 1, "column_span": 1, "header": false, "page_number": 1, "text": "Client Service Revenue\u2026\u2026\u2026\u2026\u2026\u2026\u2026", "y_position": 2.7195}, {"row": 2, "column": 1, "row_span": 1, "column_span": 1, "header": false, "page_number": 1, "text": "S 256,651", "y_position": 2.7143}, {"row": 2, "column": 2, "row_span": 1, "column_span": 1, "header": false, "page_number": 1, "text": "$ 279,156", "y_position": 2.7143}]
                    
                 Output: 
                 Line Item | 2003 | 2004
                 Sales |  | 
                 Client Service Revenue |256,651|279,156
        
                If any other documents are uplaoded, perform below tasks:
                 1 - Identify the document language,/
                 2 - Identify the document type,/
                 3 - Extract all the entities and their values from the form 
                 '''
                 },
                {"role": "user", "content": str(content)}
            ], temperature=0)
        response_data = StringIO(f"{response['choices'][0]['message']['content']}")
        output_df = pd.read_csv(response_data, sep='|')
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        output_df.to_csv(output_csv_path, header=True, index=False)
        return output_df

    def get_bill_exchange(self, input_txt):
        user_prompt = f"""{input_txt}"""
        response = openai.ChatCompletion.create(
            engine="genformers_gpt",
            messages=[
                {"role": "system", "content": '''You are an Invoice Data Extractor expert./
                 Based upon provided user_prompt,/
                 please extract the Borrower Name,Borrower Address,Borrower Pincode,Borrower City, Borrower Country,Seller Name,Seller Address,Seller Pincode,Seller City,Seller Country,Vessel/Aircaft, Date of departure,Date of invoice,Date of issue, Description of Goods
                 if provided text is not in a structured format make it N/A
                 Consider Drawer equal to Borrower 
                 Consider Drawee equal to Seller
                 '''
                 },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0)
        # return response['choices'][0]['message']['content']
        response_data = StringIO(f"{response['choices'][0]['message']['content']}")
        output_df = pd.read_csv(response_data, sep=':')
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        output_df.to_csv(output_csv_path, header=True, index=False)
        return output_df

    def get_commercial_invoice(self, input_txt):
        user_prompt = f"""{input_txt}"""
        response = openai.ChatCompletion.create(
            engine="genformers_gpt",
            messages=[
                {"role": "system", "content": '''You are an Invoice Data Extractor expert./
                 Based upon provided user_prompt,/
                 please extract the Person, Bank Name, Country, Company Name, Vessel/Aircaft,Borrower Name,Borrower Address,Borrower Pincode,Borrower City, Borrower Country,Seller Name,Seller Address,Seller Pincode,Seller City,Seller Country,Date of departure,Date of invoice,Date of issue, Description of Goods
                 '''
                 },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0)
        # return response['choices'][0]['message']['content']
        response_data = StringIO(f"{response['choices'][0]['message']['content']}")
        output_df = pd.read_csv(response_data, sep=':')
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        output_df.to_csv(output_csv_path, header=True, index=False)
        return output_df

    def get_bill_of_lading(self, input_txt):
        user_prompt = f"""{input_txt}"""
        response = openai.ChatCompletion.create(
            engine="genformers_gpt",
            messages=[
                {"role": "system", "content": '''You are an Invoice Data Extractor expert./
                         Based upon provided user_prompt,/
                         please extract the Borrower Name, Borrower Address, Borrower Pincode,Borrower City,
                         Borrower Country,Seller Name,Seller Address, Seller Pincode, Seller City, Seller Country,
                         Date of departure, Date of invoice, Date of issue, Description of Goods
                         '''
                 },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0)
        # return response['choices'][0]['message']['content']
        response_data = StringIO(f"{response['choices'][0]['message']['content']}")
        output_df = pd.read_csv(response_data, sep=':')
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        output_df.to_csv(output_csv_path, header=True, index=False)
        return output_df

    def get_packaging(self, input_txt):
        user_prompt = f"""{input_txt}"""
        response = openai.ChatCompletion.create(
            engine="genformers_gpt",
            messages=[
                {"role": "system", "content": '''You are an Invoice Data Extractor expert./
                 Based upon provided user_prompt,/
                [{'E':'Borrower/Consignee/Drawee Name', 'w':'Bob Jones'},{'E':'Borrower/Consignee/Drawee Address', 'w':'410 Queen Street'},{'E':'Borrower/Consignee/Drawee Pincode', 'w':'4814'},{'E':'Borrower/Consignee/Drawee City', 'w':'Brisbane'},
                {'E':'Borrower/Consignee/Drawee Country', 'w':'Australia'},
                {'E':'Seller/shipper/Drawer Name', 'w':'Randy Clarke'},
                {'E':'Seller/shipper/Drawer Address', 'w':'4300 Longbeach Blvd'},
                {'E':'Seller/shipper/Drawer Pincode', 'w':'90807'},
                {'E':'Seller/shipper/Drawer City', 'w':'California'},
                {'E':'Seller/shipper/Drawer Country', 'w':'United states'},
                {'E':'Vessel name', 'w':'MAERSK'},
                {'E':'Date of departure', 'w':'04 Jul 2022'},
                {'E':'Date of invoice', 'w':'04 Jul 2022'},
                {'E':'Date of issue', 'w':''},
                {'E': 'Description of Goods', 'W':'Bar Stool aluminium, Bar tabe aluminium'}]
                 please extract the Person, Bank Name, Country, Company Name, Vessel/Aircaft,Borrower Name,Borrower Address,Borrower Pincode,Borrower City, Borrower Country,Seller Name,Seller Address,Seller Pincode,Seller City,Seller Country,Date of departure,Date of invoice,Date of issue, Description of Goods
                 '''
                 },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0)
        # return response['choices'][0]['message']['content']
        response_data = StringIO(f"{response['choices'][0]['message']['content']}")
        output_df = pd.read_csv(response_data, sep=':')
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        output_df.to_csv(output_csv_path, header=True, index=False)
        return output_df

    def get_KYC(self, input_txt):
        user_prompt = f"""{input_txt}"""
        response = openai.ChatCompletion.create(
            engine="genformers_gpt",
            messages=[
                {"role": "system", "content": '''You are an Data Extractor expert./
                 Based upon provided user_prompt,/
                 
                 please identify the language and Identify the document type.
                 then extract the important fields with their value 
                 '''
                 },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0)
        response_data = StringIO(f"{response['choices'][0]['message']['content']}")
        output_df = pd.read_csv(response_data, sep=':')
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        output_df.to_csv(output_csv_path, header=True, index=False)
        return output_df

    def get_qa(self, input_txt):
        user_prompt = f"""{input_txt}"""
        response = openai.ChatCompletion.create(
            engine="genformers_gpt",
            messages=[
                {"role": "system", "content": '''You are an Data Extractor expert./
                 Based upon provided user_prompt,/
                 please extract the Issuer Name, Issuer Employer Identification Number (EIN), City, State, Post Office
                 Also, provides answers to following questions as question answer pairs, answers should only be provided from given document.
                 Question 1 : "Describe the organizational action and, if applicable, the date of the action or the date against which shareholders' ownership is measured for
                 the action" 
                 Question 2 : "Describe the quantitative effect of the organizational action on the basis of the security in the hands of a U.S. taxpayer as an adjustment per
                 share or as a percentage of old basis" 
                 Question 3 : "Describe the calculation of the change in basis and the data that supports the calculation, such as the market values of securities and the
                 valuation dates" 
                 '''
                 },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0)
        response_data = StringIO(f"{response['choices'][0]['message']['content']}")
        columns = ['Entity', 'Value']
        output_df = pd.read_csv(response_data, sep=':', header=None, names=columns)
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        output_df.to_csv(output_csv_path, header=True, index=False)
        return output_df

    def get_resume(self, input_txt):
        user_prompt = f"""{input_txt}"""
        response = openai.ChatCompletion.create(
            engine="genformers_gpt",
            messages=[
                {"role": "system", "content": '''You are an Resume Data Extractor expert./
                        Based upon provided user_prompt,/
                        please extract the Name, Total work experience, work experience, skills, certification and education
                        Please keep extracted entities on single line 
                        Don't put multiple extracted entities on multiple line
                        '''
                 },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0)
        # return response['choices'][0]['message']['content']
        response_data = StringIO(f"{response['choices'][0]['message']['content']}")
        columns = ['Entity', 'Value']
        output_df = pd.read_csv(response_data, sep=':', header=None, names=columns)
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        output_df.to_csv(output_csv_path, header=True, index=False, sep=';')
        return output_df

    def get_genai_extraction(self):
        final_output_path = os.path.join(self.data_path, Constants.FINAL_OUTPUT)
        output_csv_path = os.path.join(final_output_path, self.file_name.split(".")[0] + '.csv')
        print(self.file_name.split(".")[0])
        if self.file_name.split(".")[0] == 'resume':
            output_df = pd.read_csv(output_csv_path, sep=';')
        else:
            output_df = pd.read_csv(output_csv_path)
        return output_df

    @abc.abstractmethod
    def run(self):
        pass
