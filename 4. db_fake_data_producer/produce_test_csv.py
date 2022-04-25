import csv
import random
import string
import math
from datetime import datetime

import read_table_meta

today = datetime.now().strftime('%Y-%m-%d')

def c_value_producer(c_type, c_length)->str:
    if c_type=='str':
        if c_length>10:
            c_length=10
        return ''.join((random.choice(string.ascii_lowercase) for  _ in range(c_length)))
    if c_type=='number':
        return math.floor(random.random()*10**c_length)
    if c_type=='date':
        return today

def r_value_producer(meta):
    return {column['name']:c_value_producer(column['type'], column['length']) for column in meta }

def csv_producer(file_name, row_num, meta,):
    with open(file_name, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, [column['name'] for column in meta])
        writer.writeheader()
        for _ in range(row_num):
            writer.writerow(r_value_producer(meta))

if __name__=='__main__':
    meta_data = read_table_meta.collector('681_tmp_meta.csv')
    # classify_dict = read_table_meta.classify_nullable(meta_data)
    # meta_data = read_table_meta.get_sample_meta(classify_dict['null'], classify_dict['unull'], 5)
    csv_producer('681.csv', 20000, meta_data)
    