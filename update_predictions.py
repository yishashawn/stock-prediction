"""
更新预测数据脚本
每天收盘后运行此脚本，自动更新实际收盘价并重新训练模型
"""

import json
import os
from datetime import datetime
from predict_stock_price_advanced import build_and_update_model

def update_predictions():
    """更新预测数据"""
    print("=" * 80)
    print("更新中际旭创价格预测数据")
    print("=" * 80)
    
    # 读取历史记录
    history_file = 'prediction_history.json'
    if not os.path.exists(history_file):
        print("未找到历史记录文件，将创建新模型...")
        build_and_update_model()
        return
    
    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    # 重新构建模型（会自动获取最新数据）
    print("\n正在重新构建模型并更新预测...")
    build_and_update_model()
    
    print("\n" + "=" * 80)
    print("更新完成！")
    print("=" * 80)
    print("\n请打开 中际旭创_价格预测.html 查看更新后的预测结果")

if __name__ == '__main__':
    update_predictions()

