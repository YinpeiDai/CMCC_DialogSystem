"""
自动抽取本体的脚本
"""
# 领域
domains = ["套餐", "流量", "WLAN", "号卡", "国际港澳台", "家庭多终端", "个人"]

# user act
USER_ACT = ["告知", "问询", "比较", "要求更多", "要求更少", "更换", "同时办理", "问询费用选项", "问询通话时长选项", "问询流量选项", "闲聊"]

# 个人业务
Personal_name_entity = {"名称": ["180元档幸福流量年包", "18元4G飞享套餐升级版", "流量安心包",
                               "139邮箱免费版", "飞信", "满意100服务资讯"]}
Personal_informable_slots = []
Personal_requestable_slots = [
    "已购业务", "订购时间", "套餐使用情况", "号码", "归属地", "品牌", "是否转品牌过渡期", "是否停机",
    "账单查询", "话费充值", "流量充值", "话费查询", "流量查询"
]

main_bussiness_dict = ['畅享套餐', '畅享不限量套餐','88商旅套餐', '4G飞享套餐升级版', '4G短信包',
                            '短信包套餐', '和4G套餐', '动感地带可选套餐', '神州行可选套餐', '全球通专属数据包',
                            '4G数据终端资费套餐', '畅游包', ' 数据流量加油包', '夜间流量套餐', '数据流量实体卡',
                            '流量小时包', '流量日包', '流量季包', '流量半年包', '幸福流量年包', '4G上网卡',
                            '任我用流量套餐', '月末流量安心包', '流量月末包', '移动数据流量不限流量叠加包',
                            '流量安心套餐', '假日流量包', '7天手机视频流量包', '手机视频流量包', '地铁流量包',
                            '任我看视频流量包', 'WLAN标准套餐', 'WLAN流量套餐', 'WLAN校园套餐',
                            '和家庭分享', '家庭计划', '多终端分享', '和校园', '亲情通',
                            '国际/港澳台漫游', '多国/大包多天流量包', '港澳台三地畅游包', '数据流量包',
                            '2018俄罗斯世界杯特惠包', '“海外随心看”日套餐']

# 具有一定普适性的问询槽
# GLOBAL_slots = {
#     "超出处理_国内主叫": "超出套餐的通话时长 0.19元/分钟，不收取漫游费",
#     "超出处理_国内流量": "套餐内流量用尽后，超出资费将按每10元100MB计费，不足10元部分按0.29元/MB收取，以此类推；直至超出流量费用达到60元时，不再收取费用，此时您可以继续使用流量直至1GB。再次超出后，按同样规则以此类推，直至流量双封顶（套餐外流量消费最高500元或15GB）",
#     "结转规则_国内主叫":"套餐内语音资源当月有效，未用完部分不累计到下月。",
#     "结转规则_国内流量":"当月未消费的剩余流量（不含促销赠送的套外流量及定向视频流量），可以结转至次月使用，结转流量次月月底失效。同一类型的流量 优先扣减上月结转的剩余流量，再扣减套餐内流量。不同类型的流量，按照原有的扣费顺序扣减，计费规则不变。若办理了套餐变更（含档位变更、变更回原套餐）、手机处于停机销号则流量无法结转",
#     "结转规则_赠送流量": "赠送的套外流量，套餐内所有流量用尽后方可使用，且不结转，可分享",
#     "是否全国接听免费": "是",
#     "是否包含港澳台地区": "不包含",
#     "流量分享方式":"登录移动APP客户端后，选择办理，点击\"流量共享\"，按提示操作即可",
#     "流量转赠方式":" 登录移动官方APP，点击“剩余流量”界面的“流量转赠”，按提示操作即可",
#     "停机销号管理":"若您整月处于停机状态（含申停、欠停），不收取当月功能费或移动数据流量套餐费，已购服务有效期不延期，剩余流量无法结转，不支持退换费用。" ,
#     "封顶规则":"默认套餐遵循500元、15G双封顶限制",
#     "受理时间":"一般每月最后一天19点后无法办理",
#     "开通客户限制": "一般仅限北京移动全球通、动感地带、神州行升级版标准卡、畅听卡、家园卡、5元卡开通",
#     "开通生效规则":"默认新入网客户或未开通主套餐的客户当月开通，当月生效。当月的月功能费及免费资源按天折算。已办理其他套餐的客户，申请开通套餐时，直接开通新套餐即可，无需对原套餐进行取消，当月办理下月生效。",
#     "取消变更生效规则":"当月变更/取消，下月生效"
# }


