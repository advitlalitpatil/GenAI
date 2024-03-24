import pandas as pd
import json
pd.set_option('display.max_colwidth', None)
from pandas import json_normalize
data = '''
{
    "name": "John Doe, RN, APRN-BC",
    "education": [
        {
            "duration": "Sept/1986-Augt/1992",
            "summary": "Doctor in Medicine from University of Havana, Havana, Cuba."
        },
        {
            "duration": "August/2005-April/2007",
            "summary": "Registered Nurse, BSN from Florida International University, Nicole Wertheim College of Nursing and Health Sciences, Biscayne Bay Campus, North Miami, Fla. Foreign Educated Physician to Nursing Program."
        },
        {
            "duration": "May/2011 to May/2013",
            "summary": "Neonatal Nurse Practitioner-BC from Stony Brook University, New York, NY. Program Director: Paula Timoney, DNP."
        }
    ],
    "licensure_and_certifications": [
        {
            "duration": "2013",
            "summary": "Board Certified Neonatal Nurse Practitioner by National Certification Corporation. Current & Active."
        },
        {
            "duration": "2013",
            "summary": "Registered Nurse/APRN, State of Florida, Lic # APRN 9265106. Current & Active."
        },
        {
            "duration": "2013",
            "summary": "NCC certified. BLS & NRP Certifications. Current & Active."
        }
    ],
    "professional_experience": [
        {
            "duration": "2013-present",
            "summary": "Advanced Practice Registered Nurse at Kidz Medical Services, Inc. in Coral Gables, FL. Responsibilities include Neonatal Nurse Practitioner in a Medical Neonatology Group serving numerous hospitals in South Florida area, including Level II and III NICUs as well as in Well Baby Nurseries."
        },
        {
            "duration": "2007-2013",
            "summary": "Staff RN/BSN at Palmetto General Hospital; Tenet Healthcare Corp. in Hialeah, FL. Duties included general nursing in a 17-beds Neonatal Intensive Care Unit and attending high-risk deliveries."
        },
        {
            "duration": "2007-2013",
            "summary": "Staff RN/BSN at North Shore Hospital in Miami, FL. Responsibilities included general nursing in a 22-beds Neonatal Intensive Care Unit and attending high-risk deliveries."
        }
    ]
}
'''
# print("Create JSON data:\n", data)
dict = json.loads(data)
name = dict["name"]
df = pd.DataFrame()

for column in ["education", "licensure_and_certifications", "professional_experience"]:
    df2 = pd.json_normalize(dict[f"{column}"])
    df2.rename(columns={'duration': 'duration_' + column , 'summary': 'summary_' + column}, inplace=True)
    df = pd.concat([df, df2], axis=1)
df["name"] = name
# df = df.T

# import os
# output_csv_path = os.path.join(r'D:\Persistent\Y2023\Generative_AI\GenAI_Hackthon\Final\Resume\Genformers_Project\source\data\final_output\temp.csv')
# df.to_csv(output_csv_path, header=True, sep=',')
# # print("After converting JSON data to DataFrame:\n", df)