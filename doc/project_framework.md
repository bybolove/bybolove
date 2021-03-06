# 1.data
> 用于存放数据集

1. mars_tianchi_songs.csv 初始歌曲数据
2. mars_tianchi_user_actions.csv 初始用户行为数据
3. mars_tianchi_user_actions_testing.csv 切割出的用于测试集的用户行为数据
4. mars_tianchi_user_actions_training.csv 切割出的用于训练集的用户行为数据
5. label.csv 从3中提取出的匹配提交要求的统计数据
6. mars_tianchi_songs_tiny.csv 歌曲数据的小数据
7. mars_tianchi_user_actions_tiny.csv 用户行为的小数据 
8. mars_tianchi_user_actions_tiny_testing.csv 用于测试集的用户行为的小数据
9. mars_tianchi_user_actions_tiny_training.csv 用于训练集的用户行为的小数据
10.label_tiny.csv 从8中提取出的统计数据

# 2.doc
> 用于存放文档，描述性文件

1. project_framework.md 用于描述整个项目框架。
2. interface.md 用于描述一些公共接口使用。
3. dataset\_analysis_160322.md 对不同预测方法的可用训练集大小进行了估计。
4. time\_series\_plot_160326.md 每个艺人6个月内的play数量构成的时间序列，帮助观察一些规律

# 3.src
> 存放源码

1. logging.conf: python.logging的配置文件
2. gbdt.py: 用gbdt测试简单模型

## 3.1 script

> 放一些简单的脚本，用于数据调研类的

1. data_statistics.sh: 用于统计数据规模 (./data_statistics.sh)
2. data_split.py: 用于切割数据，生成相应的训练测试集，以及label数据 (./data_split.py <number of days for testing>)
3. usr_song_artist_action_exploration.R  探索原始数据集中数据点的个数，比如用户u对歌曲s有多少天（以天为基本单位）播放（play操作）记录。
4. usr_song_artist_exploration.R 探索原始数据集中数据点的个数，不区分3种操作（播放，下载，收藏），比如用户u对歌曲s有多少天操作记录。
5. TimeSeries_Generation_Artist.R 对每个艺人生成时间序列并保存到csv文件
6. TimeSeries_Plot.R 对每个艺人绘制时间序列


## 3.2 utils

> 公共的接口，工具

1. data_set.py 数据读取和处理
2. evaluate.py 评估最终的预测结果
3. feature_handler.py 一些特征处理，如归一化，离散化