# 套餐业务
TaoCan_name_entity = {'短信包套餐': ['短信包10元套餐', '短信包20元套餐', '短信包30元套餐', '短信包40元套餐', '短信包50元套餐'],
                      '88商旅套餐': ['58元档88商旅套餐', '88元档88商旅套餐', '128元档88商旅套餐', '158元档88商旅套餐', '188元档88商旅套餐', '288元档88商旅套餐', '388元档88商旅套餐', '588元档88商旅套餐', '888元档88商旅套餐'],
                      '畅享不限量套餐': ['98元畅享不限量套餐', '188元畅享不限量套餐', '198元畅享不限量套餐', '288元畅享不限量套餐'],
                      '和4G套餐': ['38档和4G套餐', '58档和4G套餐', '88档和4G套餐', '108档和4G套餐', '128档和4G套餐', '158档和4G套餐', '188档和4G套餐', '288档和4G套餐', '388档和4G套餐', '588档和4G套餐', '888档和4G套餐'],
                      '4G短信包': ['10元4G短信包', '20元4G短信包', '30元4G短信包'],
                      '神州行可选套餐': ['5元短信套餐', '10元短信套餐', '15元短信套餐', '20元短信套餐'],
                      '全球通专属数据包': ['全球通短信包', '全球通尊享包', '全球通音乐包', '全球通阅读包', '全球通凤凰资讯包'],
                      '畅享套餐': ['58元畅享套餐', '88元畅享套餐', '108元畅享套餐', '138元畅享套餐', '158元畅享套餐', '188元畅享套餐', '288元畅享套餐', '388元畅享套餐', '588元畅享套餐'],
                      '4G彩信包': ['10元4G彩信包', '20元4G彩信包', '30元4G彩信包'],
                      '动感地带可选套餐': ['3元彩信包', '5元彩信包', '全球呼', '短信120', '短信500'],
                      '4G飞享套餐升级版': ['18元档4G飞享套餐升级版', '28元档4G飞享套餐升级版', '38元档4G飞享套餐升级版', '48元档4G飞享套餐升级版', '58元档4G飞享套餐升级版', '88元档4G飞享套餐升级版', '138元档4G飞享套餐升级版', '158元档4G飞享套餐升级版', '238元档4G飞享套餐升级版', '268元档4G飞享套餐升级版', '338元档4G飞享套餐升级版', '588元档4G飞享套餐升级版'],
                      '神州行家园卡套餐': ['欢乐套餐']}
TaoCan_informable_slots = [
    "功能费",
    "套餐内容_国内主叫",
    "套餐内容_国内流量",
] # 支持数值型value (如 88元，三百兆)和 描述性 value (如：贵一点，流量多的)
TaoCan_requestable_slots = TaoCan_informable_slots + [
    "产品介绍", "计费方式", "适用品牌",
    "套餐内容_国内短信", "套餐内容_国内彩信", "套餐内容_WLAN流量", "套餐内容_其他功能", "套餐内容",
    "超出处理_国内主叫", "超出处理_国内短信", "超出处理_国内彩信", "超出处理_国内流量", "超出处理",
    "结转规则_国内主叫", "结转规则_国内短信", "结转规则_国内流量", "结转规则_赠送流量", "结转规则",
    "是否全国接听免费", "是否包含港澳台地区", "能否结转滚存", "能否分享", "能否转赠",
    "流量分享方式", "流量转赠方式", "转户转品牌管理", "停机销号管理", "赠送优惠活动",
    "使用限制", "使用有效期", "使用方式设置", "封顶规则", "限速说明",
    "受理时间", "互斥业务", "开通客户限制", "累次叠加规则", "开通方式", "开通生效规则",
    "是否到期自动取消", "能否变更或取消","取消方式", "取消变更生效规则", "变更方式"
]
TaoCan_DB_slots = ["子业务" , "主业务"] + TaoCan_requestable_slots
TaoCan_Recommend_entity = "畅享套餐" # 万金油业务，万一找不到合适套餐就推荐

