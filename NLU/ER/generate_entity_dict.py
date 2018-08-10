import sys
sys.path.append('../..')
import xlrd, re, sqlite3,copy, pprint

entity_list = []

data = xlrd.open_workbook('../../data/DataBase/NewOntology.xlsx')
tables = ['套餐业务','流量业务', 'WLAN业务','号卡业务', '家庭及多终端', '国际港澳台']

for table_name in tables:
    table = data.sheet_by_name(table_name)  # 通过名称获取
    ziyewu = table.col_values(0)[1:]
    ziyewu = list(filter(lambda t: t != "", ziyewu))
    zhuyewu = table.col_values(1)[1:]
    zhuyewu = list(filter(lambda t: t != "", zhuyewu))
    for yewu in ziyewu:
        if yewu not in entity_list:
            entity_list.append(yewu)
    for yewu in zhuyewu:
        if yewu not in entity_list:
            entity_list.append(yewu)

with open('entity_list.txt', 'w', encoding='utf-8') as f:
    for entity in entity_list:
        f.write(entity+'\n')


