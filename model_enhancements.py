"""
模型增强功能模块
包含：模型解释性、风险管理、实时数据集成、自动化部署等功能
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import os
import pickle
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


# ==================== 1. 模型解释性 ====================

def calculate_shap_values(model, X_sample, feature_names):
    """计算SHAP值（解释每个特征的贡献）
    
    需要安装: pip install shap
    """
    try:
        import shap
        shap.initjs()
        
        # 创建SHAP解释器
        if hasattr(model, 'predict_proba'):
            # 树模型（XGBoost, LightGBM, RandomForest）
            explainer = shap.TreeExplainer(model)
        else:
            # 其他模型使用KernelExplainer（较慢）
            explainer = shap.KernelExplainer(model.predict, X_sample[:100])  # 使用样本加速
        
        # 计算SHAP值
        shap_values = explainer.shap_values(X_sample)
        
        # 可视化
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        # 创建SHAP摘要图
        plt.figure(figsize=(12, 8))
        shap.summary_plot(shap_values, X_sample, feature_names=feature_names, show=False)
        plt.tight_layout()
        plt.savefig('中际旭创_SHAP特征重要性.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 计算平均绝对SHAP值（特征重要性）
        if len(shap_values.shape) > 1:
            feature_importance = np.abs(shap_values).mean(0)
        else:
            feature_importance = np.abs(shap_values).mean()
        
        # 创建特征重要性DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'shap_importance': feature_importance
        }).sort_values('shap_importance', ascending=False)
        
        return shap_values, importance_df, explainer
    except ImportError:
        print("SHAP库未安装。安装命令: pip install shap")
        return None, None, None
    except Exception as e:
        print(f"SHAP值计算失败: {str(e)[:50]}")
        return None, None, None


def calculate_lime_explanation(model, X_sample, feature_names, instance_idx=0):
    """计算LIME局部解释（解释单个预测）
    
    需要安装: pip install lime
    """
    try:
        from lime.lime_tabular import LimeTabularExplainer
        
        # 创建LIME解释器
        explainer = LimeTabularExplainer(
            X_sample.values,
            feature_names=feature_names,
            mode='regression'
        )
        
        # 解释单个实例
        explanation = explainer.explain_instance(
            X_sample.iloc[instance_idx].values,
            model.predict,
            num_features=min(10, len(feature_names))
        )
        
        # 保存解释结果
        explanation.save_to_file('中际旭创_LIME解释.html')
        
        return explanation
    except ImportError:
        print("LIME库未安装。安装命令: pip install lime")
        return None
    except Exception as e:
        print(f"LIME解释计算失败: {str(e)[:50]}")
        return None


def visualize_feature_importance(model, feature_names, merged=None, X_sample=None, save_path='中际旭创_特征重要性详细分析.png'):
    """可视化特征重要性（多种方法）"""
    print(f"    开始生成特征重要性分析图: {save_path}")
    try:
        # 确保matplotlib使用非交互式后端（避免在某些环境下无法保存）
        import matplotlib
        if matplotlib.get_backend() != 'Agg':
            matplotlib.use('Agg')
        
        # 特征名称映射（英文转中文）
        feature_name_map = {
            'price_ma5_ratio': '价格相对MA5位置', 'price_ma10_ratio': '价格相对MA10位置', 'price_ma20_ratio': '价格相对MA20位置',
            'vol_ratio': '成交量比率', 'vol_ratio_10': '成交量比率(10日)',
            'momentum_5': '5日动量', 'momentum_10': '10日动量',
            'rsi': 'RSI指标', 'macd': 'MACD指标', 'macd_hist': 'MACD柱状图',
            'volatility_5': '5日波动率', 'volatility_10': '10日波动率',
            'high_low_ratio': '高低价比率', 'prev_pct_chg': '前一日涨跌幅',
            'kdj_k': 'KDJ-K值', 'kdj_d': 'KDJ-D值', 'kdj_j': 'KDJ-J值',
            'boll_mid': '布林带中轨', 'boll_upper': '布林带上轨', 'boll_lower': '布林带下轨',
            'boll_width': '布林带宽度', 'boll_position': '价格在布林带位置',
            'cci': 'CCI指标', 'obv': 'OBV指标', 'obv_ma': 'OBV均线', 'obv_ratio': 'OBV比率',
            'wr': '威廉指标', 'plus_di': 'DMI+DI', 'minus_di': 'DMI-DI', 'adx': 'DMI-ADX',
            'margin_balance_change': '融资余额变化率', 'short_balance_change': '融券余额变化率',
            'holder_change_pct': '股东户数变化率', 'margin_ratio': '融资占比',
            'inst_hold_vol_change': '机构持仓量变化率', 'inst_hold_num_change': '机构持仓数量变化率',
            'roe': '净资产收益率', 'roa': '总资产收益率', 'grossprofit_rate': '毛利率',
            'netprofit_rate': '净利率', 'eps': '每股收益', 'bps': '每股净资产',
            'revenue_yoy': '营收同比增长率', 'n_income_yoy': '净利润同比增长率',
            'revenue_qoq': '营收环比增长率', 'n_income_qoq': '净利润环比增长率',
            'forecast_optimism': '业绩预告乐观度',
            'cyb_pct': '创业板指涨跌幅', 'sz_pct': '深证成指涨跌幅', 'hs300_pct': '沪深300涨跌幅',
            'sh_pct': '上证指数涨跌幅', 'zz500_pct': '中证500涨跌幅',
            'btc_pct': '比特币涨跌幅', 'SP500_pct': '标普500涨跌幅',
            'NASDAQ_pct': '纳斯达克涨跌幅', 'DOW_pct': '道琼斯涨跌幅',
            'net_ratio': '资金净流入比率', 'net_mf_amount': '资金净流入',
            'turnover_rate': '换手率', 'circ_mv': '流通市值', 'total_mv': '总市值',
            'new_fiber_pct': '新易盛涨跌幅',
            'cpi_yoy': 'CPI同比增长率', 'cpi_mom': 'CPI环比增长率',
            'pmi': 'PMI指数', 'pmi_change': 'PMI变化', 'gdp_yoy': 'GDP同比增长率',
            'interest_rate': '利率', 'interest_rate_change': '利率变化',
            'exchange_rate': '汇率', 'exchange_rate_change': '汇率变化率',
            'm2_yoy': 'M2同比增长率', 'm2_mom': 'M2环比增长率',
            'news_sentiment': '新闻情绪得分',
            'is_monday': '是否周一', 'is_friday': '是否周五', 'is_tuesday': '是否周二',
            'friday_pct_chg': '周五涨跌幅'
        }
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 方法1：基于模型的特征重要性
        importances = None
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            coef = model.coef_
            if len(coef.shape) > 1:
                importances = np.abs(coef).mean(axis=0)
            else:
                importances = np.abs(coef)
        elif hasattr(model, 'estimators_'):
            # 对于集成模型，尝试获取基础模型的重要性
            try:
                if len(model.estimators_) > 0 and hasattr(model.estimators_[0], 'feature_importances_'):
                    importances = np.mean([est.feature_importances_ for est in model.estimators_], axis=0)
            except:
                pass
        
        if importances is not None and len(importances) == len(feature_names):
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False).head(20)
            
            if len(importance_df) > 0:
                # 转换为中文名称
                importance_df['feature_cn'] = importance_df['feature'].map(lambda x: feature_name_map.get(x, x))
                axes[0, 0].barh(range(len(importance_df)), importance_df['importance'])
                axes[0, 0].set_yticks(range(len(importance_df)))
                axes[0, 0].set_yticklabels(importance_df['feature_cn'], fontsize=9)
                axes[0, 0].set_xlabel('重要性', fontsize=11)
                axes[0, 0].set_title('模型特征重要性（Top 20）', fontsize=12, fontweight='bold')
                axes[0, 0].invert_yaxis()
            else:
                axes[0, 0].text(0.5, 0.5, '无可用数据', ha='center', va='center')
                axes[0, 0].set_title('模型特征重要性', fontsize=12)
        else:
            axes[0, 0].text(0.5, 0.5, '模型不支持特征重要性', ha='center', va='center')
            axes[0, 0].set_title('模型特征重要性', fontsize=12)
        
        # 方法2：SHAP值（如果可用）
        try:
            import shap
            if X_sample is not None and len(X_sample) > 0:
                try:
                    # 检查模型类型，选择合适的explainer
                    if hasattr(model, 'feature_importances_') or (hasattr(model, 'estimators_') and len(model.estimators_) > 0):
                        # 树模型（RandomForest, XGBoost, LightGBM等）
                        explainer = shap.TreeExplainer(model)
                        shap_values = explainer.shap_values(X_sample[:100])
                    elif hasattr(model, 'predict'):
                        # 其他模型使用KernelExplainer（较慢）
                        explainer = shap.KernelExplainer(model.predict, X_sample[:50])
                        shap_values = explainer.shap_values(X_sample[:50])
                    else:
                        raise Exception("模型不支持SHAP分析")
                    
                    if shap_values is not None:
                        if isinstance(shap_values, list):
                            shap_values = shap_values[0]
                        if len(shap_values.shape) > 1:
                            shap_importance = np.abs(shap_values).mean(0)
                        else:
                            shap_importance = np.abs(shap_values)
                        
                        if len(shap_importance) == len(feature_names):
                            shap_df = pd.DataFrame({
                                'feature': feature_names,
                                'shap_importance': shap_importance
                            }).sort_values('shap_importance', ascending=False).head(20)
                            
                            if len(shap_df) > 0:
                                # 转换为中文名称
                                shap_df['feature_cn'] = shap_df['feature'].map(lambda x: feature_name_map.get(x, x))
                                axes[0, 1].barh(range(len(shap_df)), shap_df['shap_importance'])
                                axes[0, 1].set_yticks(range(len(shap_df)))
                                axes[0, 1].set_yticklabels(shap_df['feature_cn'], fontsize=9)
                                axes[0, 1].set_xlabel('SHAP重要性', fontsize=11)
                                axes[0, 1].set_title('SHAP特征重要性（Top 20）', fontsize=12, fontweight='bold')
                                axes[0, 1].invert_yaxis()
                            else:
                                axes[0, 1].text(0.5, 0.5, '无可用数据', ha='center', va='center')
                                axes[0, 1].set_title('SHAP特征重要性', fontsize=12)
                        else:
                            axes[0, 1].text(0.5, 0.5, f'SHAP维度不匹配\n{len(shap_importance)} vs {len(feature_names)}', ha='center', va='center')
                            axes[0, 1].set_title('SHAP特征重要性', fontsize=12)
                    else:
                        axes[0, 1].text(0.5, 0.5, 'SHAP计算失败', ha='center', va='center')
                        axes[0, 1].set_title('SHAP特征重要性', fontsize=12)
                except Exception as e:
                    error_msg = str(e)[:50] if len(str(e)) > 50 else str(e)
                    axes[0, 1].text(0.5, 0.5, f'SHAP不可用\n{error_msg}', ha='center', va='center', fontsize=9)
                    axes[0, 1].set_title('SHAP特征重要性', fontsize=12)
            else:
                axes[0, 1].text(0.5, 0.5, '缺少样本数据', ha='center', va='center')
                axes[0, 1].set_title('SHAP特征重要性', fontsize=12)
        except ImportError:
            axes[0, 1].text(0.5, 0.5, 'SHAP库未安装\npip install shap', ha='center', va='center')
            axes[0, 1].set_title('SHAP特征重要性', fontsize=12)
        except Exception as e:
            error_msg = str(e)[:50] if len(str(e)) > 50 else str(e)
            axes[0, 1].text(0.5, 0.5, f'SHAP错误\n{error_msg}', ha='center', va='center', fontsize=9)
            axes[0, 1].set_title('SHAP特征重要性', fontsize=12)
        
        # 方法3：特征相关性
        corr_data = None
        if merged is not None and 'pct_chg' in merged.columns:
            try:
                # 调试信息
                print(f"    调试: merged形状={merged.shape}, pct_chg列存在={('pct_chg' in merged.columns)}")
                print(f"    调试: feature_names数量={len(feature_names)}, merged列数={len(merged.columns)}")
                
                # 只选择存在的特征
                available_features = [f for f in feature_names if f in merged.columns]
                print(f"    调试: 可用特征数量={len(available_features)}")
                
                if len(available_features) > 0:
                    # 计算相关性，处理缺失值 - 使用更宽松的策略
                    # 只删除pct_chg为NaN的行，其他特征的NaN在计算相关性时会被忽略
                    temp_data = merged[available_features + ['pct_chg']].copy()
                    temp_data = temp_data.dropna(subset=['pct_chg'])  # 只删除pct_chg为NaN的行
                    
                    print(f"    调试: 删除pct_chg为NaN后，剩余数据={len(temp_data)}行")
                    
                    if len(temp_data) > 0:
                        # 计算每个特征与pct_chg的相关性（忽略NaN）
                        correlations = {}
                        for f in available_features:
                            if f in temp_data.columns:
                                # 只使用两个字段都不为NaN的数据
                                valid_data = temp_data[[f, 'pct_chg']].dropna()
                                if len(valid_data) > 3:  # 降低要求：至少需要3个有效数据点
                                    try:
                                        corr = valid_data[f].corr(valid_data['pct_chg'])
                                        if not np.isnan(corr) and not np.isinf(corr):
                                            correlations[f] = abs(corr)
                                    except Exception as e:
                                        pass
                        
                        print(f"    调试: 成功计算相关性的特征数量={len(correlations)}")
                        
                        if len(correlations) > 0:
                            # 转换为Series并排序
                            corr_data = pd.Series(correlations).sort_values(ascending=False).head(20)
                            
                            if len(corr_data) > 0:
                                # 转换为中文名称
                                corr_data_cn = corr_data.copy()
                                corr_data_cn.index = [feature_name_map.get(idx, idx) for idx in corr_data.index]
                                axes[1, 0].barh(range(len(corr_data_cn)), corr_data_cn.values)
                                axes[1, 0].set_yticks(range(len(corr_data_cn)))
                                axes[1, 0].set_yticklabels(corr_data_cn.index, fontsize=9)
                                axes[1, 0].set_xlabel('与涨跌幅的相关系数（绝对值）', fontsize=11)
                                axes[1, 0].set_title('特征相关性（Top 20）', fontsize=12, fontweight='bold')
                                axes[1, 0].invert_yaxis()
                            else:
                                axes[1, 0].text(0.5, 0.5, '无可用数据', ha='center', va='center')
                                axes[1, 0].set_title('特征相关性', fontsize=12)
                        else:
                            # 如果逐个计算失败，尝试使用整体corr方法
                            try:
                                print("    调试: 逐个计算失败，尝试使用整体corr方法...")
                                temp_data_filled = temp_data.fillna(0)  # 用0填充NaN
                                if len(temp_data_filled) > 5:  # 降低要求
                                    corr_all = temp_data_filled[available_features + ['pct_chg']].corr()['pct_chg'].drop('pct_chg').abs().sort_values(ascending=False).head(20)
                                    if len(corr_all) > 0:
                                        corr_all_cn = corr_all.copy()
                                        corr_all_cn.index = [feature_name_map.get(idx, idx) for idx in corr_all.index]
                                        axes[1, 0].barh(range(len(corr_all_cn)), corr_all_cn.values)
                                        axes[1, 0].set_yticks(range(len(corr_all_cn)))
                                        axes[1, 0].set_yticklabels(corr_all_cn.index, fontsize=9)
                                        axes[1, 0].set_xlabel('与涨跌幅的相关系数（绝对值）', fontsize=11)
                                        axes[1, 0].set_title('特征相关性（Top 20）', fontsize=12, fontweight='bold')
                                        axes[1, 0].invert_yaxis()
                                        print(f"    调试: 使用整体corr方法成功，显示{len(corr_all_cn)}个特征")
                                    else:
                                        axes[1, 0].text(0.5, 0.5, '无法计算相关性\n（corr结果为空）', ha='center', va='center', fontsize=10)
                                        axes[1, 0].set_title('特征相关性', fontsize=12)
                                else:
                                    axes[1, 0].text(0.5, 0.5, f'数据不足\n（仅{len(temp_data_filled)}行，需要>5）', ha='center', va='center', fontsize=10)
                                    axes[1, 0].set_title('特征相关性', fontsize=12)
                            except Exception as e2:
                                error_msg = str(e2)[:50] if len(str(e2)) > 50 else str(e2)
                                axes[1, 0].text(0.5, 0.5, f'无法计算相关性\n{error_msg}', ha='center', va='center', fontsize=9)
                                axes[1, 0].set_title('特征相关性', fontsize=12)
                                print(f"    调试: 整体corr方法失败: {error_msg}")
                    else:
                        axes[1, 0].text(0.5, 0.5, f'数据不足\n（pct_chg全为NaN）', ha='center', va='center', fontsize=10)
                        axes[1, 0].set_title('特征相关性', fontsize=12)
                else:
                    # 显示哪些特征不在merged中
                    missing_features = [f for f in feature_names[:10] if f not in merged.columns]
                    error_msg = f'无可用特征\n前10个特征中缺失: {", ".join(missing_features[:3])}...' if missing_features else '无可用特征'
                    axes[1, 0].text(0.5, 0.5, error_msg, ha='center', va='center', fontsize=9)
                    axes[1, 0].set_title('特征相关性', fontsize=12)
            except Exception as e:
                import traceback
                error_msg = str(e)[:50] if len(str(e)) > 50 else str(e)
                axes[1, 0].text(0.5, 0.5, f'相关性计算失败\n{error_msg}', ha='center', va='center', fontsize=9)
                axes[1, 0].set_title('特征相关性', fontsize=12)
                print(f"    特征相关性计算错误详情: {traceback.format_exc()[:300]}")
        else:
            error_info = []
            if merged is None:
                error_info.append("merged为None")
            elif 'pct_chg' not in merged.columns:
                error_info.append("缺少pct_chg列")
                if merged is not None:
                    error_info.append(f"merged列: {', '.join(merged.columns[:5].tolist())}...")
            axes[1, 0].text(0.5, 0.5, f'缺少数据\n{"; ".join(error_info)}', ha='center', va='center', fontsize=9)
            axes[1, 0].set_title('特征相关性', fontsize=12)
        
        # 方法4：特征重要性对比
        if importances is not None and len(importances) == len(feature_names) and merged is not None and 'pct_chg' in merged.columns:
            try:
                print(f"    调试: 开始计算特征重要性对比，importances长度={len(importances)}, feature_names长度={len(feature_names)}")
                
                available_features = [f for f in feature_names if f in merged.columns]
                print(f"    调试: 可用特征数量={len(available_features)}")
                
                if len(available_features) > 0:
                    # 计算相关性（使用与方法3相同的策略）
                    temp_data = merged[available_features + ['pct_chg']].copy()
                    temp_data = temp_data.dropna(subset=['pct_chg'])
                    
                    print(f"    调试: 删除pct_chg为NaN后，剩余数据={len(temp_data)}行")
                    
                    if len(temp_data) > 0:
                        # 先尝试逐个计算相关性
                        corr_data_dict = {}
                        for f in available_features:
                            if f in temp_data.columns:
                                valid_data = temp_data[[f, 'pct_chg']].dropna()
                                if len(valid_data) > 3:  # 降低要求：至少需要3个有效数据点
                                    try:
                                        corr = valid_data[f].corr(valid_data['pct_chg'])
                                        if not np.isnan(corr) and not np.isinf(corr):
                                            corr_data_dict[f] = abs(corr)
                                    except:
                                        pass
                        
                        # 如果逐个计算失败，尝试使用整体corr方法
                        if len(corr_data_dict) == 0:
                            try:
                                print("    调试: 逐个计算失败，尝试使用整体corr方法...")
                                temp_data_filled = temp_data.fillna(0)
                                if len(temp_data_filled) > 5:  # 降低要求
                                    corr_all = temp_data_filled[available_features + ['pct_chg']].corr()['pct_chg'].drop('pct_chg').abs()
                                    corr_data_dict = corr_all.to_dict()
                                    print(f"    调试: 使用整体corr方法，获得{len(corr_data_dict)}个相关性值")
                            except:
                                pass
                        
                        print(f"    调试: 相关性字典长度={len(corr_data_dict)}")
                        
                        # 创建对比数据
                        comparison_data = []
                        for i, f in enumerate(feature_names):
                            if f in available_features and i < len(importances):
                                comparison_data.append({
                                    'feature': f,
                                    'model_importance': importances[i],
                                    'correlation': corr_data_dict.get(f, 0)
                                })
                        
                        print(f"    调试: 对比数据长度={len(comparison_data)}")
                        
                        if len(comparison_data) > 0:
                            comparison_df = pd.DataFrame(comparison_data)
                            # 过滤掉模型重要性为0且相关性也为0的特征
                            comparison_df = comparison_df[
                                (comparison_df['model_importance'] > 0) | (comparison_df['correlation'] > 0)
                            ].sort_values('model_importance', ascending=False).head(15)
                            
                            print(f"    调试: 过滤后对比数据长度={len(comparison_df)}")
                            
                            if len(comparison_df) > 0:
                                # 转换为中文名称
                                comparison_df['feature_cn'] = comparison_df['feature'].map(lambda x: feature_name_map.get(x, x))
                                
                                x = np.arange(len(comparison_df))
                                width = 0.35
                                # 归一化以便对比（都缩放到0-1范围）
                                max_imp = comparison_df['model_importance'].max()
                                max_corr = comparison_df['correlation'].max()
                                if max_imp > 0:
                                    norm_imp = comparison_df['model_importance'] / max_imp
                                else:
                                    norm_imp = comparison_df['model_importance']
                                if max_corr > 0:
                                    norm_corr = comparison_df['correlation'] / max_corr
                                else:
                                    norm_corr = comparison_df['correlation']
                                
                                axes[1, 1].bar(x - width/2, norm_imp, width, label='模型重要性（归一化）', alpha=0.8)
                                axes[1, 1].bar(x + width/2, norm_corr, width, label='相关性（归一化）', alpha=0.8)
                                axes[1, 1].set_xlabel('特征', fontsize=11)
                                axes[1, 1].set_ylabel('重要性（归一化）', fontsize=11)
                                axes[1, 1].set_title('特征重要性对比（Top 15）', fontsize=12, fontweight='bold')
                                axes[1, 1].set_xticks(x)
                                axes[1, 1].set_xticklabels(comparison_df['feature_cn'], rotation=45, ha='right', fontsize=8)
                                axes[1, 1].legend()
                                print(f"    调试: 成功绘制特征重要性对比图，显示{len(comparison_df)}个特征")
                            else:
                                axes[1, 1].text(0.5, 0.5, '无有效数据\n（重要性全为0）', ha='center', va='center', fontsize=10)
                                axes[1, 1].set_title('特征重要性对比', fontsize=12)
                        else:
                            axes[1, 1].text(0.5, 0.5, '无法创建对比数据', ha='center', va='center')
                            axes[1, 1].set_title('特征重要性对比', fontsize=12)
                    else:
                        axes[1, 1].text(0.5, 0.5, f'数据不足\n（pct_chg全为NaN）', ha='center', va='center', fontsize=10)
                        axes[1, 1].set_title('特征重要性对比', fontsize=12)
                else:
                    axes[1, 1].text(0.5, 0.5, '无可用特征', ha='center', va='center')
                    axes[1, 1].set_title('特征重要性对比', fontsize=12)
            except Exception as e:
                import traceback
                error_msg = str(e)[:50] if len(str(e)) > 50 else str(e)
                axes[1, 1].text(0.5, 0.5, f'对比计算失败\n{error_msg}', ha='center', va='center', fontsize=9)
                axes[1, 1].set_title('特征重要性对比', fontsize=12)
                print(f"    特征重要性对比计算错误详情: {traceback.format_exc()[:300]}")
        else:
            error_info = []
            if importances is None:
                error_info.append("无模型重要性")
            elif len(importances) != len(feature_names):
                error_info.append(f"重要性维度不匹配({len(importances)} vs {len(feature_names)})")
            if merged is None:
                error_info.append("merged为None")
            elif 'pct_chg' not in merged.columns:
                error_info.append("缺少pct_chg列")
                if merged is not None:
                    error_info.append(f"merged列: {', '.join(merged.columns[:3].tolist())}...")
            axes[1, 1].text(0.5, 0.5, f'数据不足\n{"; ".join(error_info)}', ha='center', va='center', fontsize=9)
            axes[1, 1].set_title('特征重要性对比', fontsize=12)
        
        plt.tight_layout()
        try:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"    ✓ 特征重要性分析图已保存: {save_path}")
        except Exception as save_error:
            print(f"    ✗ 保存图片失败: {str(save_error)[:100]}")
            # 尝试使用不同的保存方法
            try:
                plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
                print(f"    ✓ 使用备用方法保存成功: {save_path}")
            except:
                print(f"    ✗ 备用保存方法也失败")
        finally:
            plt.close()
    except Exception as e:
        print(f"    ✗ 特征重要性可视化失败: {str(e)[:100]}")
        import traceback
        print(f"    错误详情: {traceback.format_exc()[:500]}")
        # 即使出错也尝试保存一个错误提示图
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f'特征重要性分析失败\n错误: {str(e)[:100]}', 
                   ha='center', va='center', fontsize=12, wrap=True)
            ax.set_title('特征重要性详细分析 - 生成失败', fontsize=14)
            plt.tight_layout()
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
            print(f"    ✓ 已保存错误提示图: {save_path}")
        except:
            pass


# ==================== 2. 风险管理 ====================

def calculate_prediction_intervals(model, X_test, y_test, confidence=0.95):
    """计算预测区间（置信区间）"""
    try:
        # 获取预测值
        predictions = model.predict(X_test)
        
        # 计算残差
        residuals = y_test - predictions
        
        # 计算残差的标准差
        residual_std = np.std(residuals)
        
        # 计算置信区间
        from scipy import stats
        z_score = stats.norm.ppf((1 + confidence) / 2)
        
        # 预测区间
        lower_bound = predictions - z_score * residual_std
        upper_bound = predictions + z_score * residual_std
        
        return predictions, lower_bound, upper_bound, residual_std
    except Exception as e:
        print(f"预测区间计算失败: {str(e)[:50]}")
        return None, None, None, None


def calculate_risk_metrics(predictions, actuals, prices):
    """计算风险指标"""
    try:
        risk_metrics = {}
        
        # 1. 波动率（预测值的标准差）
        risk_metrics['volatility'] = np.std(predictions)
        
        # 2. 最大回撤（基于价格）
        if prices is not None and len(prices) > 0:
            cumulative = (1 + np.array(predictions) / 100).cumprod()
            running_max = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - running_max) / running_max * 100
            risk_metrics['max_drawdown'] = np.min(drawdown)
            risk_metrics['current_drawdown'] = drawdown[-1] if len(drawdown) > 0 else 0
        
        # 3. VaR（风险价值，95%置信度）
        risk_metrics['var_95'] = np.percentile(predictions, 5)  # 5%分位数
        
        # 4. CVaR（条件风险价值）
        var_95 = risk_metrics['var_95']
        risk_metrics['cvar_95'] = predictions[predictions <= var_95].mean() if len(predictions[predictions <= var_95]) > 0 else var_95
        
        # 5. 夏普比率（假设无风险利率为0）
        if risk_metrics['volatility'] > 0:
            risk_metrics['sharpe_ratio'] = np.mean(predictions) / risk_metrics['volatility']
        else:
            risk_metrics['sharpe_ratio'] = 0
        
        return risk_metrics
    except Exception as e:
        print(f"风险指标计算失败: {str(e)[:50]}")
        return {}


def generate_stop_loss_take_profit(predicted_price, current_price, risk_metrics, risk_tolerance=0.02):
    """生成止损/止盈建议"""
    try:
        suggestions = {}
        
        # 预测涨跌幅
        predicted_pct = (predicted_price - current_price) / current_price * 100
        
        # 止损建议（基于风险容忍度）
        stop_loss_pct = -risk_tolerance * 100  # 默认-2%
        stop_loss_price = current_price * (1 + stop_loss_pct / 100)
        suggestions['stop_loss'] = {
            'price': stop_loss_price,
            'percentage': stop_loss_pct,
            'reason': f'基于风险容忍度 {risk_tolerance*100}%'
        }
        
        # 止盈建议（基于预测和风险调整）
        if predicted_pct > 0:
            # 如果预测上涨，设置止盈为预测价格的80%（保守）
            take_profit_pct = predicted_pct * 0.8
            take_profit_price = current_price * (1 + take_profit_pct / 100)
            suggestions['take_profit'] = {
                'price': take_profit_price,
                'percentage': take_profit_pct,
                'reason': '基于预测价格的80%（保守策略）'
            }
        else:
            # 如果预测下跌，不建议止盈
            suggestions['take_profit'] = None
        
        # 风险警告
        if 'var_95' in risk_metrics and risk_metrics['var_95'] < -5:
            suggestions['risk_warning'] = '高风险：95% VaR低于-5%'
        elif 'max_drawdown' in risk_metrics and risk_metrics['max_drawdown'] < -10:
            suggestions['risk_warning'] = '高风险：最大回撤超过-10%'
        else:
            suggestions['risk_warning'] = None
        
        return suggestions
    except Exception as e:
        print(f"止损止盈建议生成失败: {str(e)[:50]}")
        return {}


# ==================== 3. 实时数据集成 ====================

def get_realtime_news_sentiment(ts_code, hours=24):
    """获取实时新闻情绪（最近N小时）"""
    try:
        import tushare as ts
        pro = ts.pro_api()
        
        # 获取最近N小时的新闻
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=hours)
        
        news_df = pro.news(
            src='sina',
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d')
        )
        
        if news_df is not None and len(news_df) > 0:
            # 使用高级NLP分析（如果可用）
            from predict_stock_price_advanced import get_news_sentiment
            sentiment_df = get_news_sentiment(ts_code, start_date, end_date, use_advanced_nlp=True)
            return sentiment_df
        return None
    except Exception as e:
        print(f"实时新闻情绪获取失败: {str(e)[:50]}")
        return None


def get_social_media_sentiment(ts_code, platform='weibo'):
    """获取社交媒体情绪（微博、股吧等）
    
    注意：这需要相应的API接口，这里提供框架
    """
    try:
        # 这里需要接入实际的社交媒体API
        # 示例：使用爬虫或API获取数据
        
        if platform == 'weibo':
            # 微博情绪分析（需要API）
            print("微博情绪分析需要API接口")
            return None
        elif platform == 'guba':
            # 股吧情绪分析（需要API）
            print("股吧情绪分析需要API接口")
            return None
        else:
            return None
    except Exception as e:
        print(f"社交媒体情绪获取失败: {str(e)[:50]}")
        return None


def get_realtime_money_flow(ts_code):
    """获取实时资金流向数据"""
    try:
        import tushare as ts
        pro = ts.pro_api()
        
        # 获取实时行情（需要相应权限）
        try:
            realtime_df = pro.realtime_quote(ts_code=ts_code)
            if realtime_df is not None and len(realtime_df) > 0:
                # 计算实时资金流向
                if 'amount' in realtime_df.columns and 'vol' in realtime_df.columns:
                    # 简化计算（实际需要更复杂的逻辑）
                    return realtime_df[['ts_code', 'amount', 'vol']]
        except:
            print("实时行情数据需要更高权限")
        
        return None
    except Exception as e:
        print(f"实时资金流向获取失败: {str(e)[:50]}")
        return None


# ==================== 4. 自动化部署 ====================

class ModelVersionManager:
    """模型版本管理器"""
    
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
    
    def save_model(self, model, version, metadata=None):
        """保存模型版本"""
        try:
            version_dir = os.path.join(self.model_dir, f'v{version}')
            if not os.path.exists(version_dir):
                os.makedirs(version_dir)
            
            # 保存模型
            model_path = os.path.join(version_dir, 'model.pkl')
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # 保存元数据
            if metadata is None:
                metadata = {}
            metadata['version'] = version
            metadata['save_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            metadata_path = os.path.join(version_dir, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"模型已保存: {model_path}")
            return model_path
        except Exception as e:
            print(f"模型保存失败: {str(e)[:50]}")
            return None
    
    def load_model(self, version):
        """加载模型版本"""
        try:
            version_dir = os.path.join(self.model_dir, f'v{version}')
            model_path = os.path.join(version_dir, 'model.pkl')
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                return model
            else:
                print(f"模型版本 {version} 不存在")
                return None
        except Exception as e:
            print(f"模型加载失败: {str(e)[:50]}")
            return None
    
    def list_versions(self):
        """列出所有模型版本"""
        try:
            versions = []
            for item in os.listdir(self.model_dir):
                if item.startswith('v') and os.path.isdir(os.path.join(self.model_dir, item)):
                    version_num = item[1:]
                    try:
                        version_num = int(version_num)
                        versions.append(version_num)
                    except:
                        pass
            return sorted(versions)
        except Exception as e:
            print(f"版本列表获取失败: {str(e)[:50]}")
            return []


def setup_auto_update_task(script_path, schedule='daily', time='15:30'):
    """设置自动更新任务
    
    参数:
        script_path: 要运行的脚本路径
        schedule: 调度频率 ('daily', 'weekly', 'hourly')
        time: 运行时间（格式: 'HH:MM'）
    """
    try:
        import schedule
        import time as time_module
        
        def run_script():
            import subprocess
            subprocess.run(['python', script_path])
        
        if schedule == 'daily':
            schedule.every().day.at(time).do(run_script)
        elif schedule == 'weekly':
            schedule.every().week.at(time).do(run_script)
        elif schedule == 'hourly':
            schedule.every().hour.do(run_script)
        
        print(f"自动更新任务已设置: {schedule} at {time}")
        print("运行 schedule.run_pending() 来执行任务")
        
        return schedule
    except ImportError:
        print("schedule库未安装。安装命令: pip install schedule")
        return None
    except Exception as e:
        print(f"自动更新任务设置失败: {str(e)[:50]}")
        return None


def ab_test_models(model1, model2, X_test, y_test, model1_name='Model A', model2_name='Model B'):
    """A/B测试不同模型版本"""
    try:
        results = {}
        
        # 测试模型1
        pred1 = model1.predict(X_test)
        r2_1 = r2_score(y_test, pred1)
        rmse_1 = np.sqrt(mean_squared_error(y_test, pred1))
        
        # 测试模型2
        pred2 = model2.predict(X_test)
        r2_2 = r2_score(y_test, pred2)
        rmse_2 = np.sqrt(mean_squared_error(y_test, pred2))
        
        results[model1_name] = {'r2': r2_1, 'rmse': rmse_1}
        results[model2_name] = {'r2': r2_2, 'rmse': rmse_2}
        
        # 选择更好的模型
        if r2_1 > r2_2:
            best_model = model1_name
        else:
            best_model = model2_name
        
        results['best_model'] = best_model
        results['improvement'] = {
            'r2': abs(r2_1 - r2_2),
            'rmse': abs(rmse_1 - rmse_2)
        }
        
        # 可视化对比
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # R²对比
        axes[0].bar([model1_name, model2_name], [r2_1, r2_2])
        axes[0].set_ylabel('R²得分')
        axes[0].set_title('模型R²对比')
        axes[0].axhline(y=max(r2_1, r2_2), color='r', linestyle='--', alpha=0.5, label='最佳')
        axes[0].legend()
        
        # RMSE对比
        axes[1].bar([model1_name, model2_name], [rmse_1, rmse_2])
        axes[1].set_ylabel('RMSE')
        axes[1].set_title('模型RMSE对比')
        axes[1].axhline(y=min(rmse_1, rmse_2), color='r', linestyle='--', alpha=0.5, label='最佳')
        axes[1].legend()
        
        plt.tight_layout()
        plt.savefig('中际旭创_AB测试结果.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"A/B测试完成。最佳模型: {best_model}")
        print(f"  {model1_name}: R²={r2_1:.4f}, RMSE={rmse_1:.4f}")
        print(f"  {model2_name}: R²={r2_2:.4f}, RMSE={rmse_2:.4f}")
        
        return results
    except Exception as e:
        print(f"A/B测试失败: {str(e)[:50]}")
        return {}