# 流量业务
LiuLiang_name_entity = {'地铁流量包': ['20元地铁流量包', '30元地铁流量包', '50元地铁流量包'],
                        '流量月末包': ['9元流量月末包', '20元流量月末包'],
                        '流量小时包': ['6元流量小时包', '9元流量小时包'],
                        '移动数据流量不限流量叠加包': ['移动数据流量不限流量叠加包'],
                        '流量年包': ['1200元流量年包'],
                        '夜间流量套餐': ['夜间流量包'],
                        '任我用流量套餐': ['任我用流量包 '],
                        '流量季包': ['30元流量季包', '60元流量季包', '90元流量季包'],
                        '月末流量安心包': ['月末流量安心包'],
                        '4G上网卡': ['特惠年包卡', '上网卡年包卡'],
                        '畅游包': ['30元畅游包', '50元畅游包', '70元畅游包', '100元畅游包', '150元畅游包', '200元畅游包', '300元畅游包'],
                        '假日流量包': ['元旦包', '春节包', '清明包', '五一包', '端午包', '中秋包', '国庆包'],
                        '手机视频流量包': ['乐视版手机视频流量包', '百视通手机视频流量包', '芒果TV手机视频流量包', '搜狐视频手机视频流量包', '爱奇艺视频手机视频流量包', 'PPTV视频手机视频流量包', '暴风影音视频手机视频流量包', '手机电影视频手机视频流量包'],
                        '流量日包': ['10元流量日包', '15元流量日包'],
                        '4G数据终端资费套餐': ['40元档4G数据终端资费套餐', '50元档4G数据终端资费套餐', '70元档4G数据终端资费套餐', '100元档4G数据终端资费套餐', '130元档4G数据终端资费套餐', '180元档4G数据终端资费套餐', '280元档4G数据终端资费套餐'],
                        '幸福流量年包': ['180元档幸福流量年包', '360元档幸福流量年包'],
                        '任我看视频流量包': ['9元档任我看视频流量包', '24元档任我看视频流量包'],
                        '流量安心套餐': ['流量安心包'],
                        '7天手机视频流量包': ['7天乐视会员特惠流量包', '7天百视通会员特惠流量包', '7天芒果TV会员特惠流量包', '7天手机电影会员特惠流量包', '7天爱奇艺会员特惠流量包', '7天腾讯会员特惠流量包', '7天PP视频会员特惠流量包', '7天暴风影音会员特惠流量包', '7天QQ音乐会员特惠流量包'],
                        '数据流量加油包': ['5元加油包', '8元加油包', '10元加油包', '15元加油包', '30元加油包', '40元加油包', '500元加油包'],
                        '数据流量实体卡': ['数据流量实体月卡', '30元数据流量实体季卡', '60元数据流量实体季卡', '90元数据流量实体季卡'],
                        '流量半年包': ['60元流量半年包', '120元流量半年包', '180元流量半年包', '600元流量半年包']}
LiuLiang_informable_slots = [
    "功能费",
    "套餐内容_国内流量"
]
LiuLiang_requestable_slots = LiuLiang_informable_slots + [
    "适用品牌", "产品介绍", "计费方式","套餐内容_定向视频流量", "套餐内容_夜间闲时流量", "套餐内容_其他功能", "套餐内容",
    "超出处理_国内流量", "超出处理",
    "结转规则_国内流量", "结转规则",
    "是否包含港澳台地区", "能否结转滚存", "能否分享", "能否转赠",
    "流量分享方式", "流量转赠方式", "转户转品牌管理", "停机销号管理", "赠送优惠活动",
    "使用限制", "使用有效期", "使用方式设置", "封顶规则", "限速说明",
    "受理时间", "互斥业务", "开通客户限制", "累次叠加规则", "开通方式", "开通生效规则",
    "是否到期自动取消", "能否变更或取消","取消方式", "取消变更生效规则", "变更方式"
]
LiuLiang_DB_slots = ["子业务" , "主业务"] + LiuLiang_requestable_slots
LiuLiang_Recommend_entity = "畅游包"


