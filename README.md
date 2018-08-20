### 系统整体结构如下

```
├─DM  			    对话管理器，实现对话状态跟踪和对话策略生成
│  ├─DST		
│  └─policy
├─data 				存放数据和预处理脚本的文件夹
│  ├─DataBase 	 	存放数据库，本体等
│  ├─DialogData 	存放对话数据
│  ├─tmp			存放中间文件，如词典、词向量等, 非自动生成的文件有前缀‘_’
│  ├─WordDict 		存放生成词典、词向量的脚本
│  └─WordSeg 		存放分词脚本
├─NLU 				处理输入数据
│  ├─DomDect 		领域检测
│  │  └─model  	
│  │      └─ckpt 	
│  ├─NER 			业务实体识别
│  ├─SentiDect 		情感检测
│  ├─SlotFilling 	识别本轮槽值对、问询槽
│  │  └─model
│  │      └─ckpt
│  └─UserAct 		用户动作检测
│      └─model
│          └─ckpt
└─NLG 				自然语言生成
```


运行：
在主目录下运行命令 python Agent.py --print=<whether to print details or not>
输入restrat可重置dialog state

