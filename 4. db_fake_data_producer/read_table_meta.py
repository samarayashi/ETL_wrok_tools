import csv
import random


def collector(meta_csv: str) -> list:
    meta_collector = []
    with open(meta_csv, 'r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            column_name = row['COLUMN_NAME']
            data_type = row['DATA_TYPE']
            data_length = int(row['DATA_LENGTH'])
            nullable = row['NULLABLE'] == 'Y' and True
            data_precision = int(row['DATA_PRECISION'] or 0)
            data_scale = int(row['DATA_SCALE'] or 0)

            ramdom_length :int
            if  'CHAR' in data_type:
                data_type = 'str'
                ramdom_length = data_length
            elif  'DATE' in data_type:
                data_type = 'date'
                ramdom_length = data_length
            elif  'NUMBER' in data_type:
                data_type = 'number'
                ramdom_length = data_precision-data_scale

            meta_collector.append({'table': row['TABLE_NAME'],
            'name': column_name,
            'type': data_type, 
            'length': ramdom_length,
            'nullable': nullable})
        return meta_collector

def classify_nullable(meta_collector):
    null_list=[]
    unull_list=[]
    for column in meta_collector:
        if column['nullable']:
            null_list.append(column)
        else:
            unull_list.append(column)
    return {'null': null_list,
    'unull': unull_list}

def get_sample_meta(null_meta_list, unull_meta_list, sample_column_num):
    return random.sample(null_meta_list, sample_column_num)+unull_meta_list