# WLAN 业务
WLAN_name_entity = {'WLAN标准套餐': ['WLAN标准套餐'],
                    'WLAN校园套餐': ['10元WLAN校园套餐', '20元WLAN校园套餐', '40元WLAN校园套餐'],
                    'WLAN流量套餐': ['10元WLAN流量套餐', '20元WLAN流量套餐', '30元WLAN流量套餐', '50元WLAN流量套餐', '70元WLAN流量套餐', '100元WLAN流量套餐']}
WLAN_informable_slots = [
    "功能费",
]
WLAN_requestable_slots = WLAN_informable_slots +[
    "套餐内容_WLAN流量", "套餐内容_WLAN时长",
    "适用品牌", "产品介绍", "计费方式", "套餐内容",
    "超出处理_WLAN流量", "超出处理_WLAN时长", "超出处理",
    "结转规则_WLAN流量", "结转规则_WLAN时长", "结转规则",
    "是否包含港澳台地区", "能否结转滚存", "能否分享", "能否转赠",
    "流量分享方式", "流量转赠方式", "转户转品牌管理", "停机销号管理", "赠送优惠活动",
    "使用限制", "使用有效期", "使用方式设置", "封顶规则", "限速说明",
    "受理时间", "互斥业务", "开通客户限制", "累次叠加规则", "开通方式", "开通生效规则",
     "是否到期自动取消", "能否变更或取消","取消方式", "取消变更生效规则", "变更方式",
    "密码重置方式"
]
WLAN_DB_slots = ["子业务", "主业务"] + WLAN_requestable_slots
WLAN_Recommend_entity = "WLAN流量套餐"



# 号卡业务
Card_name_entity = {"号卡" : ["4G包年卡", "4G飞享卡", "4G任我用卡", "4G爱家卡", "8元卡", "万能副卡"]}
Card_informable_slots = []
Card_requestable_slots = [
    "对应套餐", "产品介绍","功能费",
    "套餐内容_国内主叫", "套餐内容_国内短信", "套餐内容_国内彩信",  "套餐内容_国内流量", "套餐内容_本地流量", "套餐内容_定向视频流量", "套餐内容_夜间闲时流量", "套餐内容_WLAN流量", "套餐内容",
    "超出处理",  "结转规则",
    "是否全国接听免费", "是否包含港澳台地区", "能否结转滚存", "能否分享", "能否转赠",
    "流量分享方式", "流量转赠方式", "转户转品牌管理", "停机销号管理", "赠送优惠活动",
    "使用限制", "使用有效期", "使用方式设置", "封顶规则", "限速说明",
    "受理时间", "互斥业务", "开通客户限制", "累次叠加规则", "开通方式", "开通生效规则",
    "是否自动顺延到下月", "是否到期自动取消", "能否变更或取消","取消方式", "取消变更生效规则", "变更方式",
    "激活方式", "主副卡处理"
]
Card_DB_slots = ["号卡"] + Card_requestable_slots
Card_Gerneral_introduction = "中国移动推出了4G包年卡、4G飞享卡、4G任我用卡、4G爱家卡、万能副卡等多种号卡服务。请问您想了解哪个业务？"

# # 增值业务  先不做吧
# ZengZhi_name_entity ={"业务": {'无线音乐', '和校园', '和娱乐', '139邮箱20元版', '亲情通', '彩铃', '休闲娱乐', '和留言', '咪咕阅读', '和通讯录', '满意100优惠资讯', 'mm移动应用商场', '和彩印', '手机冲浪', '139邮箱免费版', '139邮箱5元版', '新闻与评论', '呼叫转移', '手机彩票', '和包', '生活助手', '飞信', '咪咕视频', '移动秘书', '飞信会员'}}
# ZengZhi_informabe_slot = []
# ZengZhi_requestable_slot = [
#     "适用品牌", "产品介绍", "计费方式",
#     "转户转品牌管理", "停机销号管理", "赠送优惠活动",
#     "使用限制", "使用有效期", "使用方式设置",
#     "受理时间", "开通客户限制", "累次叠加规则", "开通方式", "开通生效规则",
#     "能否变更或取消","取消方式", "取消变更生效规则", "变更方式",
#     "暂停方式", "恢复方式"
# ]


