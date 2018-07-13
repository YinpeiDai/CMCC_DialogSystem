"""
20180613清华中移动客服对话系统语料
预处理脚本，整理为对话数据
"""
import xlrd, pprint, json
file1 = '20180613清华中移动客服对话系统语料采集（第一次收集）\【结果】中移动客服对话系统语料采集-10.xlsx'
file2 = '20180613清华中移动客服对话系统语料采集（第一次收集）\【结果】中移动客服对话系统语料采集-30.xlsx'
file3 = '20180613清华中移动客服对话系统语料采集（第一次收集）\【结果】中移动客服对话系统语料采集-50.xlsx'

taskfile = '20180613清华中移动客服对话系统语料采集（第一次收集）\众包任务设计.xlsx'

AllData = {}
col_dict = {"对话场景总体描述":1, "业务领域":2, "用户动作":3, "业务实体":4,
            "对话状态":5, "问询槽":6, "上轮系统动作":7, "对话历史":9,
            "用户回复示例1":10, "用户回复示例2":11, "用户回复示例3":12,  }

with xlrd.open_workbook(taskfile) as f:
    table = f.sheet_by_index(0)
    nrows = table.nrows
    for row in range(1, nrows):
        idx = table.cell(row,0).value
        AllData[idx] = {}


        tmp = table.cell_value(row, col_dict["对话历史"])
        if tmp != "":
            AllData[idx]["对话历史"] = tmp.split('\n')

        tmp = table.cell_value(row, col_dict["上轮系统动作"])
        if tmp != "":
            AllData[idx]["上轮系统动作"] = tmp.replace("request", "问询")

        tmp = table.cell_value(row, col_dict["业务实体"])
        if tmp != "":
            AllData[idx]["业务实体"] = tmp.split('，')

        tmp = table.cell_value(row, col_dict["问询槽"])
        if tmp != "":
            AllData[idx]["问询槽"] = tmp.split('，')

        for s in ["对话场景总体描述", "对话状态", "用户动作", "业务领域"]:
            tmp = table.cell_value(row, col_dict[s])
            if tmp != "":
                AllData[idx][s] = tmp

        AllData[idx]["用户回复示例"] = []
        for s in ["用户回复示例1", "用户回复示例2", "用户回复示例3"]:
            tmp = table.cell_value(row, col_dict[s])
            if tmp != "":
                AllData[idx]["用户回复示例"].append(tmp)


with xlrd.open_workbook(file1) as f:
    table = f.sheet_by_name('中移动客服对话系统语料采集-10--阿里众包处理结果详情下载')
    nrows = table.nrows
    for row in range(1, nrows):
        idx = table.cell(row, 1).value
        AllData[idx]["用户回复示例"].append(table.cell(row, 2).value)

with xlrd.open_workbook(file2) as f:
    table = f.sheet_by_name('中移动客服对话系统语料采集-30--阿里众包处理结果详情下载')
    nrows = table.nrows
    for row in range(1, nrows):
        idx = table.cell(row, 1).value
        AllData[idx]["用户回复示例"].append(table.cell(row, 2).value)

with xlrd.open_workbook(file3) as f:
    table = f.sheet_by_name('中移动客服对话系统语--50--阿里众包处理结果详情下载')
    nrows = table.nrows
    for row in range(1, nrows):
        idx = table.cell(row, 1).value
        AllData[idx]["用户回复示例"].append(table.cell(row, 3).value)

for k, item in AllData.items():
    item["收集个数"] = len(item["用户回复示例"])

with open('../tmp/DialogData20180613.json', 'w', encoding='utf-8') as f:
    json.dump(AllData, f, indent=2, ensure_ascii=False)










