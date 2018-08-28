"""
结合所有的 Manager,实现text-in text-out的交互式 agent 的接口
"""
import os
import sys
import time
import argparse
import logging
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, '../..'))
os.environ["CUDA_VISIBLE_DEVICES"]="1"

from DM.DST.StateTracking import DialogStateTracker
from DM.policy.RuleMapping import RulePolicy
from data.DataManager import DataManager
from NLU.NLUManager import NLUManager
from NLG.NLGManager import rule_based_NLG

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--print', type=bool, default=True, help='print details')
FLAGS= parser.parse_args()

UserPersonal =  {
            "已购业务": ["180元档幸福流量年包", "18元4G飞享套餐升级版"], # 这里应该是完整的业务的信息dict
            "套餐使用情况": "剩余流量 11.10 GB，剩余通话 0 分钟，话费余额 110.20 元，本月已产生话费 247.29 元",
            "号码": "18811369685",
            "归属地" : "北京",
            "品牌": "动感地带",
            "是否转品牌过渡期": "否",
            "话费查询": "话费余额 110.20 元",
            "流量查询": "剩余流量 11.10 GB",
            "订购时间": "订购时间 2017-04-04， 生效时间 2017-05-01",
            "是否停机": "否",
            "话费充值": "请登录网上营业厅、微厅或 APP 充值",
            "流量充值": "请登录网上营业厅、微厅或 APP 充值",
            "账单查询": "请登录网上营业厅、微厅或 APP 查询"
        }

NLU_save_path_dict = {
    'domain': os.path.join(BASE_DIR, 'NLU/DomDect/model/ckpt'),
    'useract': os.path.join(BASE_DIR, 'NLU/UserAct/model/ckpt'),
    'slotfilling': os.path.join(BASE_DIR, 'NLU/SlotFilling/model/ckpt'),
    'entity': os.path.join(BASE_DIR, 'NLU/ER/entity_list.txt'),
    'sentiment': os.path.join(BASE_DIR, 'NLU/SentiDect')
}

class DialogAgent:
    def __init__(self):
        self.history_savedir = None
        self.detail_savedir = None
        self.logger = None
        self.user = self.create_user()
        self.rule_policy = RulePolicy()
        self.dst = DialogStateTracker(UserPersonal, FLAGS.print, self.logger)
        self.data_manager = DataManager(os.path.join(BASE_DIR, 'data/tmp'))
        self.nlu_manager = NLUManager(NLU_save_path_dict)
        # self.nlg_template = NLG_template
        self.turn_num = 1
        self.dialog_history = []

    def create_user(self):
        user_name = input("请输入您的用户名：")
        user_path = os.path.join(BASE_DIR, 'user', user_name)
        log_path = os.path.join(user_path, 'log')
        if not os.path.exists(user_path):
            os.mkdir(user_path)
            os.mkdir(log_path)
        self.history_savedir = user_path + '/dialogs.txt'
        log_name = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        self.detail_savedir = log_path +'/' + log_name + '.log'
        self.logger = self.create_logger(self.detail_savedir)
        return user_name

    def create_logger(self, logdir):
        fmt = '%(message)s'
        # datefmt = "%y-%m-%d %H:%M:%S"
        logging.basicConfig(level=logging.INFO,
                                          format=fmt)
                                          # datefmt=datefmt)
        logger = logging.getLogger('mylogger')
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(logdir)
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)
        return logger

    def run(self):
        if FLAGS.print:
            self.logger.info('对话记录时间：'+time.strftime("%Y-%m-%d %H:%M:%S",
                                     time.localtime()))
        try:
            while True:
                user_utter = input("用户输入：")
                if FLAGS.print:
                    with open(self.detail_savedir, 'a') as f:
                        f.write('-------------- Turn ' + str(self.turn_num) + '--------------\n')
                        f.write('用户：' + user_utter + '\n')
                self.dialog_history.append('用户：' + user_utter)
                if user_utter in ['restart' , '重来' , '重新开始']:
                    self.dst = DialogStateTracker(UserPersonal, FLAGS.print, self.logger)
                    self.rule_policy = RulePolicy()
                    if FLAGS.print:
                        self.logger.info('对话状态已重置')
                    else:
                        print('对话状态已重置')
                    continue
                if '再见' in user_utter or '结束' in user_utter or '谢谢' in user_utter:
                    self.close()
                    break
                nlu_results = self.nlu_manager.get_NLU_results(user_utter,  self.data_manager)
                self.dst.update(nlu_results, self.rule_policy, self.data_manager)
                reply  = rule_based_NLG(self.dst)
                if FLAGS.print:
                    self.logger.info('系统:' + reply + '\n')
                else:
                    print('系统:', reply, '\n')
                self.dialog_history.append('系统：' + reply)
                self.turn_num += 1

        except KeyboardInterrupt:
            self.close()

    def close(self):
        self.nlu_manager.close()
        reply = '感谢您的使用，再见！'
        if FLAGS.print:
            self.logger.info('系统:' + reply + '\n')
        else:
            print('系统:', reply, '\n')
        with open(os.path.join(BASE_DIR, self.history_savedir), 'a') as f:
            f.write('对话记录时间：')
            f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n\n')
            for dialog in self.dialog_history:
                dialog = '\n'.join(dialog.split())
                f.write(dialog+'\n\n')
            f.write('系统：感谢您的使用，再见！\n')
            f.write('————————————————————————————————\n')

if __name__ == '__main__':
    agent = DialogAgent()
    agent.run()

