Overseas_name_entity = {
    '国际/港澳台漫游': ['短期国际及港澳台漫游', '180天国际及港澳台漫游', '国际/港澳台漫游'],
    '多国/大包多天流量包': ['一带一路多国流量包', '欧洲多国流量包', '北美多国流量包', '南美多国流量包',
                                        '非洲多国流量包', '大洋洲多国流量包', '日本大包多天流量包', '韩国大包多天流量包',
                                        '阿联酋大包多天流量包', '港澳台三地流量包'],
    '港澳台三地畅游包': ['港澳台三地畅游包（3天）', '港澳台三地畅游包（5天）', '港澳台三地畅游包（7天）'],
    '2018俄罗斯世界杯特惠包': ['2018俄罗斯世界杯特惠包（7天）', '2018俄罗斯世界杯特惠包（15天）'],
    '数据流量包': ['3元数据流量包', '30元流量包天优惠', '30元流量封顶限制',
                        '6元数据流量包', '60元流量包天优惠', '60元流量封顶限制',
                        '9元数据流量包', '90元流量包天优惠', '90元流量封顶限制'],
    '“海外随心看”日套餐': ['“海外随心看”日套餐']
}
Overseas_informable_slots = [
    "开通方向"
]
Overseas_requestable_slots = Overseas_informable_slots +[
    "开通天数","功能费",
    "产品介绍", "计费方式",
    "套餐内容_国内主叫", "套餐内容_国内短信", "套餐内容_国内彩信", "套餐内容_国内流量", "套餐内容_其他功能", "套餐内容",
    "超出处理_国内主叫", "超出处理_国内短信", "超出处理_国内流量", "超出处理",
    "能否结转滚存", "能否分享", "能否转赠",
    "流量分享方式", "流量转赠方式", "转户转品牌管理", "停机销号管理", "赠送优惠活动",
    "使用限制", "封顶规则", "限速说明",
    "受理时间", "互斥业务", "开通客户限制", "累次叠加规则", "开通方式", "开通生效规则",
    "是否到期自动取消", "能否变更或取消","取消方式", "到期失效规则"]
Overseas_DB_slots = ["子业务", "主业务"] + Overseas_requestable_slots


# 家庭多终端
MultiTerminal_name_entity = {
    '和家庭分享': ['和家庭分享', '加10元流量翻番', '和家庭安心包', '和家庭流量包'],
    '家庭计划': ['家庭计划月套餐', '家庭计划年套餐'],
    '多终端分享': ['4G多终端分享'],
    '和校园': ['和校园标准版', '和校园增强版'],
    '亲情通': ['亲情通']
}
MultiTerminal_informable_slots = [
    # "功能费",
    # "副卡数量上限"
]
MultiTerminal_requestable_slots = MultiTerminal_informable_slots +[
    "产品介绍", "计费方式","适用品牌","功能费","副卡数量上限",
    "能否分享", "套餐内容_通话共享规则", "套餐内容_短信共享规则", "套餐内容_流量共享规则",  # 归为 能否分享
    "套餐内容_其他功能", "套餐内容",  "结转规则_国内流量","是否包含港澳台地区",
    "能否结转滚存", "能否分享", "能否转赠",
    "流量分享方式", "流量转赠方式", "转户转品牌管理", "停机销号管理", "赠送优惠活动",
    "使用有效期",  "封顶规则", "限速说明", "受理时间",
    "互斥业务", "主卡互斥业务", "副卡互斥业务", # 归为  互斥业务
    "开通客户限制", "主卡开通客户限制","副卡客户限制", "主卡套餐限制", "其他开通限制" , # 归为 开通客户限制
     "开通方式", "取消方式",
    "主卡添加成员", "主卡删除成员","副卡成员主动退出","主卡查询副卡","副卡查询主卡", "恢复流量功能",
    "开通生效规则","取消变更生效规则","是否自动顺延到下月", "是否到期自动取消", "能否变更或取消"]
MultiTerminal_DB_slots = ["子业务", "主业务"] + MultiTerminal_requestable_slots
MultiTerminal_DB_slots.remove("能否分享")
MultiTerminal_DB_slots.remove("互斥业务")
MultiTerminal_DB_slots.remove("开通客户限制")
MultiTerminal_Gerneral_introduction = "北京移动面向已开通“4G套餐”的客户，推出“4G多终端流量共享”“和家庭共享”“家庭计划”等业务，一人有4G,大家一起用。请问您想了解哪个业务？"




