import json

user_acts = [
    '问询', '告知', '要求更多', '要求更少', '更换', '问询费用选项', '问询通话时长选项',
    '问询流量选项', '同时办理', '比较', '闲聊'
]
user_act_task_ids = {
    '问询':[], '告知':[], '要求更多':[], '要求更少':[], '更换':[], '问询费用选项':[], '问询通话时长选项':[],
    '问询流量选项':[], '同时办理':[], '比较':[], '闲聊':[]
}
with open('../../../data/tmp/DialogData20180613.json',  'r', encoding="utf-8") as fr:
    task_dict = json.load(fr)
    for task_id in task_dict.keys():
        task_user_act =  task_dict[task_id]["用户动作"]
        if task_user_act in user_acts:
            user_act_task_ids[task_user_act].append(task_id)
        else:
            print(task_id, task_user_act)


with open('user_act_intro.txt', 'w', encoding = 'utf-8') as fw:
    for user_act in user_act_task_ids.keys():
        print(user_act+", count:" +str(len(user_act_task_ids[user_act])))
        fw.write(user_act+", count:" +str(len(user_act_task_ids[user_act]))+'\n')

    fw.write('\n')
    for user_act in user_act_task_ids.keys():
        print(user_act+", " +str(user_act_task_ids[user_act]))
        fw.write("'"+user_act+"'"+": " +str(user_act_task_ids[user_act])+'\n')

print(user_act_task_ids)