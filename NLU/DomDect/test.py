import json
domains = ["套餐", "流量", "WLAN", "号卡", "国际港澳台", "家庭多终端", "个人"]
domain_task_ids = {
    '个人': [],
    '套餐': [],
    '流量': [],
    'WLAN': [],
    '号卡': [],
    '家庭多终端': [],
    '国际港澳台': [],
}
with open('../../data/tmp/DialogData20180613.json',  'r', encoding="utf-8") as f:
        task_dict = json.load(f)
        for task_id in task_dict.keys():
            task_domain =  task_dict[task_id]["业务领域"]
            if task_domain in domains:
                domain_task_ids[task_domain].append(task_id)
            else:
                print(task_id, task_domain)

for domain in domain_task_ids.keys():
    print(domain+", count:" +str(len(domain_task_ids[domain])))

print(domain_task_ids)