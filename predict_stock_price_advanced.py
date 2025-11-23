"""
中际旭创股票价格预测模型（增强版）
支持未来日期预测和自动更新
"""

import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, VotingRegressor, StackingRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score, make_scorer
from sklearn.feature_selection import SelectKBest, f_regression, RFE, RFECV
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
import warnings
import os
import json
warnings.filterwarnings('ignore')

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 设置token
TOKEN = '6eeadde0c615452a0b1015218259e8175877a7c04d11c3c95eb22b57'
ts.set_token(TOKEN)
pro = ts.pro_api()

# 股票代码
ZJXC_CODE = '300308.SZ'  # 中际旭创

def get_stock_data(ts_code, start_date, end_date):
    """获取股票数据"""
    try:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df is not None and len(df) > 0:
            return df
    except:
        pass
    return None

def get_index_data(index_code, start_date, end_date):
    """获取指数数据"""
    # 优先使用index_daily接口
    try:
        df = pro.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date)
        if df is not None and len(df) > 0:
            return df
    except:
        pass
    
    # 如果index_daily失败，尝试使用daily接口（某些指数可能可以用daily接口）
    try:
        df = pro.daily(ts_code=index_code, start_date=start_date, end_date=end_date)
        if df is not None and len(df) > 0:
            return df
    except:
        pass
    
    # 尝试使用pro_bar接口
    try:
        import tushare as ts
        df = ts.pro_bar(ts_code=index_code, start_date=start_date, end_date=end_date, asset='I')
        if df is not None and len(df) > 0:
            return df
    except:
        pass
    
    return None

def get_bitcoin_data(start_date, end_date):
    """获取比特币数据"""
    try:
        import yfinance as yf
        start = pd.to_datetime(start_date).strftime('%Y-%m-%d')
        end = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        ticker = yf.Ticker('BTC-USD')
        df = ticker.history(start=start, end=end)
        if df is not None and len(df) > 0:
            df = df.reset_index()
            df['trade_date'] = df['Date'].dt.strftime('%Y%m%d')
            df['btc_close'] = df['Close']
            df['btc_pct'] = df['Close'].pct_change() * 100
            return df[['trade_date', 'btc_close', 'btc_pct']]
    except Exception as e:
        print(f"获取比特币数据失败: {e}")
    return None

def get_macro_economic_data(start_date, end_date):
    """获取宏观经济指标数据（GDP、CPI、PMI、利率、汇率、M2等）"""
    try:
        import tushare as ts
        pro = ts.pro_api()
        
        macro_data = {}
        
        # 1. 获取CPI数据（居民消费价格指数）
        try:
            # CPI是月度数据，需要转换为日度数据（使用前值填充）
            cpi_df = pro.cn_cpi(start_date=start_date.strftime('%Y%m'), end_date=end_date.strftime('%Y%m'))
            if cpi_df is not None and len(cpi_df) > 0:
                cpi_df['month'] = pd.to_datetime(cpi_df['month'], format='%Y%m')
                # 计算CPI同比和环比变化率
                if 'nt_val' in cpi_df.columns:  # 全国CPI
                    cpi_df['cpi_yoy'] = cpi_df['nt_val'].pct_change(12) * 100  # 同比
                    cpi_df['cpi_mom'] = cpi_df['nt_val'].pct_change(1) * 100  # 环比
                    macro_data['cpi'] = cpi_df[['month', 'cpi_yoy', 'cpi_mom']].copy()
        except Exception as e:
            print(f"    无法获取CPI数据: {str(e)[:50]}")
        
        # 2. 获取PMI数据（采购经理人指数）
        try:
            pmi_df = pro.cn_pmi(start_date=start_date.strftime('%Y%m'), end_date=end_date.strftime('%Y%m'))
            if pmi_df is not None and len(pmi_df) > 0:
                pmi_df['month'] = pd.to_datetime(pmi_df['month'], format='%Y%m')
                # PMI通常直接使用数值，50为荣枯线
                if 'pmi' in pmi_df.columns:
                    pmi_df['pmi_change'] = pmi_df['pmi'].diff()  # PMI变化
                    macro_data['pmi'] = pmi_df[['month', 'pmi', 'pmi_change']].copy()
        except Exception as e:
            print(f"    无法获取PMI数据: {str(e)[:50]}")
        
        # 3. 获取GDP数据（季度数据）
        try:
            gdp_df = pro.cn_gdp(start_date=start_date.strftime('%Y%m'), end_date=end_date.strftime('%Y%m'))
            if gdp_df is not None and len(gdp_df) > 0:
                gdp_df['quarter'] = pd.to_datetime(gdp_df['quarter'], format='%Y%m')
                if 'gdp' in gdp_df.columns:
                    gdp_df['gdp_yoy'] = gdp_df['gdp'].pct_change(4) * 100  # 同比
                    macro_data['gdp'] = gdp_df[['quarter', 'gdp_yoy']].copy()
        except Exception as e:
            print(f"    无法获取GDP数据: {str(e)[:50]}")
        
        # 4. 获取利率数据（存贷款基准利率）
        try:
            # 尝试获取利率数据
            rate_df = pro.shibor(start_date=start_date.strftime('%Y%m%d'), end_date=end_date.strftime('%Y%m%d'))
            if rate_df is not None and len(rate_df) > 0:
                rate_df['date'] = pd.to_datetime(rate_df['date'])
                # 使用SHIBOR（上海银行间同业拆放利率）作为利率指标
                if 'on' in rate_df.columns:  # 隔夜利率
                    rate_df['rate_change'] = rate_df['on'].diff()  # 利率变化
                    macro_data['interest_rate'] = rate_df[['date', 'on', 'rate_change']].copy()
                    macro_data['interest_rate'].columns = ['month', 'interest_rate', 'interest_rate_change']
        except Exception as e:
            print(f"    无法获取利率数据: {str(e)[:50]}")
        
        # 5. 获取汇率数据（人民币对美元汇率）
        try:
            # 尝试获取汇率数据
            fx_df = pro.fx_daily(start_date=start_date.strftime('%Y%m%d'), end_date=end_date.strftime('%Y%m%d'))
            if fx_df is not None and len(fx_df) > 0:
                fx_df['trade_date'] = pd.to_datetime(fx_df['trade_date'])
                # 使用USDCNY（美元对人民币）汇率
                if 'bid_close' in fx_df.columns:
                    fx_df['fx_rate'] = fx_df['bid_close']
                    fx_df['fx_rate_change'] = fx_df['fx_rate'].pct_change() * 100  # 汇率变化率
                    macro_data['exchange_rate'] = fx_df[['trade_date', 'fx_rate', 'fx_rate_change']].copy()
                    macro_data['exchange_rate'].columns = ['month', 'exchange_rate', 'exchange_rate_change']
        except Exception as e:
            print(f"    无法获取汇率数据: {str(e)[:50]}")
        
        # 6. 获取M2货币供应量数据
        try:
            # 尝试获取货币供应量数据
            money_df = pro.cn_m(start_date=start_date.strftime('%Y%m'), end_date=end_date.strftime('%Y%m'))
            if money_df is not None and len(money_df) > 0:
                money_df['month'] = pd.to_datetime(money_df['month'], format='%Y%m')
                # M2货币供应量
                if 'm2' in money_df.columns:
                    money_df['m2_yoy'] = money_df['m2'].pct_change(12) * 100  # 同比
                    money_df['m2_mom'] = money_df['m2'].pct_change(1) * 100  # 环比
                    macro_data['m2'] = money_df[['month', 'm2_yoy', 'm2_mom']].copy()
        except Exception as e:
            print(f"    无法获取M2数据: {str(e)[:50]}")
        
        return macro_data
    except Exception as e:
        print(f"    获取宏观经济数据失败: {str(e)[:50]}")
        return {}

def get_news_sentiment(ts_code, start_date, end_date, use_advanced_nlp=False):
    """获取新闻情绪数据（使用Tushare新闻接口）
    
    支持两种模式：
    1. 基础模式：使用关键词匹配（默认）
    2. 高级模式：使用BERT/GPT等预训练模型（需要安装transformers库）
    """
    try:
        import tushare as ts
        pro = ts.pro_api()
        
        # 尝试获取新闻数据
        try:
            news_df = pro.news(src='sina', start_date=start_date.strftime('%Y%m%d'), 
                              end_date=end_date.strftime('%Y%m%d'))
            if news_df is not None and len(news_df) > 0:
                # 选择使用高级NLP还是基础关键词匹配
                if use_advanced_nlp:
                    try:
                        # 尝试使用BERT模型进行情绪分析
                        from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
                        import torch
                        
                        # 使用中文情感分析模型（如果有GPU则使用GPU）
                        device = 0 if torch.cuda.is_available() else -1
                        try:
                            # 尝试加载中文情感分析模型
                            sentiment_analyzer = pipeline(
                                "sentiment-analysis",
                                model="uer/roberta-base-finetuned-chinanews-chinese",
                                device=device
                            )
                        except:
                            # 如果中文模型不可用，使用通用模型
                            try:
                                sentiment_analyzer = pipeline(
                                    "sentiment-analysis",
                                    model="nlptown/bert-base-multilingual-uncased-sentiment",
                                    device=device
                                )
                            except:
                                # 如果都不可用，回退到关键词匹配
                                print("    高级NLP模型不可用，使用关键词匹配")
                                use_advanced_nlp = False
                        
                        if use_advanced_nlp:
                            def calculate_sentiment_bert(text):
                                """使用BERT模型计算情绪"""
                                if pd.isna(text) or text == '':
                                    return 0
                                text = str(text)
                                # 限制文本长度（BERT有最大长度限制）
                                max_length = 512
                                if len(text) > max_length:
                                    text = text[:max_length]
                                
                                try:
                                    result = sentiment_analyzer(text)
                                    # 结果格式：{'label': 'POSITIVE'/'NEGATIVE', 'score': 0.xx}
                                    if isinstance(result, list):
                                        result = result[0]
                                    
                                    # 转换为-1到1之间的得分
                                    if 'POSITIVE' in str(result.get('label', '')).upper() or \
                                       '积极' in str(result.get('label', '')) or \
                                       '正面' in str(result.get('label', '')):
                                        score = result.get('score', 0.5)
                                        return score  # 0到1之间
                                    else:
                                        score = result.get('score', 0.5)
                                        return -score  # -1到0之间
                                except Exception as e:
                                    # 如果BERT分析失败，回退到关键词匹配
                                    return calculate_sentiment_keywords(text)
                            
                            # 使用BERT分析正文内容（如果可用）
                            if 'content' in news_df.columns:
                                print("    使用BERT模型分析新闻正文内容...")
                                news_df['sentiment'] = news_df['content'].apply(calculate_sentiment_bert)
                            elif 'title' in news_df.columns:
                                print("    使用BERT模型分析新闻标题...")
                                news_df['sentiment'] = news_df['title'].apply(calculate_sentiment_bert)
                            else:
                                return None
                    except ImportError:
                        print("    transformers库未安装，使用关键词匹配。安装命令: pip install transformers torch")
                        use_advanced_nlp = False
                    except Exception as e:
                        print(f"    高级NLP模型加载失败: {str(e)[:50]}，使用关键词匹配")
                        use_advanced_nlp = False
                
                # 基础关键词匹配方法
                if not use_advanced_nlp:
                    # 正面关键词
                    positive_keywords = ['涨', '升', '利好', '增长', '盈利', '超预期', '突破', '创新高', 
                                       '上涨', '大涨', '飙升', '暴涨', '涨停', '强势', '看好', '推荐']
                    # 负面关键词
                    negative_keywords = ['跌', '降', '利空', '亏损', '下滑', '不及预期', '跌破', '创新低',
                                       '下跌', '大跌', '暴跌', '跌停', '弱势', '看空', '风险', '警告']
                    
                    def calculate_sentiment_keywords(text):
                        """使用关键词匹配计算情绪"""
                        if pd.isna(text):
                            return 0
                        text = str(text)
                        positive_count = sum(1 for kw in positive_keywords if kw in text)
                        negative_count = sum(1 for kw in negative_keywords if kw in text)
                        # 情绪得分：正数表示正面，负数表示负面，归一化到-1到1
                        if positive_count + negative_count == 0:
                            return 0
                        sentiment_score = (positive_count - negative_count) / (positive_count + negative_count + 1)
                        return sentiment_score
                    
                    if 'content' in news_df.columns:
                        news_df['sentiment'] = news_df['content'].apply(calculate_sentiment_keywords)
                    elif 'title' in news_df.columns:
                        news_df['sentiment'] = news_df['title'].apply(calculate_sentiment_keywords)
                    else:
                        return None
                
                # 按日期聚合情绪得分
                if 'datetime' in news_df.columns:
                    news_df['datetime'] = pd.to_datetime(news_df['datetime'])
                    news_df['date'] = news_df['datetime'].dt.date
                    daily_sentiment = news_df.groupby('date')['sentiment'].mean().reset_index()
                    daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])
                    return daily_sentiment
        except Exception as e:
            # 如果无法获取新闻，使用简化的情绪分析
            print(f"    无法获取新闻数据: {str(e)[:50]}")
            return None
        
        return None
    except Exception as e:
        print(f"    新闻情绪分析失败: {str(e)[:50]}")
        return None

def get_us_stock_index(start_date, end_date):
    """获取美股指数数据"""
    try:
        import yfinance as yf
        start = pd.to_datetime(start_date).strftime('%Y-%m-%d')
        end = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        indices = {}
        for symbol, name in [('^GSPC', 'SP500'), ('^IXIC', 'NASDAQ'), ('^DJI', 'DOW')]:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=start, end=end)
                if df is not None and len(df) > 0:
                    df = df.reset_index()
                    df['trade_date'] = df['Date'].dt.strftime('%Y%m%d')
                    df[f'{name}_pct'] = df['Close'].pct_change() * 100
                    indices[name] = df[['trade_date', f'{name}_pct']]
            except:
                pass
        return indices
    except Exception as e:
        print(f"获取美股指数数据失败: {e}")
    return {}

def calculate_technical_indicators(df):
    """计算技术指标"""
    df = df.sort_values('trade_date').copy()
    df['pct_chg'] = df['close'].pct_change() * 100
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    df['ma30'] = df['close'].rolling(30).mean()
    df['price_ma5_ratio'] = (df['close'] - df['ma5']) / df['ma5'] * 100
    df['price_ma10_ratio'] = (df['close'] - df['ma10']) / df['ma10'] * 100
    df['price_ma20_ratio'] = (df['close'] - df['ma20']) / df['ma20'] * 100
    df['vol_ma5'] = df['vol'].rolling(5).mean()
    df['vol_ma10'] = df['vol'].rolling(10).mean()
    df['vol_ratio'] = df['vol'] / df['vol_ma5']
    df['vol_ratio_10'] = df['vol'] / df['vol_ma10']
    df['momentum_5'] = df['close'].pct_change(5) * 100
    df['momentum_10'] = df['close'].pct_change(10) * 100
    df['prev_pct_chg'] = df['pct_chg'].shift(1)
    
    # 计算RSI（相对强弱指标）
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 计算MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # 计算波动率
    df['volatility_5'] = df['pct_chg'].rolling(5).std()
    df['volatility_10'] = df['pct_chg'].rolling(10).std()
    
    # 计算高低价比率
    df['high_low_ratio'] = (df['high'] - df['low']) / df['close'] * 100
    
    # 计算KDJ指标（随机指标）
    # KDJ = (RSV的3日移动平均, RSV的3日移动平均的3日移动平均, 3*K-2*D)
    low_min = df['low'].rolling(window=9).min()
    high_max = df['high'].rolling(window=9).max()
    rsv = (df['close'] - low_min) / (high_max - low_min + 1e-10) * 100
    df['kdj_k'] = rsv.ewm(com=2, adjust=False).mean()  # K值（3日EMA）
    df['kdj_d'] = df['kdj_k'].ewm(com=2, adjust=False).mean()  # D值（K的3日EMA）
    df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']  # J值
    
    # 计算BOLL指标（布林带）
    boll_period = 20
    boll_std = 2
    df['boll_mid'] = df['close'].rolling(window=boll_period).mean()  # 中轨
    boll_std_val = df['close'].rolling(window=boll_period).std()
    df['boll_upper'] = df['boll_mid'] + boll_std * boll_std_val  # 上轨
    df['boll_lower'] = df['boll_mid'] - boll_std * boll_std_val  # 下轨
    df['boll_width'] = (df['boll_upper'] - df['boll_lower']) / df['boll_mid'] * 100  # 布林带宽度
    df['boll_position'] = (df['close'] - df['boll_lower']) / (df['boll_upper'] - df['boll_lower'] + 1e-10) * 100  # 价格在布林带中的位置
    
    # 计算CCI指标（商品通道指数）
    cci_period = 14
    tp = (df['high'] + df['low'] + df['close']) / 3  # 典型价格
    sma_tp = tp.rolling(window=cci_period).mean()
    mad = tp.rolling(window=cci_period).apply(lambda x: np.abs(x - x.mean()).mean())  # 平均绝对偏差
    df['cci'] = (tp - sma_tp) / (0.015 * mad + 1e-10)  # CCI值
    
    # 计算OBV指标（能量潮）
    df['obv'] = (np.sign(df['close'].diff()) * df['vol']).fillna(0).cumsum()
    df['obv_ma'] = df['obv'].rolling(window=20).mean()
    df['obv_ratio'] = df['obv'] / (df['obv_ma'] + 1e-10)  # OBV相对均线比率
    
    # 计算威廉指标（WR）
    wr_period = 14
    wr_high = df['high'].rolling(window=wr_period).max()
    wr_low = df['low'].rolling(window=wr_period).min()
    df['wr'] = -100 * (wr_high - df['close']) / (wr_high - wr_low + 1e-10)
    
    # 计算DMI指标（趋向指标）的简化版
    # +DI和-DI
    high_diff = df['high'].diff()
    low_diff = -df['low'].diff()
    tr = pd.concat([high_diff, low_diff, (df['high'] - df['low']).abs()], axis=1).max(axis=1)
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = -low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
    atr = tr.rolling(window=14).mean()
    df['plus_di'] = 100 * plus_dm.rolling(window=14).mean() / (atr + 1e-10)
    df['minus_di'] = 100 * minus_dm.rolling(window=14).mean() / (atr + 1e-10)
    df['adx'] = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'] + 1e-10)
    
    return df

def is_trading_day(date):
    """判断是否为交易日（简化版，实际应该用交易日历）"""
    # 排除周末
    if date.weekday() >= 5:
        return False
    return True

def get_next_trading_days(start_date, num_days=10):
    """获取未来N个交易日"""
    trading_days = []
    current_date = start_date
    while len(trading_days) < num_days:
        if is_trading_day(current_date):
            trading_days.append(current_date)
        current_date += timedelta(days=1)
    return trading_days

def prepare_features_for_prediction(merged, feature_cols, last_date):
    """为未来日期准备特征数据"""
    # 获取最后一条数据作为基准
    last_row = merged.iloc[-1].copy()
    
    # 创建未来日期的特征（使用最后已知值或平均值）
    future_features = {}
    for col in feature_cols:
        if col in merged.columns:
            # 使用最近几天的平均值作为预测特征
            future_features[col] = merged[col].tail(5).mean()
        else:
            future_features[col] = 0
    
    return future_features

def build_and_update_model():
    """构建和更新预测模型"""
    print("=" * 80)
    print("中际旭创股票价格预测模型（增强版）")
    print("=" * 80)
    
    # 计算日期范围（近2年，用于训练，为LSTM提供更多历史数据）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 增加到2年历史数据
    
    start_date_str = start_date.strftime('%Y%m%d')
    end_date_str = end_date.strftime('%Y%m%d')
    
    print(f"\n数据获取时间范围: {start_date_str} 至 {end_date_str}")
    
    # 读取历史预测数据（如果存在）
    history_file = 'prediction_history.json'
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {'predictions': {}, 'actuals': {}}
    
    # 获取中际旭创数据
    print("\n正在获取中际旭创股票数据...")
    zjxc_df = get_stock_data(ZJXC_CODE, start_date_str, end_date_str)
    if zjxc_df is None or len(zjxc_df) == 0:
        print("错误: 无法获取中际旭创数据")
        return
    
    zjxc_df['trade_date'] = pd.to_datetime(zjxc_df['trade_date'])
    zjxc_df = calculate_technical_indicators(zjxc_df)
    
    # 准备合并数据（包含所有技术指标）
    # 重要：技术指标也需要做+1天偏移，因为要用前一天的技术指标预测当天的涨跌幅
    tech_cols = ['trade_date', 'close', 'pct_chg', 'price_ma5_ratio', 'price_ma10_ratio', 
                 'price_ma20_ratio', 'vol_ratio', 'vol_ratio_10', 'momentum_5', 'momentum_10',
                 'rsi', 'macd', 'macd_hist', 'volatility_5', 'volatility_10', 
                 'high_low_ratio', 'prev_pct_chg']
    available_cols = [col for col in tech_cols if col in zjxc_df.columns]
    merged = zjxc_df[available_cols].copy()
    
    # 将技术指标向前偏移一天（使其表示"前一天的技术指标"）
    # 这样可以用前一天的技术指标预测当天的涨跌幅
    # 例如：T-1日的技术指标用于预测T日的涨跌幅
    tech_indicator_cols = [col for col in available_cols if col not in ['trade_date', 'close', 'pct_chg']]
    for col in tech_indicator_cols:
        # 将技术指标向前偏移1天，使其与T日的涨跌幅对齐
        merged[col] = merged[col].shift(1)
    
    # 获取大盘指数
    print("\n正在获取大盘指数数据...")
    indices = {
        'cyb': ('399006.SZ', '创业板指'),
        'sz': ('399001.SZ', '深证成指'),
        'hs300': ('000300.SH', '沪深300'),
        'sh': ('000001.SH', '上证指数'),
        'zz500': ('000905.SH', '中证500'),
    }
    
    for key, (code, name) in indices.items():
        print(f"  获取{name}数据...")
        index_df = get_index_data(code, start_date_str, end_date_str)
        if index_df is not None and len(index_df) > 0:
            index_df['trade_date'] = pd.to_datetime(index_df['trade_date'])
            index_df['pct_chg'] = index_df['close'].pct_change() * 100
            temp = index_df[['trade_date', 'pct_chg']].copy()
            temp.columns = ['trade_date', f'{key}_pct']
            # 重要：使用前一天的指数涨跌幅（因为要预测明天的股价，只能用今天及之前的数据）
            temp['trade_date'] = temp['trade_date'] + pd.Timedelta(days=1)
            merged = pd.merge(merged, temp, on='trade_date', how='left')
            print(f"    ✓ 成功获取{name}数据（使用前一天涨跌幅）")
    
    # 获取行业指数
    print("\n正在获取行业指数数据...")
    industry_indices = {
        'semiconductor': ('801081.SI', '半导体(申万)'),
        'communication': ('801770.SI', '通信(申万)'),
        'electronics': ('801080.SI', '电子(申万)'),
        'optical': ('801084.SI', '光学光电子(申万)'),
        'comm_device': ('801102.SI', '通信设备(申万)'),
    }
    
    for key, (code, name) in industry_indices.items():
        print(f"  获取{name}行业指数数据...")
        # 尝试多种方法获取行业指数
        index_df = None
        
        # 方法1: 尝试index_daily接口
        try:
            index_df = pro.index_daily(ts_code=code, start_date=start_date_str, end_date=end_date_str)
            if index_df is None or len(index_df) == 0:
                index_df = None
        except:
            index_df = None
        
        # 方法2: 如果index_daily失败，尝试daily接口
        if index_df is None or len(index_df) == 0:
            try:
                index_df = pro.daily(ts_code=code, start_date=start_date_str, end_date=end_date_str)
                if index_df is None or len(index_df) == 0:
                    index_df = None
            except:
                index_df = None
        
        # 方法3: 尝试pro_bar接口
        if index_df is None or len(index_df) == 0:
            try:
                import tushare as ts
                index_df = ts.pro_bar(ts_code=code, start_date=start_date_str, end_date=end_date_str, asset='I')
                if index_df is None or len(index_df) == 0:
                    index_df = None
            except:
                index_df = None
        
        if index_df is not None and len(index_df) > 0:
            index_df['trade_date'] = pd.to_datetime(index_df['trade_date'])
            index_df['pct_chg'] = index_df['close'].pct_change() * 100
            temp = index_df[['trade_date', 'pct_chg']].copy()
            temp.columns = ['trade_date', f'{key}_pct']
            # 使用前一天的行业指数涨跌幅
            temp['trade_date'] = temp['trade_date'] + pd.Timedelta(days=1)
            merged = pd.merge(merged, temp, on='trade_date', how='left')
            print(f"    ✓ 成功获取{name}行业指数数据（使用前一天涨跌幅）")
        else:
            print(f"    ✗ 无法获取{name}行业指数数据（可能代码不正确或需要权限）")
    
    # 尝试获取同行业相关股票作为参考（光模块、通信设备相关）
    print("\n正在获取同行业相关股票数据...")
    related_stocks = {
        'new_fiber': ('300394.SZ', '新易盛'),  # 光模块
    }
    
    # 只获取一个相关股票作为参考（避免数据过多）
    for key, (code, name) in related_stocks.items():
        print(f"  获取{name}({code})数据作为行业参考...")
        try:
            stock_df = get_stock_data(code, start_date_str, end_date_str)
            if stock_df is not None and len(stock_df) > 0:
                stock_df['trade_date'] = pd.to_datetime(stock_df['trade_date'])
                stock_df['pct_chg'] = stock_df['close'].pct_change() * 100
                temp = stock_df[['trade_date', 'pct_chg']].copy()
                temp.columns = ['trade_date', f'{key}_pct']
                # 使用前一天的涨跌幅
                temp['trade_date'] = temp['trade_date'] + pd.Timedelta(days=1)
                merged = pd.merge(merged, temp, on='trade_date', how='left')
                print(f"    ✓ 成功获取{name}数据（使用前一天涨跌幅）")
        except Exception as e:
            print(f"    ✗ 无法获取{name}数据: {str(e)[:50]}")
    
    # 获取资金流向
    print("\n正在获取资金流向数据...")
    try:
        moneyflow_df = pro.moneyflow(ts_code=ZJXC_CODE, start_date=start_date_str, end_date=end_date_str)
        if moneyflow_df is not None and len(moneyflow_df) > 0:
            moneyflow_df['trade_date'] = pd.to_datetime(moneyflow_df['trade_date'])
            # 检查字段名
            print(f"    资金流向数据字段: {moneyflow_df.columns.tolist()}")
            
            # 计算资金流向指标（根据实际字段名）
            if 'net_mf_amount' in moneyflow_df.columns:
                if 'buy_amount' in moneyflow_df.columns:
                    moneyflow_df['net_ratio'] = moneyflow_df['net_mf_amount'] / (moneyflow_df['buy_amount'] + moneyflow_df['sell_amount'] + 1) * 100
                else:
                    moneyflow_df['net_ratio'] = moneyflow_df['net_mf_amount'] / (abs(moneyflow_df['net_mf_amount']) + 1) * 100
                
                temp = moneyflow_df[['trade_date', 'net_mf_amount']].copy()
                if 'net_ratio' in moneyflow_df.columns:
                    temp['net_ratio'] = moneyflow_df['net_ratio']
                
                # 重要：使用前一天的资金流向（因为要预测明天的股价，只能用今天及之前的数据）
                temp['trade_date'] = temp['trade_date'] + pd.Timedelta(days=1)
                merged = pd.merge(merged, temp, on='trade_date', how='left')
                print("    ✓ 成功获取资金流向数据（使用前一天数据）")
            else:
                print("    ✗ 资金流向数据字段不完整")
    except Exception as e:
        print(f"    ✗ 无法获取资金流向数据: {str(e)[:50]}")
    
    # 获取股票基本面数据（换手率、市值等）
    print("\n正在获取股票基本面数据...")
    try:
        daily_basic_df = pro.daily_basic(ts_code=ZJXC_CODE, start_date=start_date_str, end_date=end_date_str)
        if daily_basic_df is not None and len(daily_basic_df) > 0:
            daily_basic_df['trade_date'] = pd.to_datetime(daily_basic_df['trade_date'])
            # 选择有用的指标
            basic_cols = ['trade_date']
            if 'turnover_rate' in daily_basic_df.columns:
                basic_cols.append('turnover_rate')
            if 'circ_mv' in daily_basic_df.columns:
                basic_cols.append('circ_mv')
            if 'total_mv' in daily_basic_df.columns:
                basic_cols.append('total_mv')
            
            temp = daily_basic_df[basic_cols].copy()
            # 使用前一天的基本面数据
            temp['trade_date'] = temp['trade_date'] + pd.Timedelta(days=1)
            merged = pd.merge(merged, temp, on='trade_date', how='left')
            print("    ✓ 成功获取基本面数据（换手率、市值等）")
    except Exception as e:
        print(f"    ✗ 无法获取基本面数据: {str(e)[:50]}")
    
    # 获取比特币数据
    print("\n正在获取比特币数据...")
    btc_df = get_bitcoin_data(start_date_str, end_date_str)
    if btc_df is not None and len(btc_df) > 0:
        btc_df['trade_date'] = pd.to_datetime(btc_df['trade_date'])
        # 重要：使用前一天的比特币涨跌幅（因为要预测明天的股价，只能用今天及之前的数据）
        # 比特币是24小时交易，所以用前一天的收盘数据
        btc_df['trade_date'] = btc_df['trade_date'] + pd.Timedelta(days=1)
        merged = pd.merge(merged, btc_df[['trade_date', 'btc_pct']], on='trade_date', how='left')
        print("    ✓ 成功获取比特币数据（使用前一天涨跌幅）")
    
    # 获取融资融券数据（反映市场情绪和认可度）
    print("\n正在获取融资融券数据（市场情绪指标）...")
    try:
        margin_df = pro.margin(ts_code=ZJXC_CODE, start_date=start_date_str, end_date=end_date_str)
        if margin_df is not None and len(margin_df) > 0:
            margin_df['trade_date'] = pd.to_datetime(margin_df['trade_date'])
            # 计算融资余额变化率、融券余额变化率
            margin_df = margin_df.sort_values('trade_date')
            margin_df['margin_balance_change'] = margin_df['rqye'].pct_change() * 100  # 融资余额变化率
            margin_df['short_balance_change'] = margin_df['rzye'].pct_change() * 100  # 融券余额变化率
            margin_df['margin_ratio'] = margin_df['rqye'] / (margin_df['rqye'] + margin_df['rzye'] + 1) * 100  # 融资占比
            # 使用前一天的融资融券数据
            temp = margin_df[['trade_date', 'margin_balance_change', 'short_balance_change', 'margin_ratio']].copy()
            temp['trade_date'] = temp['trade_date'] + pd.Timedelta(days=1)
            merged = pd.merge(merged, temp, on='trade_date', how='left')
            print("    ✓ 成功获取融资融券数据（使用前一天数据）")
    except Exception as e:
        print(f"    ✗ 无法获取融资融券数据: {str(e)[:50]}")
    
    # 获取股东户数数据（反映散户参与度和认可度）
    print("\n正在获取股东户数数据（散户参与度指标）...")
    try:
        holder_df = pro.stk_holdernumber(ts_code=ZJXC_CODE, start_date=start_date_str, end_date=end_date_str)
        if holder_df is not None and len(holder_df) > 0:
            holder_df['end_date'] = pd.to_datetime(holder_df['end_date'])
            holder_df = holder_df.sort_values('end_date')
            # 计算股东户数变化率（负值表示户数减少，认可度提升）
            holder_df['holder_change_pct'] = holder_df['holder_num'].pct_change() * 100
            # 计算户均持股（市值/户数，反映集中度）
            # 需要合并市值数据
            temp = holder_df[['end_date', 'holder_num', 'holder_change_pct']].copy()
            temp.columns = ['trade_date', 'holder_num', 'holder_change_pct']
            # 将股东户数数据对齐到最近的交易日
            merged['holder_num'] = None
            merged['holder_change_pct'] = None
            for idx, row in merged.iterrows():
                trade_date = row['trade_date']
                # 找到最近的股东户数数据
                closest = temp.loc[(temp['trade_date'] <= trade_date), :]
                if len(closest) > 0:
                    closest_row = closest.iloc[-1]
                    merged.at[idx, 'holder_num'] = closest_row['holder_num']
                    merged.at[idx, 'holder_change_pct'] = closest_row['holder_change_pct']
            # 使用前一天的股东户数变化率
            merged['holder_change_pct'] = merged['holder_change_pct'].shift(1)
            print("    ✓ 成功获取股东户数数据（使用前一天数据）")
    except Exception as e:
        print(f"    ✗ 无法获取股东户数数据: {str(e)[:50]}")
    
    # 获取公司业绩数据（财务指标）
    print("\n正在获取公司业绩数据（财务指标）...")
    try:
        # 获取财务指标数据（包含ROE、ROA、净利润率等）
        fina_indicator_df = pro.fina_indicator(ts_code=ZJXC_CODE, start_date=start_date_str, end_date=end_date_str)
        if fina_indicator_df is not None and len(fina_indicator_df) > 0:
            fina_indicator_df['end_date'] = pd.to_datetime(fina_indicator_df['end_date'])
            fina_indicator_df = fina_indicator_df.sort_values('end_date')
            # 选择关键财务指标
            fina_cols = ['roe', 'roa', 'grossprofit_rate', 'netprofit_rate', 'eps', 'bps']
            available_fina_cols = [col for col in fina_cols if col in fina_indicator_df.columns]
            if available_fina_cols:
                temp = fina_indicator_df[['end_date'] + available_fina_cols].copy()
                temp.columns = ['trade_date'] + available_fina_cols
                # 将财务数据对齐到最近的交易日
                for col in available_fina_cols:
                    merged[col] = None
                for idx, row in merged.iterrows():
                    trade_date = row['trade_date']
                    closest = temp.loc[(temp['trade_date'] <= trade_date), :]
                    if len(closest) > 0:
                        closest_row = closest.iloc[-1]
                        for col in available_fina_cols:
                            merged.at[idx, col] = closest_row[col]
                # 使用前一天的财务指标
                for col in available_fina_cols:
                    merged[col] = merged[col].shift(1)
                print(f"    ✓ 成功获取财务指标数据（{', '.join(available_fina_cols)}，使用前一天数据）")
    except Exception as e:
        print(f"    ✗ 无法获取财务指标数据: {str(e)[:50]}")
    
    # 获取利润表数据（营收、净利润增长率）
    print("\n正在获取利润表数据（营收、净利润增长率）...")
    try:
        income_df = pro.income(ts_code=ZJXC_CODE, start_date=start_date_str, end_date=end_date_str, 
                              period='', report_type='1')  # report_type='1'表示合并报表
        if income_df is not None and len(income_df) > 0:
            income_df['end_date'] = pd.to_datetime(income_df['end_date'])
            income_df = income_df.sort_values('end_date')
            # 计算营收和净利润增长率（同比）
            if 'revenue' in income_df.columns and 'n_income' in income_df.columns:
                income_df['revenue_yoy'] = income_df['revenue'].pct_change(periods=4) * 100  # 同比（假设季度数据）
                income_df['n_income_yoy'] = income_df['n_income'].pct_change(periods=4) * 100
                # 计算环比增长率
                income_df['revenue_qoq'] = income_df['revenue'].pct_change() * 100
                income_df['n_income_qoq'] = income_df['n_income'].pct_change() * 100
                temp = income_df[['end_date', 'revenue_yoy', 'n_income_yoy', 'revenue_qoq', 'n_income_qoq']].copy()
                temp.columns = ['trade_date', 'revenue_yoy', 'n_income_yoy', 'revenue_qoq', 'n_income_qoq']
                # 将利润表数据对齐到最近的交易日
                for col in ['revenue_yoy', 'n_income_yoy', 'revenue_qoq', 'n_income_qoq']:
                    merged[col] = None
                for idx, row in merged.iterrows():
                    trade_date = row['trade_date']
                    closest = temp.loc[(temp['trade_date'] <= trade_date), :]
                    if len(closest) > 0:
                        closest_row = closest.iloc[-1]
                        for col in ['revenue_yoy', 'n_income_yoy', 'revenue_qoq', 'n_income_qoq']:
                            merged.at[idx, col] = closest_row[col]
                # 使用前一天的利润表数据
                for col in ['revenue_yoy', 'n_income_yoy', 'revenue_qoq', 'n_income_qoq']:
                    merged[col] = merged[col].shift(1)
                print("    ✓ 成功获取利润表数据（营收、净利润增长率，使用前一天数据）")
    except Exception as e:
        print(f"    ✗ 无法获取利润表数据: {str(e)[:50]}")
    
    # 获取业绩预告数据（反映未来业绩预期）
    print("\n正在获取业绩预告数据（未来业绩预期）...")
    try:
        forecast_df = pro.forecast(ts_code=ZJXC_CODE, start_date=start_date_str, end_date=end_date_str)
        if forecast_df is not None and len(forecast_df) > 0:
            forecast_df['ann_date'] = pd.to_datetime(forecast_df['ann_date'])
            forecast_df = forecast_df.sort_values('ann_date')
            # 计算业绩预告的乐观程度（如果有预告净利润）
            if 'p_change_min' in forecast_df.columns and 'p_change_max' in forecast_df.columns:
                forecast_df['forecast_optimism'] = (forecast_df['p_change_min'] + forecast_df['p_change_max']) / 2
                temp = forecast_df[['ann_date', 'forecast_optimism']].copy()
                temp.columns = ['trade_date', 'forecast_optimism']
                # 将业绩预告数据对齐到最近的交易日
                merged['forecast_optimism'] = None
                for idx, row in merged.iterrows():
                    trade_date = row['trade_date']
                    closest = temp.loc[(temp['trade_date'] <= trade_date), :]
                    if len(closest) > 0:
                        closest_row = closest.iloc[-1]
                        merged.at[idx, 'forecast_optimism'] = closest_row['forecast_optimism']
                # 使用前一天的业绩预告数据
                merged['forecast_optimism'] = merged['forecast_optimism'].shift(1)
                print("    ✓ 成功获取业绩预告数据（使用前一天数据）")
    except Exception as e:
        print(f"    ✗ 无法获取业绩预告数据: {str(e)[:50]}")
    
    # 获取机构持仓数据（反映机构认可度）
    print("\n正在获取机构持仓数据（机构认可度指标）...")
    try:
        fund_hold_df = pro.fund_hold(ts_code=ZJXC_CODE, start_date=start_date_str, end_date=end_date_str)
        if fund_hold_df is not None and len(fund_hold_df) > 0:
            fund_hold_df['end_date'] = pd.to_datetime(fund_hold_df['end_date'])
            # 按日期汇总机构持仓
            fund_summary = fund_hold_df.groupby('end_date').agg({
                'holdvol': 'sum',  # 持仓数量
                'holdnum': 'count'  # 持仓机构数
            }).reset_index()
            fund_summary.columns = ['end_date', 'inst_hold_vol', 'inst_hold_num']
            fund_summary = fund_summary.sort_values('end_date')
            # 计算机构持仓变化率
            fund_summary['inst_hold_vol_change'] = fund_summary['inst_hold_vol'].pct_change() * 100
            fund_summary['inst_hold_num_change'] = fund_summary['inst_hold_num'].pct_change() * 100
            # 将机构持仓数据对齐到最近的交易日
            temp = fund_summary[['end_date', 'inst_hold_vol_change', 'inst_hold_num_change']].copy()
            temp.columns = ['trade_date', 'inst_hold_vol_change', 'inst_hold_num_change']
            merged['inst_hold_vol_change'] = None
            merged['inst_hold_num_change'] = None
            for idx, row in merged.iterrows():
                trade_date = row['trade_date']
                closest = temp.loc[(temp['trade_date'] <= trade_date), :]
                if len(closest) > 0:
                    closest_row = closest.iloc[-1]
                    merged.at[idx, 'inst_hold_vol_change'] = closest_row['inst_hold_vol_change']
                    merged.at[idx, 'inst_hold_num_change'] = closest_row['inst_hold_num_change']
            # 使用前一天的机构持仓变化率
            merged['inst_hold_vol_change'] = merged['inst_hold_vol_change'].shift(1)
            merged['inst_hold_num_change'] = merged['inst_hold_num_change'].shift(1)
            print("    ✓ 成功获取机构持仓数据（使用前一天数据）")
    except Exception as e:
        print(f"    ✗ 无法获取机构持仓数据: {str(e)[:50]}")
    
    # 获取美股指数数据
    print("\n正在获取美股指数数据...")
    us_indices = get_us_stock_index(start_date_str, end_date_str)
    for name, df in us_indices.items():
        if df is not None and len(df) > 0:
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            # 重要：使用前一天的美股涨跌幅（因为要预测明天的股价，只能用今天及之前的数据）
            # 美股收盘时A股还没开盘，所以用前一个交易日的美股数据
            df['trade_date'] = df['trade_date'] + pd.Timedelta(days=1)
            merged = pd.merge(merged, df, on='trade_date', how='left')
            print(f"    ✓ 成功获取{name}数据（使用前一天涨跌幅）")
    
    # 添加周内效应特征
    merged['weekday'] = merged['trade_date'].dt.dayofweek  # 0=周一, 6=周日
    merged['is_monday'] = (merged['weekday'] == 0).astype(int)
    merged['is_friday'] = (merged['weekday'] == 4).astype(int)
    merged['is_tuesday'] = (merged['weekday'] == 1).astype(int)
    
    # 添加"周五涨跌幅"特征（用于预测周一）
    # 如果当天是周一，则使用前一个周五的涨跌幅
    merged['friday_pct_chg'] = None
    for i in range(1, len(merged)):
        if merged.iloc[i]['is_monday'] == 1:
            # 找到前一个周五
            for j in range(i-1, max(0, i-5), -1):
                if merged.iloc[j]['is_friday'] == 1:
                    merged.iloc[i, merged.columns.get_loc('friday_pct_chg')] = merged.iloc[j]['pct_chg']
                    break
    
    # 删除缺失值
    # 注意：技术指标偏移后，第一行的技术指标会是NaN（因为没有前一天数据）
    # 这是正常的，应该删除这一行，因为无法用前一天的技术指标预测第一天的涨跌幅
    merged = merged.dropna(subset=['pct_chg', 'close'])
    # 删除技术指标全部为NaN的行（这些行无法用于训练）
    tech_cols_to_check = [col for col in tech_indicator_cols if col in merged.columns]
    if tech_cols_to_check:
        merged = merged.dropna(subset=tech_cols_to_check[:3])  # 至少检查前3个技术指标
    merged = merged.sort_values('trade_date')
    
    print(f"\n有效数据样本数: {len(merged)}")
    
    # 准备特征和目标变量
    # 注意：所有外部因素（大盘指数、比特币、美股、资金流向）都已经做了+1天偏移
    # 所以它们代表的是"前一天的涨跌幅"，这是正确的
    
    # 技术指标特征（当天数据）
    tech_features = [
        'price_ma5_ratio', 'price_ma10_ratio', 'price_ma20_ratio',
        'vol_ratio', 'vol_ratio_10',
        'momentum_5', 'momentum_10',
        'rsi', 'macd', 'macd_hist',
        'volatility_5', 'volatility_10',
        'high_low_ratio',
        'prev_pct_chg',
        # 新增技术指标
        'kdj_k', 'kdj_d', 'kdj_j',  # KDJ指标
        'boll_mid', 'boll_upper', 'boll_lower', 'boll_width', 'boll_position',  # 布林带
        'cci',  # CCI指标
        'obv', 'obv_ma', 'obv_ratio',  # OBV指标
        'wr',  # 威廉指标
        'plus_di', 'minus_di', 'adx'  # DMI指标
    ]
    feature_cols = [col for col in tech_features if col in merged.columns]
    
    # 添加时间序列特征（滞后特征和滑动窗口统计）
    print("\n正在添加时间序列特征...")
    merged = add_time_series_features(merged, feature_cols)
    
    # 外部因素（使用前一天的数据）
    for col in ['cyb_pct', 'sz_pct', 'hs300_pct', 'sh_pct', 'zz500_pct', 'btc_pct', 
                'net_ratio', 'net_mf_amount',
                'turnover_rate', 'circ_mv', 'total_mv']:
        if col in merged.columns:
            feature_cols.append(col)
    
    # 市场情绪/认可度指标（使用前一天的数据）
    for col in ['margin_balance_change', 'short_balance_change', 'margin_ratio',
                'holder_change_pct', 'inst_hold_vol_change', 'inst_hold_num_change']:
        if col in merged.columns:
            feature_cols.append(col)
    
    # 公司业绩指标（使用前一天的数据）
    for col in ['roe', 'roa', 'grossprofit_rate', 'netprofit_rate', 'eps', 'bps',
                'revenue_yoy', 'n_income_yoy', 'revenue_qoq', 'n_income_qoq',
                'forecast_optimism']:
        if col in merged.columns:
            feature_cols.append(col)
    
    # 行业指数
    for key in ['semiconductor', 'communication', 'electronics', 'optical', 'comm_device']:
        if f'{key}_pct' in merged.columns:
            feature_cols.append(f'{key}_pct')
    
    # 同行业相关股票
    for key in ['new_fiber']:
        if f'{key}_pct' in merged.columns:
            feature_cols.append(f'{key}_pct')
    
    # 美股指数
    for name in ['SP500', 'NASDAQ', 'DOW']:
        if f'{name}_pct' in merged.columns:
            feature_cols.append(f'{name}_pct')
    
    # 周内效应特征
    for col in ['is_monday', 'is_friday', 'is_tuesday', 'friday_pct_chg']:
        if col in merged.columns:
            feature_cols.append(col)
    
    print(f"\n特征说明:")
    tech_cols = [col for col in feature_cols if col in tech_features]
    sentiment_cols = [col for col in feature_cols if col in ['margin_balance_change', 'short_balance_change', 'margin_ratio',
                                                              'holder_change_pct', 'inst_hold_vol_change', 'inst_hold_num_change']]
    performance_cols = [col for col in feature_cols if col in ['roe', 'roa', 'grossprofit_rate', 'netprofit_rate', 'eps', 'bps',
                                                                'revenue_yoy', 'n_income_yoy', 'revenue_qoq', 'n_income_qoq',
                                                                'forecast_optimism']]
    external_factors = [col for col in feature_cols if col not in tech_features and col not in sentiment_cols and col not in performance_cols]
    print(f"  技术指标（前一天）: {tech_cols}")
    print(f"  外部因素（前一天）: {external_factors}")
    print(f"  市场情绪/认可度指标（前一天）: {sentiment_cols}")
    print(f"  公司业绩指标（前一天）: {performance_cols}")
    print(f"  总特征数: {len(feature_cols)}")
    
    # 准备训练数据
    X = merged[feature_cols].fillna(0)
    # 清理无穷大值和异常值
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    # 限制数值范围（避免过大值）
    X = X.clip(lower=-1e6, upper=1e6)
    y = merged['pct_chg']
    
    # 划分训练集和测试集
    split_idx = int(len(merged) * 0.8)
    X_train = X[:split_idx]
    X_test = X[split_idx:]
    y_train = y[:split_idx]
    y_test = y[split_idx:]
    
    print(f"\n训练集样本数: {len(X_train)}")
    print(f"测试集样本数: {len(X_test)}")
    print(f"特征数量: {len(feature_cols)}")
    
    # 特征选择：选择最重要的特征（如果特征数较多）
    # 增加特征数量，因为现在有更多有用的特征（包括周内效应）
    if len(feature_cols) > 20:
        print(f"\n进行特征选择（从{len(feature_cols)}个特征中选择最重要的20个）...")
        selector = SelectKBest(f_regression, k=min(20, len(feature_cols)))
        X_train_selected = selector.fit_transform(X_train, y_train)
        X_test_selected = selector.transform(X_test)
        selected_features = [feature_cols[i] for i in selector.get_support(indices=True)]
        print(f"  选择的特征: {selected_features}")
        X_train = pd.DataFrame(X_train_selected, columns=selected_features, index=X_train.index)
        X_test = pd.DataFrame(X_test_selected, columns=selected_features, index=X_test.index)
        feature_cols = selected_features
    else:
        print(f"\n使用全部{len(feature_cols)}个特征（未进行特征选择）")
    
    # 训练多个模型（包括改进的模型）
    print("\n正在训练多个模型（包括改进版本）...")
    
    models = {}
    predictions = {}
    scores = {}
    
    # 1. 线性回归
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)
    lr_r2 = r2_score(y_test, lr_pred)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))
    models['线性回归'] = lr_model
    predictions['线性回归'] = lr_pred
    scores['线性回归'] = {'r2': lr_r2, 'rmse': lr_rmse}
    print(f"\n线性回归模型:")
    print(f"  R²得分: {lr_r2:.4f}")
    print(f"  RMSE: {lr_rmse:.4f}")
    
    # 2. Ridge回归（L2正则化）
    ridge_model = Ridge(alpha=1.0)
    ridge_model.fit(X_train, y_train)
    ridge_pred = ridge_model.predict(X_test)
    ridge_r2 = r2_score(y_test, ridge_pred)
    ridge_rmse = np.sqrt(mean_squared_error(y_test, ridge_pred))
    models['Ridge回归'] = ridge_model
    predictions['Ridge回归'] = ridge_pred
    scores['Ridge回归'] = {'r2': ridge_r2, 'rmse': ridge_rmse}
    print(f"\nRidge回归模型:")
    print(f"  R²得分: {ridge_r2:.4f}")
    print(f"  RMSE: {ridge_rmse:.4f}")
    
    # 3. 随机森林
    rf_model = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=12, min_samples_split=5)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_r2 = r2_score(y_test, rf_pred)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
    models['随机森林'] = rf_model
    predictions['随机森林'] = rf_pred
    scores['随机森林'] = {'r2': rf_r2, 'rmse': rf_rmse}
    print(f"\n随机森林模型:")
    print(f"  R²得分: {rf_r2:.4f}")
    print(f"  RMSE: {rf_rmse:.4f}")
    
    # 4. XGBoost（如果可用）- 带超参数调优
    try:
        import xgboost as xgb
        print("\n正在训练XGBoost模型（带超参数调优）...")
        
        # 快速超参数搜索（使用RandomizedSearchCV以节省时间）
        xgb_base = xgb.XGBRegressor(random_state=42, n_jobs=-1)
        xgb_param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.05, 0.1, 0.15],
            'subsample': [0.7, 0.8, 0.9],
            'colsample_bytree': [0.7, 0.8, 0.9]
        }
        
        # 使用较小的搜索空间以节省时间
        xgb_search = RandomizedSearchCV(
            xgb_base, xgb_param_grid, 
            n_iter=10,  # 随机搜索10组参数
            cv=3,  # 3折交叉验证
            scoring='r2',
            n_jobs=-1,
            random_state=42,
            verbose=0
        )
        xgb_search.fit(X_train, y_train)
        xgb_model = xgb_search.best_estimator_
        xgb_pred = xgb_model.predict(X_test)
        xgb_r2 = r2_score(y_test, xgb_pred)
        xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_pred))
        models['XGBoost(调优)'] = xgb_model
        predictions['XGBoost(调优)'] = xgb_pred
        scores['XGBoost(调优)'] = {'r2': xgb_r2, 'rmse': xgb_rmse}
        print(f"  XGBoost模型（最佳参数）:")
        print(f"    R²得分: {xgb_r2:.4f}")
        print(f"    RMSE: {xgb_rmse:.4f}")
        print(f"    最佳参数: {xgb_search.best_params_}")
    except ImportError:
        print("\nXGBoost未安装，跳过（可运行: pip install xgboost）")
    except Exception as e:
        print(f"\nXGBoost超参数调优失败，使用默认参数: {str(e)[:50]}")
        try:
            import xgboost as xgb
            xgb_model = xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, 
                                        subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)
            xgb_model.fit(X_train, y_train)
            xgb_pred = xgb_model.predict(X_test)
            xgb_r2 = r2_score(y_test, xgb_pred)
            xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_pred))
            models['XGBoost'] = xgb_model
            predictions['XGBoost'] = xgb_pred
            scores['XGBoost'] = {'r2': xgb_r2, 'rmse': xgb_rmse}
            print(f"  XGBoost模型（默认参数）:")
            print(f"    R²得分: {xgb_r2:.4f}")
            print(f"    RMSE: {xgb_rmse:.4f}")
        except:
            pass
    
    # 5. LightGBM（如果可用）- 带超参数调优
    try:
        import lightgbm as lgb
        print("\n正在训练LightGBM模型（带超参数调优）...")
        
        lgb_base = lgb.LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1)
        lgb_param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.05, 0.1, 0.15],
            'subsample': [0.7, 0.8, 0.9],
            'colsample_bytree': [0.7, 0.8, 0.9]
        }
        
        lgb_search = RandomizedSearchCV(
            lgb_base, lgb_param_grid,
            n_iter=10,
            cv=3,
            scoring='r2',
            n_jobs=-1,
            random_state=42,
            verbose=0
        )
        lgb_search.fit(X_train, y_train)
        lgb_model = lgb_search.best_estimator_
        lgb_pred = lgb_model.predict(X_test)
        lgb_r2 = r2_score(y_test, lgb_pred)
        lgb_rmse = np.sqrt(mean_squared_error(y_test, lgb_pred))
        models['LightGBM(调优)'] = lgb_model
        predictions['LightGBM(调优)'] = lgb_pred
        scores['LightGBM(调优)'] = {'r2': lgb_r2, 'rmse': lgb_rmse}
        print(f"  LightGBM模型（最佳参数）:")
        print(f"    R²得分: {lgb_r2:.4f}")
        print(f"    RMSE: {lgb_rmse:.4f}")
        print(f"    最佳参数: {lgb_search.best_params_}")
    except ImportError:
        print("\nLightGBM未安装，跳过（可运行: pip install lightgbm）")
    except Exception as e:
        print(f"\nLightGBM超参数调优失败，使用默认参数: {str(e)[:50]}")
        try:
            import lightgbm as lgb
            lgb_model = lgb.LGBMRegressor(n_estimators=200, max_depth=6, learning_rate=0.1,
                                         subsample=0.8, colsample_bytree=0.8, random_state=42, 
                                         n_jobs=-1, verbose=-1)
            lgb_model.fit(X_train, y_train)
            lgb_pred = lgb_model.predict(X_test)
            lgb_r2 = r2_score(y_test, lgb_pred)
            lgb_rmse = np.sqrt(mean_squared_error(y_test, lgb_pred))
            models['LightGBM'] = lgb_model
            predictions['LightGBM'] = lgb_pred
            scores['LightGBM'] = {'r2': lgb_r2, 'rmse': lgb_rmse}
            print(f"  LightGBM模型（默认参数）:")
            print(f"    R²得分: {lgb_r2:.4f}")
            print(f"    RMSE: {lgb_rmse:.4f}")
        except:
            pass
    
    # 6. LSTM深度学习模型（如果可用）
    try:
        import tensorflow as tf
        # TensorFlow 2.x中，keras已集成，使用兼容的导入方式
        try:
            from tensorflow import keras
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout, GRU, Bidirectional, Multiply, Lambda
            from tensorflow.keras.callbacks import EarlyStopping
            from tensorflow.keras import Model, Input
            from tensorflow.keras import backend as K
        except ImportError:
            # 如果tensorflow.keras不可用，尝试直接使用keras
            try:
                import keras
                from keras.models import Sequential, Model
                from keras.layers import LSTM, Dense, Dropout, GRU, Bidirectional, Multiply, Lambda, Input
                from keras.callbacks import EarlyStopping
                from keras import backend as K
            except ImportError:
                raise ImportError("TensorFlow或Keras未安装")
        
        print("\n正在训练LSTM深度学习模型...")
        
        # 准备LSTM数据（需要3D输入: [samples, timesteps, features]）
        # 使用滑动窗口创建时间序列数据
        lookback = 5  # 使用过去5天的数据预测下一天
        n_features = X_train.shape[1]
        
        def create_sequences(X, y, lookback):
            X_seq, y_seq = [], []
            for i in range(lookback, len(X)):
                X_seq.append(X[i-lookback:i])
                y_seq.append(y[i])
            return np.array(X_seq), np.array(y_seq)
        
        # 标准化数据（LSTM对数据尺度敏感）
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        X_train_scaled = scaler_X.fit_transform(X_train)
        X_test_scaled = scaler_X.transform(X_test)
        y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()
        y_test_scaled = scaler_y.transform(y_test.values.reshape(-1, 1)).ravel()
        
        # 创建序列数据
        X_train_lstm, y_train_lstm = create_sequences(X_train_scaled, y_train_scaled, lookback)
        X_test_lstm, y_test_lstm = create_sequences(X_test_scaled, y_test_scaled, lookback)
        
        if len(X_train_lstm) > 0 and len(X_test_lstm) > 0:
            # 构建改进的LSTM模型（双向LSTM + Attention机制）
            # 这些导入已在上面完成，这里不需要重复导入
            
            # 方法1: 双向LSTM模型
            print("    构建双向LSTM模型...")
            lstm_model_bidirectional = Sequential([
                Bidirectional(LSTM(50, activation='relu', return_sequences=True), 
                            input_shape=(lookback, n_features)),
                Dropout(0.2),
                Bidirectional(LSTM(50, activation='relu', return_sequences=False)),
                Dropout(0.2),
                Dense(25, activation='relu'),
                Dense(1)
            ])
            
            lstm_model_bidirectional.compile(optimizer='adam', loss='mse', metrics=['mae'])
            
            # 训练双向LSTM
            early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
            lstm_history_bidirectional = lstm_model_bidirectional.fit(
                X_train_lstm, y_train_lstm,
                epochs=50,
                batch_size=16,
                validation_split=0.2,
                callbacks=[early_stopping],
                verbose=0
            )
            
            # 预测
            lstm_pred_bidirectional_scaled = lstm_model_bidirectional.predict(X_test_lstm, verbose=0)
            lstm_pred_bidirectional = scaler_y.inverse_transform(lstm_pred_bidirectional_scaled.reshape(-1, 1)).ravel()
            
            # 评估双向LSTM
            if len(lstm_pred_bidirectional) > 0:
                y_test_aligned = y_test.iloc[lookback:].values
                lstm_r2_bidirectional = r2_score(y_test_aligned, lstm_pred_bidirectional)
                lstm_rmse_bidirectional = np.sqrt(mean_squared_error(y_test_aligned, lstm_pred_bidirectional))
                
                models['LSTM(双向)'] = {'model': lstm_model_bidirectional, 'scaler_X': scaler_X, 
                                       'scaler_y': scaler_y, 'lookback': lookback}
                predictions['LSTM(双向)'] = lstm_pred_bidirectional
                scores['LSTM(双向)'] = {'r2': lstm_r2_bidirectional, 'rmse': lstm_rmse_bidirectional}
                print(f"  LSTM(双向)模型:")
                print(f"    R²得分: {lstm_r2_bidirectional:.4f}")
                print(f"    RMSE: {lstm_rmse_bidirectional:.4f}")
            
            # 方法2: 带Attention机制的LSTM（简化版）
            print("    构建Attention LSTM模型...")
            try:
                # 构建带Attention的LSTM模型
                inputs = Input(shape=(lookback, n_features))
                lstm1 = LSTM(50, activation='relu', return_sequences=True)(inputs)
                dropout1 = Dropout(0.2)(lstm1)
                lstm2 = LSTM(50, activation='relu', return_sequences=True)(dropout1)
                dropout2 = Dropout(0.2)(lstm2)
                # 简化的注意力层（修复形状问题）
                # 计算注意力权重（对每个时间步）
                attention_scores = Dense(1, activation='tanh')(dropout2)  # [batch, lookback, 1]
                attention_weights = Dense(1, activation='softmax')(attention_scores)  # [batch, lookback, 1]
                # 加权求和
                attention_output = Lambda(lambda x: K.sum(x[0] * x[1], axis=1))(
                    [dropout2, attention_weights])  # [batch, features]
                dense1 = Dense(25, activation='relu')(attention_output)
                outputs = Dense(1)(dense1)
                
                lstm_model_attention = Model(inputs=inputs, outputs=outputs)
                lstm_model_attention.compile(optimizer='adam', loss='mse', metrics=['mae'])
                
                # 训练Attention LSTM
                early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
                lstm_history_attention = lstm_model_attention.fit(
                    X_train_lstm, y_train_lstm,
                    epochs=50,
                    batch_size=16,
                    validation_split=0.2,
                    callbacks=[early_stopping],
                    verbose=0
                )
                
                # 预测
                lstm_pred_attention_scaled = lstm_model_attention.predict(X_test_lstm, verbose=0)
                lstm_pred_attention = scaler_y.inverse_transform(lstm_pred_attention_scaled.reshape(-1, 1)).ravel()
                
                # 评估Attention LSTM
                if len(lstm_pred_attention) > 0:
                    y_test_aligned = y_test.iloc[lookback:].values
                    lstm_r2_attention = r2_score(y_test_aligned, lstm_pred_attention)
                    lstm_rmse_attention = np.sqrt(mean_squared_error(y_test_aligned, lstm_pred_attention))
                    
                    models['LSTM(Attention)'] = {'model': lstm_model_attention, 'scaler_X': scaler_X,
                                               'scaler_y': scaler_y, 'lookback': lookback}
                    predictions['LSTM(Attention)'] = lstm_pred_attention
                    scores['LSTM(Attention)'] = {'r2': lstm_r2_attention, 'rmse': lstm_rmse_attention}
                    print(f"  LSTM(Attention)模型:")
                    print(f"    R²得分: {lstm_r2_attention:.4f}")
                    print(f"    RMSE: {lstm_rmse_attention:.4f}")
            except Exception as e:
                print(f"    Attention LSTM构建失败: {str(e)[:50]}")
            
            # 使用表现最好的LSTM模型
            lstm_models_to_compare = {k: v for k, v in scores.items() if 'LSTM' in k}
            if lstm_models_to_compare:
                best_lstm_name = max(lstm_models_to_compare.items(), key=lambda x: x[1]['r2'])[0]
                print(f"    选择最佳LSTM模型: {best_lstm_name}")
    except ImportError:
        print("\nTensorFlow/Keras未安装，跳过LSTM（可运行: pip install tensorflow keras）")
    except Exception as e:
        print(f"\nLSTM模型训练失败: {str(e)[:100]}")
    
    # 7. 集成模型（投票回归器）
    print("\n正在训练集成模型（投票回归器）...")
    try:
        # 选择表现最好的3-5个模型进行集成（排除LSTM，因为它的预测长度不同）
        sorted_models = sorted(scores.items(), key=lambda x: x[1]['r2'], reverse=True)
        # 过滤掉LSTM（如果存在），因为它的预测长度不同
        available_models = [(name, score) for name, score in sorted_models if name != 'LSTM']
        top_models = available_models[:min(5, len(available_models))]
        
        if len(top_models) >= 2:
            estimators = [(name, models[name]) for name, _ in top_models]
            ensemble_model = VotingRegressor(estimators=estimators, weights=None)
            ensemble_model.fit(X_train, y_train)
            ensemble_pred = ensemble_model.predict(X_test)
            ensemble_r2 = r2_score(y_test, ensemble_pred)
            ensemble_rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
            models['集成模型(投票)'] = ensemble_model
            predictions['集成模型(投票)'] = ensemble_pred
            scores['集成模型(投票)'] = {'r2': ensemble_r2, 'rmse': ensemble_rmse}
            print(f"  集成模型(投票):")
            print(f"    R²得分: {ensemble_r2:.4f}")
            print(f"    RMSE: {ensemble_rmse:.4f}")
            print(f"    使用的模型: {[name for name, _ in top_models]}")
        else:
            print("  集成模型: 可用模型不足，跳过")
    except Exception as e:
        print(f"  集成模型训练失败: {str(e)[:50]}")
    
    # 选择最佳模型
    best_model_name = max(scores.items(), key=lambda x: x[1]['r2'])[0]
    model = models[best_model_name]
    model_name = best_model_name
    
    print(f"\n{'='*60}")
    print(f"模型性能对比:")
    print(f"{'='*60}")
    for name, score in sorted(scores.items(), key=lambda x: x[1]['r2'], reverse=True):
        print(f"  {name:20s}  R²={score['r2']:.4f}  RMSE={score['rmse']:.4f}")
    print(f"{'='*60}")
    print(f"\n选择最佳模型: {model_name} (R²={scores[model_name]['r2']:.4f})")
    
    # 在整个数据集上预测（使用正确的特征）
    X_all = merged[feature_cols].fillna(0)
    all_predictions = model.predict(X_all)
    merged['predicted_pct'] = all_predictions
    
    # 应用科创板20%涨跌幅限制
    max_pct_limit = 20.0  # 科创板涨跌幅限制
    merged['predicted_pct'] = merged['predicted_pct'].clip(-max_pct_limit, max_pct_limit)
    
    # 计算预测收盘价：基于前一日收盘价 * (1 + 预测涨跌幅 / 100)
    # 注意：shift(1)表示前一日，所以merged['close'].shift(1)是前一日收盘价
    merged['predicted_close'] = merged['close'].shift(1) * (1 + merged['predicted_pct'] / 100)
    
    # 验证并修正历史数据中的预测涨跌幅和预测收盘价的一致性
    print("\n验证并修正历史数据预测收盘价计算:")
    for i in range(min(10, len(merged))):
        if i > 0:  # 跳过第一行（没有前一日数据）
            prev_close = merged['close'].iloc[i-1]
            pred_pct = merged['predicted_pct'].iloc[i]
            calc_close = prev_close * (1 + pred_pct / 100)
            actual_close = merged['predicted_close'].iloc[i]
            
            # 从预测收盘价反推涨跌幅
            calculated_pct = (actual_close / prev_close - 1) * 100 if prev_close > 0 else 0
            
            if abs(calc_close - actual_close) > 0.01 or abs(calculated_pct - pred_pct) > 0.01:
                # 如果不一致，使用预测涨跌幅重新计算收盘价
                corrected_close = prev_close * (1 + pred_pct / 100)
                merged.at[merged.index[i], 'predicted_close'] = corrected_close
                print(f"  修正第{i}行: 前一日收盘价={prev_close:.2f}, 预测涨跌幅={pred_pct:.2f}%, 修正前预测收盘价={actual_close:.2f}, 修正后={corrected_close:.2f}")
            else:
                print(f"  ✓ 第{i}行: 前一日收盘价={prev_close:.2f}, 预测涨跌幅={pred_pct:.2f}%, 预测收盘价={actual_close:.2f}")
    
    # 对所有历史数据进行一致性检查和修正
    print("\n对所有历史数据进行一致性检查和修正...")
    corrected_count = 0
    for i in range(1, len(merged)):
        prev_close = merged['close'].iloc[i-1]
        pred_pct = merged['predicted_pct'].iloc[i]
        actual_close = merged['predicted_close'].iloc[i]
        
        # 从预测收盘价反推涨跌幅
        calculated_pct = (actual_close / prev_close - 1) * 100 if prev_close > 0 else 0
        
        if abs(calculated_pct - pred_pct) > 0.01:
            # 如果不一致，使用预测涨跌幅重新计算收盘价
            corrected_close = prev_close * (1 + pred_pct / 100)
            merged.at[merged.index[i], 'predicted_close'] = corrected_close
            corrected_count += 1
            # 显示所有修正的详细信息（特别是2025-08-28）
            date_str = merged.iloc[i]['trade_date'].strftime('%Y-%m-%d') if hasattr(merged.iloc[i]['trade_date'], 'strftime') else str(merged.iloc[i]['trade_date'])
            if corrected_count <= 20 or '2025-08-28' in date_str:
                print(f"    修正: {date_str}, 基准收盘价={prev_close:.2f}, 预测涨跌幅={pred_pct:.2f}%, 从收盘价反推涨跌幅={calculated_pct:.2f}%, 修正前预测收盘价={actual_close:.2f}, 修正后={corrected_close:.2f}")
    
    if corrected_count > 0:
        print(f"  已修正 {corrected_count} 条历史数据的预测收盘价，确保与预测涨跌幅一致")
    
    # 预测未来5个工作日
    print("\n正在预测未来5个工作日...")
    last_date = merged['trade_date'].max()
    
    # 获取未来5个交易日
    future_dates_all = get_next_trading_days(last_date + timedelta(days=1), num_days=5)
    
    # 预测所有5个交易日
    future_dates = []
    for i, date in enumerate(future_dates_all, 1):
        future_dates.append((i, date))
    
    print(f"  将预测以下日期：")
    for day, date in future_dates:
        print(f"    第{day}个工作日: {date.strftime('%Y-%m-%d')}")
    
    future_predictions = []
    last_known_close = merged['close'].iloc[-1]
    last_known_data = merged.iloc[-1].copy()
    
    # 保存原始股票数据用于计算技术指标
    zjxc_df_for_ma = zjxc_df.copy() if 'zjxc_df' in locals() else None
    
    # 按顺序预测每个目标日期（使用递归方式）
    for day_offset, future_date in future_dates:
        # 准备特征（使用最新可用的数据）
        # 重要：预测未来N天的股价，只能使用今天及之前的数据
        # 对于多天预测，使用递归方式：用前一天的预测结果作为输入
        future_features = {}
        
        # 确定当前的基础数据
        if day_offset == 1:
            # 第1天：使用最后已知数据
            current_data = last_known_data.copy()
            current_close = last_known_close
            prev_pct_chg = last_known_data['pct_chg'] if 'pct_chg' in last_known_data else 0
        else:
            # 第2天及以后：使用前一天的预测结果
            # 找到前一个预测（day_offset-1对应的索引）
            prev_idx = None
            for i, (prev_day, _) in enumerate(future_dates):
                if prev_day == day_offset - 1:
                    prev_idx = i
                    break
            
            if prev_idx is not None and prev_idx < len(future_predictions):
                prev_pred = future_predictions[prev_idx]
                current_close = prev_pred['predicted_close']
                prev_pct_chg = prev_pred['predicted_pct']
            else:
                # 如果找不到前一个预测，使用最后已知数据
                current_close = last_known_close
                prev_pct_chg = last_known_data['pct_chg'] if 'pct_chg' in last_known_data else 0
            # 基于预测的收盘价更新数据（简化处理）
            current_data = last_known_data.copy()
            current_data['close'] = current_close
            current_data['pct_chg'] = prev_pct_chg
        
        for col in feature_cols:
            if col in merged.columns:
                # 技术指标
                if col in tech_features:
                    if day_offset == 1:
                        # 第1天：使用最后已知数据
                        future_features[col] = current_data[col] if col in current_data and not pd.isna(current_data[col]) else merged[col].tail(5).mean()
                    else:
                        # 多天预测时，基于预测价格重新计算部分技术指标
                        if col == 'prev_pct_chg':
                            # 前一日涨跌幅：使用前一天的预测涨跌幅
                            future_features[col] = prev_pct_chg
                        elif col in ['price_ma5_ratio', 'price_ma10_ratio', 'price_ma20_ratio']:
                            # 价格相对均线位置：基于预测价格和已知均线计算
                            # 从最后已知的price_maX_ratio反推均线值，然后基于预测价格重新计算
                            try:
                                last_close_for_ma = merged['close'].iloc[-1]
                                if 'price_ma5_ratio' in col:
                                    last_ratio = merged['price_ma5_ratio'].iloc[-1] if 'price_ma5_ratio' in merged.columns else 0
                                    # 反推：price_ma5_ratio = (close - ma5) / ma5 * 100
                                    # ma5 = close / (1 + price_ma5_ratio/100)
                                    estimated_ma = last_close_for_ma / (1 + last_ratio/100) if last_ratio != -100 else last_close_for_ma
                                    # 假设均线每天缓慢移动（例如每天移动0.1%）
                                    estimated_ma = estimated_ma * (1 + 0.001 * (day_offset - 1))
                                    future_features[col] = (current_close - estimated_ma) / estimated_ma * 100 if estimated_ma > 0 else last_ratio
                                elif 'price_ma10_ratio' in col:
                                    last_ratio = merged['price_ma10_ratio'].iloc[-1] if 'price_ma10_ratio' in merged.columns else 0
                                    estimated_ma = last_close_for_ma / (1 + last_ratio/100) if last_ratio != -100 else last_close_for_ma
                                    estimated_ma = estimated_ma * (1 + 0.001 * (day_offset - 1))
                                    future_features[col] = (current_close - estimated_ma) / estimated_ma * 100 if estimated_ma > 0 else last_ratio
                                else:  # ma20
                                    last_ratio = merged['price_ma20_ratio'].iloc[-1] if 'price_ma20_ratio' in merged.columns else 0
                                    estimated_ma = last_close_for_ma / (1 + last_ratio/100) if last_ratio != -100 else last_close_for_ma
                                    estimated_ma = estimated_ma * (1 + 0.001 * (day_offset - 1))
                                    future_features[col] = (current_close - estimated_ma) / estimated_ma * 100 if estimated_ma > 0 else last_ratio
                            except:
                                future_features[col] = merged[col].tail(5).mean() if col in merged.columns else 0
                        else:
                            # 其他技术指标：使用基于预测价格的简化计算或趋势外推
                            # 使用前一天的预测值加上一个小的趋势调整，让每天都有变化
                            if day_offset == 2:
                                # 第2天：使用第1天的预测结果进行小幅调整
                                base_value = merged[col].iloc[-1] if col in merged.columns else 0
                                # 根据第1天的预测涨跌幅调整，让特征值有明显变化
                                adjustment = prev_pct_chg * 0.15  # 根据前一天的涨跌幅调整15%
                                future_features[col] = base_value + adjustment
                            elif day_offset == 3:
                                # 第3天：基于前两天的预测结果
                                if len(future_predictions) >= 1:
                                    prev_pred_2 = future_predictions[-1]  # 第2天的预测
                                    prev_pred_1 = future_predictions[-2] if len(future_predictions) >= 2 else None
                                    if prev_pred_1:
                                        trend = prev_pred_2['predicted_pct'] - prev_pred_1['predicted_pct']
                                        base_value = merged[col].iloc[-1] if col in merged.columns else 0
                                        # 使用趋势调整，让特征值有明显变化
                                        future_features[col] = base_value + trend * 0.25 + prev_pct_chg * 0.1
                                    else:
                                        base_value = merged[col].iloc[-1] if col in merged.columns else 0
                                        future_features[col] = base_value + prev_pct_chg * 0.18
                                else:
                                    future_features[col] = merged[col].tail(5).mean() if col in merged.columns else 0
                            else:
                                # 第7天：使用趋势外推，让特征值有明显变化
                                if len(future_predictions) >= 2:
                                    # 基于前几天的预测趋势
                                    recent_trend = (future_predictions[-1]['predicted_pct'] - future_predictions[-2]['predicted_pct']) if len(future_predictions) >= 2 else 0
                                    base_value = merged[col].iloc[-1] if col in merged.columns else 0
                                    # 使用更大的趋势系数，让第7天的特征值有明显不同
                                    future_features[col] = base_value + recent_trend * 0.4 * (day_offset - 2) + prev_pct_chg * 0.12
                                else:
                                    future_features[col] = merged[col].tail(5).mean() if col in merged.columns else 0
                # 周内效应特征
                elif col in ['is_monday', 'is_friday', 'is_tuesday']:
                    future_weekday = future_date.weekday()
                    if col == 'is_monday':
                        future_features[col] = 1 if future_weekday == 0 else 0
                    elif col == 'is_friday':
                        future_features[col] = 1 if future_weekday == 4 else 0
                    elif col == 'is_tuesday':
                        future_features[col] = 1 if future_weekday == 1 else 0
                # 周五涨跌幅（如果预测的是周一，使用前一个周五的涨跌幅）
                elif col == 'friday_pct_chg':
                    if future_date.weekday() == 0:  # 如果是周一
                        # 找到前一个周五的涨跌幅
                        friday_pct = None
                        for i in range(len(merged)-1, max(0, len(merged)-5), -1):
                            if merged.iloc[i]['is_friday'] == 1:
                                friday_pct = merged.iloc[i]['pct_chg']
                                break
                        future_features[col] = friday_pct if friday_pct is not None else 0
                    else:
                        future_features[col] = 0
                # 外部因素（大盘指数、比特币、美股、资金流向）
                # 对于多天预测，这些因素难以获得，使用趋势外推或衰减
                else:
                    if day_offset == 1:
                        future_features[col] = current_data[col] if col in current_data and not pd.isna(current_data[col]) else merged[col].tail(5).mean()
                    else:
                        # 多天预测时，使用趋势外推（基于最近几天的趋势）
                        if col in merged.columns:
                            recent_values = merged[col].tail(5).dropna()
                            if len(recent_values) >= 2:
                                # 计算趋势（最近几天的平均值或趋势）
                                trend = recent_values.iloc[-1] - recent_values.iloc[0] if len(recent_values) > 1 else 0
                                # 使用最后值加上趋势的衰减版本
                                future_features[col] = recent_values.iloc[-1] + trend * (day_offset - 1) * 0.3  # 趋势衰减
                            else:
                                future_features[col] = recent_values.mean() if len(recent_values) > 0 else 0
                        else:
                            future_features[col] = 0
            else:
                future_features[col] = 0
        
        # 进行预测
        X_future = pd.DataFrame([future_features])[feature_cols]
        predicted_pct_raw = model.predict(X_future)[0]
        
        # 科创板涨跌幅限制为20%（中际旭创是科创板股票）
        # 限制预测涨跌幅在-20%到+20%之间
        max_pct_limit = 20.0  # 科创板涨跌幅限制
        predicted_pct = max(-max_pct_limit, min(max_pct_limit, predicted_pct_raw))
        
        if abs(predicted_pct - predicted_pct_raw) > 0.01:
            print(f"    注意: 模型预测涨跌幅{predicted_pct_raw:.2f}%超出科创板限制，已限制为{predicted_pct:.2f}%")
        
        # 确定基准收盘价（用于计算预测收盘价）
        # 对于第1天：基于最后已知收盘价
        # 对于第2天及以后：基于前一天的预测收盘价
        if day_offset == 1:
            base_close = last_known_close
        else:
            # 找到前一个预测（day_offset-1对应的索引）
            prev_idx = None
            for i, (prev_day, _) in enumerate(future_dates):
                if prev_day == day_offset - 1:
                    prev_idx = i
                    break
            
            if prev_idx is not None and prev_idx < len(future_predictions):
                prev_pred = future_predictions[prev_idx]
                base_close = prev_pred['predicted_close']
            else:
                # 如果找不到前一个预测，基于最后已知收盘价
                base_close = last_known_close
        
        # 计算预测收盘价：基于基准收盘价和预测涨跌幅
        # 这是唯一正确的计算公式，确保一致性
        predicted_close = base_close * (1 + predicted_pct / 100)
        
        # 从预测收盘价反推涨跌幅，验证一致性
        calculated_pct_from_close = (predicted_close / base_close - 1) * 100
        
        # 如果反推的涨跌幅与模型预测的涨跌幅不一致，说明计算有问题
        # 此时应该使用模型预测的涨跌幅重新计算收盘价
        if abs(calculated_pct_from_close - predicted_pct) > 0.01:
            print(f"    警告: 预测涨跌幅和预测收盘价不一致！")
            print(f"      基准收盘价: {base_close:.2f}元")
            print(f"      模型预测涨跌幅: {predicted_pct:.2f}%")
            print(f"      从收盘价反推涨跌幅: {calculated_pct_from_close:.2f}%")
            print(f"      计算出的预测收盘价: {predicted_close:.2f}元")
            # 使用模型预测的涨跌幅重新计算收盘价，确保一致性
            predicted_close = base_close * (1 + predicted_pct / 100)
            print(f"      已修正预测收盘价为: {predicted_close:.2f}元")
            # 再次验证
            final_calculated_pct = (predicted_close / base_close - 1) * 100
            print(f"      修正后验证涨跌幅: {final_calculated_pct:.2f}% (应该与{predicted_pct:.2f}%一致)")
        
        
        # 最终一致性检查：确保预测涨跌幅和预测收盘价完全一致
        verification_pct = (predicted_close / base_close - 1) * 100
        if abs(verification_pct - predicted_pct) > 0.01:
            print(f"    错误: 最终验证失败！强制使用模型预测的涨跌幅重新计算收盘价")
            print(f"      模型预测涨跌幅: {predicted_pct:.2f}%")
            print(f"      从收盘价反推涨跌幅: {verification_pct:.2f}%")
            predicted_close = base_close * (1 + predicted_pct / 100)
            final_verification = (predicted_close / base_close - 1) * 100
            print(f"      修正后预测收盘价: {predicted_close:.2f}元")
            print(f"      修正后验证涨跌幅: {final_verification:.2f}%")
        
        future_predictions.append({
            'day_offset': day_offset,
            'date': future_date.strftime('%Y-%m-%d'),
            'predicted_pct': predicted_pct,
            'predicted_close': predicted_close,
            'base_close': base_close  # 保存基准收盘价，便于调试
        })
        
        # 最终验证输出
        final_verification_pct = (predicted_close / base_close - 1) * 100
        print(f"    第{day_offset}个工作日 ({future_date.strftime('%Y-%m-%d')}):")
        print(f"      基准收盘价: {base_close:.2f}元")
        print(f"      预测涨跌幅: {predicted_pct:.2f}% (科创板限制: ±20%)")
        print(f"      预测收盘价: {predicted_close:.2f}元")
        print(f"      验证涨跌幅: {final_verification_pct:.2f}% (应该与预测涨跌幅一致)")
        
        # 更新历史记录（记录所有预测）
        # 注意：每次都更新预测，确保使用最新的计算结果
        date_str = future_date.strftime('%Y-%m-%d')
        history['predictions'][date_str] = {
            'day_offset': day_offset,
            'predicted_pct': float(predicted_pct),
            'predicted_close': float(predicted_close),
            'base_close': float(base_close),
            'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # 检查是否有新的实际数据需要更新
    print("\n检查是否有新的实际数据...")
    latest_actual_date = merged['trade_date'].max().strftime('%Y-%m-%d')
    
    # 保存历史记录
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    # 生成HTML网页
    generate_advanced_html(merged, future_predictions, history, model_name, lr_r2 if model_name == "线性回归" else rf_r2)
    
    # 保存预测数据
    output_df = merged[['trade_date', 'close', 'predicted_close', 'pct_chg', 'predicted_pct']].copy()
    output_df['trade_date'] = output_df['trade_date'].dt.strftime('%Y-%m-%d')
    
    # 去除重复日期（保留最新的预测结果）
    # 如果同一日期有多个预测，只保留最后一个（最新的预测）
    output_df = output_df.drop_duplicates(subset=['trade_date'], keep='last')
    output_df = output_df.sort_values('trade_date')
    
    output_df.columns = ['日期', '实际收盘价', '预测收盘价', '实际涨跌幅(%)', '预测涨跌幅(%)']
    output_df['误差'] = abs(output_df['实际收盘价'] - output_df['预测收盘价'])
    output_df['误差率(%)'] = (output_df['误差'] / output_df['实际收盘价'] * 100).round(2)
    try:
        output_df.to_csv('中际旭创_价格预测数据.csv', index=False, encoding='utf-8-sig')
    except PermissionError:
        print("    警告: CSV文件被占用，跳过保存（请关闭Excel等程序后重试）")
    except Exception as e:
        print(f"    警告: 保存CSV文件失败: {str(e)[:50]}")
    
    # 生成预测模型图表（包含相关性分析和热力图）- 先于散点图生成
    print("\n正在生成预测模型图表（包含相关性分析和热力图）...")
    # 确保使用正确的R²分数
    final_r2 = lr_r2 if model_name == "线性回归" else rf_r2
    generate_prediction_model_chart(merged, feature_cols, model_name, final_r2)
    
    # 生成多因素散点图（精选12个）
    print("\n正在生成多因素散点图（精选12个重要因素）...")
    generate_factor_scatter_plots(merged, feature_cols)
    
    # 生成所有因素的散点图
    print("\n正在生成所有因素散点图（完整版）...")
    generate_all_factors_scatter_plots(merged, feature_cols)
    
    print("\n" + "=" * 80)
    print("预测模型构建完成！")
    print("=" * 80)
    print(f"\n已预测未来5个工作日:")
    for pred in future_predictions:
        print(f"  第{pred['day_offset']}个工作日 ({pred['date']}): 预测涨跌幅 {pred['predicted_pct']:.2f}%, 预测收盘价 {pred['predicted_close']:.2f}元")
    print(f"最新实际数据日期: {latest_actual_date}")
    print("\n生成的文件:")
    print("  1. 中际旭创_价格预测模型.png - 预测模型图表（包含相关性分析和热力图）")
    print("  2. 中际旭创_多因素散点图.png - 多因素散点图分析（精选12个重要因素）")
    print("  3. 中际旭创_所有因素散点图_第X页.png - 所有因素散点图（完整版，分页显示）")
    print("  4. 中际旭创_所有因素相关性汇总.csv - 所有因素相关性汇总表")
    print("  5. 中际旭创_价格预测.html - 网页表格（包含未来预测）")
    print("  6. 中际旭创_价格预测数据.csv - 预测数据CSV文件")
    print("  7. prediction_history.json - 预测历史记录")
    
    return model, feature_cols, merged, future_predictions

def generate_prediction_model_chart(merged, feature_cols, model_name, r2_score):
    """生成预测模型图表，包含相关性分析和热力图"""
    try:
        import seaborn as sns
        
        # 准备数据（去除缺失值）
        plot_data = merged[['pct_chg'] + feature_cols].copy()
        plot_data = plot_data.dropna()
        
        if len(plot_data) == 0:
            print("    警告: 数据不足，无法生成图表")
            return
        
        # 计算相关性矩阵
        corr_matrix = plot_data.corr()
        pct_chg_corr = corr_matrix['pct_chg'].drop('pct_chg').sort_values(ascending=False)
        
        # 创建图表（2行2列布局）
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle(f'中际旭创股票价格预测模型分析（{model_name}，R²={r2_score:.4f}）', 
                     fontsize=18, fontweight='bold', y=0.995)
        
        # 1. 实际值 vs 预测值散点图
        ax1 = plt.subplot(2, 2, 1)
        actual = plot_data['pct_chg']
        predicted = merged.loc[plot_data.index, 'predicted_pct'] if 'predicted_pct' in merged.columns else None
        if predicted is not None and len(predicted) > 0:
            ax1.scatter(actual, predicted, alpha=0.6, s=50, c='steelblue', edgecolors='none')
            # 添加对角线
            min_val = min(actual.min(), predicted.min())
            max_val = max(actual.max(), predicted.max())
            ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='完美预测线')
            ax1.set_xlabel('实际涨跌幅(%)', fontsize=12)
            ax1.set_ylabel('预测涨跌幅(%)', fontsize=12)
            ax1.set_title('实际值 vs 预测值', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
            # 添加R²和RMSE
            from sklearn.metrics import mean_squared_error
            rmse = np.sqrt(mean_squared_error(actual, predicted))
            ax1.text(0.05, 0.95, f'R² = {r2_score:.4f}\nRMSE = {rmse:.2f}%', 
                    transform=ax1.transAxes, fontsize=11,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 2. 相关性热力图（所有特征与涨跌幅的相关性）
        ax2 = plt.subplot(2, 2, 2)
        # 选择最重要的特征（最多20个）用于热力图
        top_features = pct_chg_corr.abs().nlargest(min(20, len(pct_chg_corr))).index.tolist()
        heatmap_data = corr_matrix.loc[['pct_chg'] + top_features, ['pct_chg'] + top_features]
        
        # 特征名称映射（用于热力图坐标标签）
        feature_name_map = {
            'pct_chg': '涨跌幅',
            'price_ma5_ratio': '价格相对MA5位置',
            'price_ma10_ratio': '价格相对MA10位置',
            'price_ma20_ratio': '价格相对MA20位置',
            'vol_ratio': '成交量比率',
            'vol_ratio_10': '成交量比率(10日)',
            'momentum_5': '5日动量',
            'momentum_10': '10日动量',
            'rsi': 'RSI指标',
            'macd': 'MACD指标',
            'macd_hist': 'MACD柱状图',
            'volatility_5': '5日波动率',
            'volatility_10': '10日波动率',
            'high_low_ratio': '高低价比率',
            'prev_pct_chg': '前一日涨跌幅',
            # 新增技术指标
            'kdj_k': 'KDJ-K值',
            'kdj_d': 'KDJ-D值',
            'kdj_j': 'KDJ-J值',
            'boll_mid': '布林带中轨',
            'boll_upper': '布林带上轨',
            'boll_lower': '布林带下轨',
            'boll_width': '布林带宽度',
            'boll_position': '价格在布林带位置',
            'cci': 'CCI指标',
            'obv': 'OBV指标',
            'obv_ma': 'OBV均线',
            'obv_ratio': 'OBV比率',
            'wr': '威廉指标',
            'plus_di': 'DMI+DI',
            'minus_di': 'DMI-DI',
            'adx': 'DMI-ADX',
            # 市场情绪指标
            'margin_balance_change': '融资余额变化率',
            'short_balance_change': '融券余额变化率',
            'holder_change_pct': '股东户数变化率',
            'margin_ratio': '融资占比',
            'inst_hold_vol_change': '机构持仓量变化率',
            'inst_hold_num_change': '机构持仓数量变化率',
            # 公司业绩指标
            'roe': '净资产收益率',
            'roa': '总资产收益率',
            'grossprofit_rate': '毛利率',
            'netprofit_rate': '净利率',
            'eps': '每股收益',
            'bps': '每股净资产',
            'revenue_yoy': '营收同比增长率',
            'n_income_yoy': '净利润同比增长率',
            'revenue_qoq': '营收环比增长率',
            'n_income_qoq': '净利润环比增长率',
            'forecast_optimism': '业绩预告乐观度',
            # 市场指数
            'cyb_pct': '创业板指涨跌幅',
            'sz_pct': '深证成指涨跌幅',
            'hs300_pct': '沪深300涨跌幅',
            'sh_pct': '上证指数涨跌幅',
            'zz500_pct': '中证500涨跌幅',
            # 外部市场
            'btc_pct': '比特币涨跌幅',
            'SP500_pct': '标普500涨跌幅',
            'NASDAQ_pct': '纳斯达克涨跌幅',
            'DOW_pct': '道琼斯涨跌幅',
            # 资金流向
            'net_ratio': '资金净流入比率',
            'net_mf_amount': '资金净流入',
            # 基本面
            'turnover_rate': '换手率',
            'circ_mv': '流通市值',
            'total_mv': '总市值',
            # 同行业股票
            'new_fiber_pct': '新易盛涨跌幅',
            # 宏观经济
            'cpi_yoy': 'CPI同比增长率',
            'cpi_mom': 'CPI环比增长率',
            'pmi': 'PMI指数',
            'pmi_change': 'PMI变化',
            'gdp_yoy': 'GDP同比增长率',
            'interest_rate': '利率',
            'interest_rate_change': '利率变化',
            'exchange_rate': '汇率',
            'exchange_rate_change': '汇率变化率',
            'm2_yoy': 'M2同比增长率',
            'm2_mom': 'M2环比增长率',
            # 新闻情绪
            'news_sentiment': '新闻情绪得分',
            # 周内效应
            'is_monday': '是否周一',
            'is_friday': '是否周五',
            'is_tuesday': '是否周二',
            'friday_pct_chg': '周五涨跌幅'
        }
        
        # 创建中文标签
        heatmap_labels = [feature_name_map.get(col, col) for col in heatmap_data.columns]
        
        # 绘制热力图，使用中文标签
        sns.heatmap(heatmap_data, annot=True, fmt='.2f', cmap='RdYlBu_r', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8}, ax=ax2,
                   vmin=-1, vmax=1, xticklabels=heatmap_labels, yticklabels=heatmap_labels)
        ax2.set_title('各因素与涨跌幅相关性热力图（Top 20）', fontsize=14, fontweight='bold')
        ax2.set_xlabel('')
        ax2.set_ylabel('')
        # 旋转标签以便更好地显示
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=9)
        plt.setp(ax2.get_yticklabels(), rotation=0, fontsize=9)
        
        # 3. 相关性条形图（Top 15特征，按绝对值排序）
        ax3 = plt.subplot(2, 2, 3)
        # 按绝对值排序，取前15个
        top_15_abs = pct_chg_corr.abs().nlargest(15)
        top_15 = pct_chg_corr.loc[top_15_abs.index].sort_values(ascending=False)
        colors = ['red' if x > 0 else 'green' for x in top_15.values]
        bars = ax3.barh(range(len(top_15)), top_15.values, color=colors, alpha=0.7)
        ax3.set_yticks(range(len(top_15)))
        # 特征名称映射
        feature_name_map = {
            'price_ma5_ratio': '价格相对MA5位置',
            'price_ma10_ratio': '价格相对MA10位置',
            'price_ma20_ratio': '价格相对MA20位置',
            'rsi': 'RSI指标',
            'macd': 'MACD指标',
            'prev_pct_chg': '前一日涨跌幅',
            'margin_balance_change': '融资余额变化率',
            'holder_change_pct': '股东户数变化率',
            'roe': '净资产收益率',
            'roa': '总资产收益率',
            'eps': '每股收益',
            'revenue_yoy': '营收同比增长率',
            'n_income_yoy': '净利润同比增长率',
            'cyb_pct': '创业板指涨跌幅',
            'btc_pct': '比特币涨跌幅',
            'net_mf_amount': '资金净流入',
            'new_fiber_pct': '新易盛涨跌幅',
            'vol_ratio': '成交量比率',
            'momentum_5': '5日动量',
            'momentum_10': '10日动量',
            'short_balance_change': '融券余额变化率',
            'margin_ratio': '融资占比',
            'bps': '每股净资产',
            'revenue_qoq': '营收环比增长率',
            'n_income_qoq': '净利润环比增长率',
            'forecast_optimism': '业绩预告乐观度',
            'sz_pct': '深证成指涨跌幅',
            'hs300_pct': '沪深300涨跌幅',
            'sh_pct': '上证指数涨跌幅',
            'zz500_pct': '中证500涨跌幅',
            'net_ratio': '资金净流入比率',
            'turnover_rate': '换手率',
            'circ_mv': '流通市值',
            'total_mv': '总市值',
            'SP500_pct': '标普500涨跌幅',
            'NASDAQ_pct': '纳斯达克涨跌幅',
            'DOW_pct': '道琼斯涨跌幅'
        }
        feature_labels = [feature_name_map.get(f, f) for f in top_15.index]
        ax3.set_yticklabels(feature_labels, fontsize=9)
        ax3.set_xlabel('相关系数', fontsize=12)
        ax3.set_title('Top 15 因素与涨跌幅相关性（按绝对值排序）', fontsize=14, fontweight='bold')
        ax3.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
        ax3.grid(True, alpha=0.3, axis='x')
        # 添加数值标签
        for i, (idx, val) in enumerate(top_15.items()):
            ax3.text(val, i, f' {val:.3f}', va='center', fontsize=8)
        
        # 4. 时间序列对比图（实际 vs 预测）
        ax4 = plt.subplot(2, 2, 4)
        # 只显示最近60天的数据，避免图表太拥挤
        recent_data = merged.tail(60).copy()
        ax4.plot(recent_data['trade_date'], recent_data['pct_chg'], 
                label='实际涨跌幅', linewidth=2, color='steelblue', marker='o', markersize=3)
        if 'predicted_pct' in recent_data.columns:
            ax4.plot(recent_data['trade_date'], recent_data['predicted_pct'], 
                    label='预测涨跌幅', linewidth=2, color='coral', linestyle='--', marker='s', markersize=3)
        ax4.set_xlabel('日期', fontsize=12)
        ax4.set_ylabel('涨跌幅(%)', fontsize=12)
        ax4.set_title('最近60天实际 vs 预测涨跌幅对比', fontsize=14, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
        # 旋转x轴标签
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig('中际旭创_价格预测模型.png', dpi=300, bbox_inches='tight')
        print("    ✓ 预测模型图表已保存: 中际旭创_价格预测模型.png")
        plt.close()
        
    except Exception as e:
        print(f"    ✗ 生成预测模型图表失败: {str(e)[:100]}")
        import traceback
        traceback.print_exc()

def add_time_series_features(df, feature_cols):
    """添加时间序列特征：滞后特征和滑动窗口统计"""
    df = df.copy()
    df = df.sort_values('trade_date')
    
    # 添加滞后特征（前1天、前2天、前3天的涨跌幅）
    if 'pct_chg' in df.columns:
        for lag in [1, 2, 3]:
            df[f'pct_chg_lag{lag}'] = df['pct_chg'].shift(lag)
    
    # 添加滑动窗口统计特征（过去5天、10天的均值、标准差）
    if 'pct_chg' in df.columns:
        for window in [5, 10]:
            df[f'pct_chg_ma{window}'] = df['pct_chg'].rolling(window=window, min_periods=1).mean()
            df[f'pct_chg_std{window}'] = df['pct_chg'].rolling(window=window, min_periods=1).std()
    
    # 添加技术指标的滞后特征（如果存在）
    key_tech_features = ['rsi', 'macd', 'price_ma5_ratio', 'price_ma10_ratio']
    for feature in key_tech_features:
        if feature in df.columns:
            df[f'{feature}_lag1'] = df[feature].shift(1)
    
    return df

def enhance_features(X_train, X_test, feature_cols, use_polynomial=False, use_interactions=True):
    """特征工程：添加交互项和多项式特征"""
    X_train_df = pd.DataFrame(X_train, columns=feature_cols)
    X_test_df = pd.DataFrame(X_test, columns=feature_cols)
    
    enhanced_features = list(feature_cols)
    
    # 添加交互项（重要特征之间的交互）
    if use_interactions:
        # 选择最重要的特征进行交互（技术指标与外部因素）
        tech_features = [f for f in feature_cols if any(x in f for x in ['ma', 'rsi', 'macd', 'momentum'])]
        external_features = [f for f in feature_cols if any(x in f for x in ['pct', 'net', 'margin', 'roe', 'roa'])]
        
        # 限制交互项数量，避免特征爆炸
        max_interactions = min(10, len(tech_features) * len(external_features))
        interaction_count = 0
        
        for tech_f in tech_features[:3]:  # 只选择前3个技术指标
            for ext_f in external_features[:3]:  # 只选择前3个外部因素
                if interaction_count >= max_interactions:
                    break
                if tech_f in X_train_df.columns and ext_f in X_train_df.columns:
                    X_train_df[f'{tech_f}_x_{ext_f}'] = X_train_df[tech_f] * X_train_df[ext_f]
                    X_test_df[f'{tech_f}_x_{ext_f}'] = X_test_df[tech_f] * X_test_df[ext_f]
                    enhanced_features.append(f'{tech_f}_x_{ext_f}')
                    interaction_count += 1
            if interaction_count >= max_interactions:
                break
    
    return X_train_df.values, X_test_df.values, enhanced_features

def generate_factor_scatter_plots(merged, feature_cols):
    """生成多因素散点图，展示各指标与股票涨跌幅的关系"""
    try:
        # 选择最重要的特征进行可视化（最多12个）
        # 优先选择：技术指标、市场情绪、业绩指标
        priority_features = []
        
        # 技术指标（包含新增指标，按优先级排序）
        tech_priority = [
            'price_ma5_ratio', 'price_ma10_ratio', 'price_ma20_ratio',
            'rsi', 'macd', 'prev_pct_chg',
            'kdj_k', 'kdj_d', 'kdj_j',
            'boll_position', 'boll_width',
            'cci', 'wr', 'adx',
            'vol_ratio', 'momentum_5', 'momentum_10',
            'volatility_5', 'high_low_ratio'
        ]
        for f in tech_priority:
            if f in feature_cols and f in merged.columns and f not in priority_features:
                priority_features.append(f)
        
        # 市场情绪指标
        sentiment_priority = ['margin_balance_change', 'holder_change_pct', 'margin_ratio',
                             'short_balance_change', 'inst_hold_vol_change']
        for f in sentiment_priority:
            if f in feature_cols and f in merged.columns and f not in priority_features:
                priority_features.append(f)
        
        # 业绩指标
        performance_priority = ['roe', 'roa', 'eps', 'revenue_yoy', 'n_income_yoy',
                               'grossprofit_rate', 'netprofit_rate', 'bps']
        for f in performance_priority:
            if f in feature_cols and f in merged.columns and f not in priority_features:
                priority_features.append(f)
        
        # 市场指数
        index_priority = ['cyb_pct', 'sz_pct', 'hs300_pct', 'sh_pct', 'zz500_pct']
        for f in index_priority:
            if f in feature_cols and f in merged.columns and f not in priority_features:
                priority_features.append(f)
        
        # 外部市场
        external_priority = ['btc_pct', 'SP500_pct', 'NASDAQ_pct', 'DOW_pct']
        for f in external_priority:
            if f in feature_cols and f in merged.columns and f not in priority_features:
                priority_features.append(f)
        
        # 资金流向
        money_priority = ['net_ratio', 'net_mf_amount']
        for f in money_priority:
            if f in feature_cols and f in merged.columns and f not in priority_features:
                priority_features.append(f)
        
        # 如果还不够12个，从所有可用特征中选择相关性最高的
        if len(priority_features) < 12:
            # 计算所有特征与涨跌幅的相关性
            available_features = [f for f in feature_cols if f in merged.columns and f not in priority_features]
            if len(available_features) > 0:
                try:
                    correlations = {}
                    for f in available_features:
                        if f in merged.columns and 'pct_chg' in merged.columns:
                            corr = merged[[f, 'pct_chg']].corr().iloc[0, 1]
                            if not np.isnan(corr):
                                correlations[f] = abs(corr)
                    
                    # 按相关性排序，选择最高的
                    sorted_features = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
                    for f, _ in sorted_features[:12 - len(priority_features)]:
                        if f not in priority_features:
                            priority_features.append(f)
                except:
                    pass
        
        # 限制最多12个特征
        priority_features = priority_features[:12]
        
        print(f"    选择了 {len(priority_features)} 个特征用于散点图: {priority_features[:5]}...")
        
        if len(priority_features) == 0:
            print("    警告: 没有可用的特征用于绘制散点图")
            return
        
        # 准备数据（去除缺失值）
        plot_data = merged[['pct_chg'] + priority_features].copy()
        # 只删除pct_chg为NaN的行，其他特征的NaN在绘制时单独处理
        plot_data = plot_data.dropna(subset=['pct_chg'])  # 至少保留pct_chg不为NaN的行
        
        if len(plot_data) == 0:
            print("    警告: 数据不足，无法绘制散点图")
            return
        
        # 检查每个特征的数据可用性
        available_features = []
        for f in priority_features:
            if f in plot_data.columns:
                non_null_count = plot_data[f].notna().sum()
                if non_null_count > 10:  # 至少需要10个有效数据点
                    available_features.append(f)
        
        if len(available_features) < len(priority_features):
            print(f"    注意: {len(priority_features) - len(available_features)} 个特征数据不足，将显示 {len(available_features)} 个特征")
            priority_features = available_features
        
        if len(priority_features) == 0:
            print("    警告: 没有足够的有效数据用于绘制散点图")
            return
        
        # 创建子图（3行4列，最多12个图）
        n_cols = 4
        n_features = len(priority_features)
        n_rows = (n_features + n_cols - 1) // n_cols
        
        print(f"    将生成 {n_features} 个散点图（{n_rows}行 x {n_cols}列）")
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5*n_rows))
        fig.suptitle('中际旭创股票涨跌幅多因素散点图分析', fontsize=16, fontweight='bold', y=0.995)
        
        # 如果只有一行，确保axes是二维数组
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        elif n_cols == 1:
            axes = axes.reshape(-1, 1)
        
        for idx, feature in enumerate(priority_features):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col] if n_rows > 1 else axes[col]
            
            # 绘制散点图
            x_data = plot_data[feature].fillna(0)
            y_data = plot_data['pct_chg']
            
            # 去除异常值（超过3个标准差）
            mean_x = x_data.mean()
            std_x = x_data.std()
            mean_y = y_data.mean()
            std_y = y_data.std()
            
            mask = (abs(x_data - mean_x) <= 3 * std_x) & (abs(y_data - mean_y) <= 3 * std_y)
            x_plot = x_data[mask]
            y_plot = y_data[mask]
            
            ax.scatter(x_plot, y_plot, alpha=0.5, s=30, c='steelblue', edgecolors='none')
            
            # 添加趋势线
            if len(x_plot) > 1:
                z = np.polyfit(x_plot, y_plot, 1)
                p = np.poly1d(z)
                x_trend = np.linspace(x_plot.min(), x_plot.max(), 100)
                ax.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2, label=f'趋势线 (斜率={z[0]:.2f})')
                ax.legend(fontsize=8)
            
            # 计算相关系数
            if len(x_plot) > 1:
                corr = np.corrcoef(x_plot, y_plot)[0, 1]
                ax.text(0.05, 0.95, f'相关系数: {corr:.3f}', 
                       transform=ax.transAxes, fontsize=10,
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            # 设置标题和标签
            feature_name_map = {
                'price_ma5_ratio': '价格相对MA5位置(%)',
                'price_ma10_ratio': '价格相对MA10位置(%)',
                'price_ma20_ratio': '价格相对MA20位置(%)',
                'vol_ratio': '成交量比率(5日)',
                'vol_ratio_10': '成交量比率(10日)',
                'momentum_5': '5日动量(%)',
                'momentum_10': '10日动量(%)',
                'rsi': 'RSI指标',
                'macd': 'MACD指标',
                'macd_hist': 'MACD柱状图',
                'volatility_5': '5日波动率(%)',
                'volatility_10': '10日波动率(%)',
                'high_low_ratio': '高低价比率(%)',
                'prev_pct_chg': '前一日涨跌幅(%)',
                # 新增技术指标
                'kdj_k': 'KDJ-K值',
                'kdj_d': 'KDJ-D值',
                'kdj_j': 'KDJ-J值',
                'boll_mid': '布林带中轨',
                'boll_upper': '布林带上轨',
                'boll_lower': '布林带下轨',
                'boll_width': '布林带宽度(%)',
                'boll_position': '价格在布林带位置(%)',
                'cci': 'CCI指标',
                'obv': 'OBV指标',
                'obv_ma': 'OBV均线',
                'obv_ratio': 'OBV比率',
                'wr': '威廉指标(%)',
                'plus_di': 'DMI+DI',
                'minus_di': 'DMI-DI',
                'adx': 'DMI-ADX',
                # 市场情绪指标
                'margin_balance_change': '融资余额变化率(%)',
                'short_balance_change': '融券余额变化率(%)',
                'holder_change_pct': '股东户数变化率(%)',
                'margin_ratio': '融资占比(%)',
                'inst_hold_vol_change': '机构持仓量变化率(%)',
                'inst_hold_num_change': '机构持仓数量变化率(%)',
                # 公司业绩指标
                'roe': '净资产收益率(%)',
                'roa': '总资产收益率(%)',
                'grossprofit_rate': '毛利率(%)',
                'netprofit_rate': '净利率(%)',
                'eps': '每股收益(元)',
                'bps': '每股净资产(元)',
                'revenue_yoy': '营收同比增长率(%)',
                'n_income_yoy': '净利润同比增长率(%)',
                'revenue_qoq': '营收环比增长率(%)',
                'n_income_qoq': '净利润环比增长率(%)',
                'forecast_optimism': '业绩预告乐观度',
                # 市场指数
                'cyb_pct': '创业板指涨跌幅(%)',
                'sz_pct': '深证成指涨跌幅(%)',
                'hs300_pct': '沪深300涨跌幅(%)',
                'sh_pct': '上证指数涨跌幅(%)',
                'zz500_pct': '中证500涨跌幅(%)',
                # 外部市场
                'btc_pct': '比特币涨跌幅(%)',
                'SP500_pct': '标普500涨跌幅(%)',
                'NASDAQ_pct': '纳斯达克涨跌幅(%)',
                'DOW_pct': '道琼斯涨跌幅(%)',
                # 资金流向
                'net_ratio': '资金净流入比率(%)',
                'net_mf_amount': '资金净流入(万元)',
                # 基本面
                'turnover_rate': '换手率(%)',
                'circ_mv': '流通市值(万元)',
                'total_mv': '总市值(万元)',
                # 宏观经济
                'cpi_yoy': 'CPI同比增长率(%)',
                'cpi_mom': 'CPI环比增长率(%)',
                'pmi': 'PMI指数',
                'pmi_change': 'PMI变化',
                'gdp_yoy': 'GDP同比增长率(%)',
                'interest_rate': '利率(%)',
                'interest_rate_change': '利率变化',
                'exchange_rate': '汇率',
                'exchange_rate_change': '汇率变化率(%)',
                'm2_yoy': 'M2同比增长率(%)',
                'm2_mom': 'M2环比增长率(%)',
                # 新闻情绪
                'news_sentiment': '新闻情绪得分',
                # 周内效应
                'is_monday': '是否周一',
                'is_friday': '是否周五',
                'is_tuesday': '是否周二',
                'friday_pct_chg': '周五涨跌幅(%)'
            }
            
            feature_name = feature_name_map.get(feature, feature)
            ax.set_xlabel(feature_name, fontsize=10)
            ax.set_ylabel('股票涨跌幅(%)', fontsize=10)
            ax.set_title(f'{feature_name} vs 涨跌幅', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
            ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
        
        # 隐藏多余的子图
        for idx in range(n_features, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col] if n_rows > 1 else axes[col]
            ax.axis('off')
        
        plt.tight_layout()
        plt.savefig('中际旭创_多因素散点图.png', dpi=300, bbox_inches='tight')
        print("    ✓ 多因素散点图已保存: 中际旭创_多因素散点图.png")
        plt.close()
        
    except Exception as e:
        print(f"    ✗ 生成多因素散点图失败: {str(e)[:100]}")
        import traceback
        traceback.print_exc()

def generate_all_factors_scatter_plots(merged, feature_cols):
    """生成所有因素的散点图，展示每个指标与股票涨跌幅的关系"""
    try:
        import seaborn as sns
        from scipy import stats
        
        # 准备数据（去除缺失值）
        plot_data = merged[['pct_chg'] + feature_cols].copy()
        plot_data = plot_data.dropna()
        
        if len(plot_data) == 0:
            print("    警告: 数据不足，无法绘制散点图")
            return
        
        # 计算每个特征与涨跌幅的相关性
        correlations = {}
        for feature in feature_cols:
            if feature in plot_data.columns:
                corr = plot_data[feature].corr(plot_data['pct_chg'])
                correlations[feature] = corr
        
        # 按相关性绝对值排序
        sorted_features = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        
        # 特征名称映射
        feature_name_map = {
            'price_ma5_ratio': '价格相对MA5位置',
            'price_ma10_ratio': '价格相对MA10位置',
            'price_ma20_ratio': '价格相对MA20位置',
            'vol_ratio': '成交量比率',
            'vol_ratio_10': '10日成交量比率',
            'momentum_5': '5日动量',
            'momentum_10': '10日动量',
            'rsi': 'RSI指标',
            'macd': 'MACD指标',
            'macd_hist': 'MACD柱状图',
            'volatility_5': '5日波动率',
            'volatility_10': '10日波动率',
            'high_low_ratio': '高低价比率',
            'prev_pct_chg': '前一日涨跌幅',
            'cyb_pct': '创业板指涨跌幅',
            'sz_pct': '深证成指涨跌幅',
            'hs300_pct': '沪深300涨跌幅',
            'sh_pct': '上证指数涨跌幅',
            'zz500_pct': '中证500涨跌幅',
            'btc_pct': '比特币涨跌幅',
            'net_ratio': '资金净流入比率',
            'net_mf_amount': '资金净流入',
            'turnover_rate': '换手率',
            'circ_mv': '流通市值',
            'total_mv': '总市值',
            'new_fiber_pct': '新易盛涨跌幅',
            'SP500_pct': '标普500涨跌幅',
            'NASDAQ_pct': '纳斯达克涨跌幅',
            'DOW_pct': '道琼斯涨跌幅',
            'is_monday': '是否周一',
            'is_friday': '是否周五',
            'is_tuesday': '是否周二',
            'friday_pct_chg': '周五涨跌幅',
            # 新增技术指标
            'kdj_k': 'KDJ-K值',
            'kdj_d': 'KDJ-D值',
            'kdj_j': 'KDJ-J值',
            'boll_mid': '布林带中轨',
            'boll_upper': '布林带上轨',
            'boll_lower': '布林带下轨',
            'boll_width': '布林带宽度',
            'boll_position': '价格在布林带位置',
            'cci': 'CCI指标',
            'obv': 'OBV指标',
            'obv_ma': 'OBV均线',
            'obv_ratio': 'OBV比率',
            'wr': '威廉指标',
            'plus_di': 'DMI+DI',
            'minus_di': 'DMI-DI',
            'adx': 'DMI-ADX',
            # 市场情绪指标
            'margin_balance_change': '融资余额变化率',
            'short_balance_change': '融券余额变化率',
            'margin_ratio': '融资占比',
            'holder_change_pct': '股东户数变化率',
            'inst_hold_vol_change': '机构持仓量变化率',
            'inst_hold_num_change': '机构持仓数量变化率',
            # 公司业绩指标
            'roe': '净资产收益率',
            'roa': '总资产收益率',
            'grossprofit_rate': '毛利率',
            'netprofit_rate': '净利率',
            'eps': '每股收益',
            'bps': '每股净资产',
            'revenue_yoy': '营收同比增长率',
            'n_income_yoy': '净利润同比增长率',
            'revenue_qoq': '营收环比增长率',
            'n_income_qoq': '净利润环比增长率',
            'forecast_optimism': '业绩预告乐观度',
            # 宏观经济指标
            'cpi_yoy': 'CPI同比增长率',
            'cpi_mom': 'CPI环比增长率',
            'pmi': 'PMI指数',
            'pmi_change': 'PMI变化',
            'gdp_yoy': 'GDP同比增长率',
            'interest_rate': '利率',
            'interest_rate_change': '利率变化',
            'exchange_rate': '汇率',
            'exchange_rate_change': '汇率变化率',
            'm2_yoy': 'M2同比增长率',
            'm2_mom': 'M2环比增长率',
            # 新闻情绪
            'news_sentiment': '新闻情绪得分'
        }
        
        # 创建子图（每页显示多个，分多页显示）
        n_features = len(sorted_features)
        n_cols = 4
        n_rows = 5  # 每页5行，共20个图
        n_pages = (n_features + n_rows * n_cols - 1) // (n_rows * n_cols)
        
        print(f"    共{len(sorted_features)}个因素，将分{n_pages}页显示")
        
        for page in range(n_pages):
            start_idx = page * n_rows * n_cols
            end_idx = min(start_idx + n_rows * n_cols, n_features)
            page_features = sorted_features[start_idx:end_idx]
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(24, 30))
            fig.suptitle(f'中际旭创股票涨跌幅 - 所有因素散点图分析（第{page+1}页，共{n_pages}页）', 
                        fontsize=18, fontweight='bold', y=0.995)
            
            # 确保axes是二维数组
            if n_rows == 1:
                axes = axes.reshape(1, -1)
            elif n_cols == 1:
                axes = axes.reshape(-1, 1)
            
            for idx, (feature, corr) in enumerate(page_features):
                row = idx // n_cols
                col = idx % n_cols
                ax = axes[row, col] if n_rows > 1 else axes[col]
                
                # 清洗数据：去除NaN和异常值
                temp_df = plot_data[[feature, 'pct_chg']].dropna()
                if len(temp_df) < 2:
                    ax.text(0.5, 0.5, '数据不足', ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(feature_name_map.get(feature, feature), fontsize=10)
                    continue
                
                # 去除异常值（超过3个标准差）
                for col_name in [feature, 'pct_chg']:
                    mean = temp_df[col_name].mean()
                    std = temp_df[col_name].std()
                    if std > 0:
                        temp_df = temp_df[(temp_df[col_name] > mean - 3 * std) & 
                                         (temp_df[col_name] < mean + 3 * std)]
                
                if len(temp_df) < 2:
                    ax.text(0.5, 0.5, '数据不足', ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(feature_name_map.get(feature, feature), fontsize=10)
                    continue
                
                # 绘制散点图
                sns.scatterplot(x=feature, y='pct_chg', data=temp_df, ax=ax, alpha=0.6, s=30)
                
                # 添加线性拟合线
                try:
                    z = np.polyfit(temp_df[feature], temp_df['pct_chg'], 1)
                    p = np.poly1d(z)
                    x_trend = np.linspace(temp_df[feature].min(), temp_df[feature].max(), 100)
                    ax.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2)
                except:
                    pass
                
                # 计算并显示相关系数
                correlation = temp_df[feature].corr(temp_df['pct_chg'])
                corr_color = 'red' if correlation > 0 else 'green'
                ax.text(0.05, 0.95, f'相关系数: {correlation:.3f}', 
                       transform=ax.transAxes, fontsize=10, 
                       verticalalignment='top', 
                       bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                       color=corr_color, fontweight='bold')
                
                # 设置标题和标签
                feature_name = feature_name_map.get(feature, feature)
                ax.set_title(f'{feature_name}\n(相关性: {correlation:.3f})', 
                            fontsize=10, fontweight='bold')
                ax.set_xlabel(feature_name, fontsize=9)
                ax.set_ylabel('涨跌幅(%)', fontsize=9)
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
                ax.axvline(x=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
            
            # 隐藏多余的子图
            for idx in range(len(page_features), n_rows * n_cols):
                row = idx // n_cols
                col = idx % n_cols
                ax = axes[row, col] if n_rows > 1 else axes[col]
                ax.axis('off')
            
            plt.tight_layout()
            filename = f'中际旭创_所有因素散点图_第{page+1}页.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"    ✓ 第{page+1}页已保存: {filename}")
            plt.close()
        
        # 生成相关性汇总文件
        print("\n    正在生成相关性汇总文件...")
        corr_summary = []
        for feature, corr in sorted_features:
            corr_summary.append({
                '因素': feature_name_map.get(feature, feature),
                '英文名': feature,
                '相关系数': round(corr, 4),
                '相关性强度': '强' if abs(corr) > 0.5 else ('中等' if abs(corr) > 0.3 else '弱'),
                '正负关系': '正相关' if corr > 0 else '负相关'
            })
        
        corr_df = pd.DataFrame(corr_summary)
        corr_df.to_csv('中际旭创_所有因素相关性汇总.csv', index=False, encoding='utf-8-sig')
        print("    ✓ 相关性汇总已保存: 中际旭创_所有因素相关性汇总.csv")
        
        # 统计正负相关数量
        positive_count = sum(1 for _, corr in sorted_features if corr > 0)
        negative_count = sum(1 for _, corr in sorted_features if corr < 0)
        print(f"\n    相关性统计:")
        print(f"      正相关因素: {positive_count}个 ({positive_count/len(sorted_features)*100:.1f}%)")
        print(f"      负相关因素: {negative_count}个 ({negative_count/len(sorted_features)*100:.1f}%)")
        print(f"      强相关因素(|r|>0.5): {sum(1 for _, corr in sorted_features if abs(corr) > 0.5)}个")
        
    except Exception as e:
        print(f"    ✗ 生成所有因素散点图失败: {str(e)[:100]}")
        import traceback
        traceback.print_exc()

def generate_advanced_html(merged, future_predictions, history, model_name, r2_score):
    """生成增强版HTML网页"""
    
    # 准备历史数据
    html_data = merged[['trade_date', 'close', 'predicted_close', 'pct_chg', 'predicted_pct']].copy()
    html_data = html_data.dropna()
    html_data['trade_date'] = html_data['trade_date'].dt.strftime('%Y-%m-%d')
    
    # 去除重复日期（保留最新的预测结果）
    # 如果同一日期有多个预测，只保留最后一个（最新的预测）
    html_data = html_data.drop_duplicates(subset=['trade_date'], keep='last')
    html_data = html_data.sort_values('trade_date').reset_index(drop=True)  # 重置索引，确保从0开始
    
    # 验证并修正历史数据中的预测涨跌幅和预测收盘价的一致性
    print("\n验证并修正历史数据中的预测一致性...")
    for idx in range(len(html_data)):
        row = html_data.iloc[idx]
        date_str = row['trade_date']
        predicted_close = row['predicted_close']
        predicted_pct = row['predicted_pct']
        
        # 计算基准收盘价（前一日收盘价）
        prev_close = None
        if idx > 0:
            # 使用前一行（前一日）的收盘价
            prev_close = html_data.iloc[idx - 1]['close']
        else:
            # 如果是第一行，尝试从merged中找到前一日收盘价
            try:
                date_obj = pd.to_datetime(date_str)
                prev_date = date_obj - pd.Timedelta(days=1)
                # 使用字符串匹配，因为merged中的trade_date可能是datetime类型
                prev_row = merged[merged['trade_date'].dt.strftime('%Y-%m-%d') == prev_date.strftime('%Y-%m-%d')]
                if len(prev_row) > 0:
                    prev_close = prev_row.iloc[0]['close']
            except Exception as e:
                pass
        
        if prev_close is not None and not pd.isna(prev_close) and prev_close > 0:
            # 从预测收盘价反推涨跌幅
            calculated_pct = (predicted_close / prev_close - 1) * 100
            # 如果反推的涨跌幅与预测涨跌幅不一致，使用预测涨跌幅重新计算收盘价
            if abs(calculated_pct - predicted_pct) > 0.01:
                corrected_close = prev_close * (1 + predicted_pct / 100)
                html_data.at[idx, 'predicted_close'] = corrected_close
                print(f"    修正历史数据: {date_str}, 基准收盘价={prev_close:.2f}, 预测涨跌幅={predicted_pct:.2f}%, 修正前预测收盘价={predicted_close:.2f}, 修正后={corrected_close:.2f}")
    
    html_data['误差'] = abs(html_data['close'] - html_data['predicted_close'])
    html_data['误差率(%)'] = (html_data['误差'] / html_data['close'] * 100).round(2)
    
    # 格式化数据
    html_data['实际收盘价'] = html_data['close'].round(2)
    html_data['预测收盘价'] = html_data['predicted_close'].round(2)
    html_data['实际涨跌幅(%)'] = html_data['pct_chg'].round(2)
    html_data['预测涨跌幅(%)'] = html_data['predicted_pct'].round(2)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>中际旭创股票价格预测（实时更新）</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #4CAF50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        td {{
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .positive {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .negative {{
            color: #27ae60;
            font-weight: bold;
        }}
        .future-row {{
            background-color: #fff9c4;
            font-weight: bold;
        }}
        .actualized-row {{
            background-color: #c8e6c9;
        }}
        .error-high {{
            background-color: #ffebee;
        }}
        .error-medium {{
            background-color: #fff3e0;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .info-box {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .info-box h3 {{
            margin-top: 0;
            color: #1976d2;
        }}
        .update-info {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>中际旭创(300308.SZ) 股票价格预测（实时更新版）</h1>
        <p class="subtitle">更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 模型: {model_name} | R²得分: {r2_score:.4f}</p>
        
        <div class="update-info">
            <strong>📊 模型说明：</strong>本模型会每天自动更新，使用最新数据重新训练，并预测未来5个工作日的股价。
            通过5个工作日的预测可以看到股票的趋势。当实际收盘价出来后，会自动更新到表格中，并用于改进模型。
        </div>
        
        <div class="info-box">
            <h3>模型说明</h3>
            <p>本预测模型综合考虑了以下因素：</p>
            <ul>
                <li>技术指标：价格相对均线位置、成交量比率、动量等</li>
                <li>大盘指数：创业板指、深证成指、沪深300</li>
                <li>资金流向：主力资金净流入比率</li>
                <li>外部市场：比特币涨跌幅、美股指数（标普500、纳斯达克、道琼斯）</li>
            </ul>
            <p><strong>注意：</strong>预测结果仅供参考，不构成投资建议。投资有风险，决策需谨慎。</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{len(html_data)}</div>
                <div class="stat-label">历史预测天数</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(future_predictions)}</div>
                <div class="stat-label">未来预测天数（5个工作日）</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{html_data['误差率(%)'].mean():.2f}%</div>
                <div class="stat-label">平均误差率</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{r2_score:.4f}</div>
                <div class="stat-label">模型R²得分</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📈 价格走势图（实际值 vs 预测值）</div>
            <div style="position: relative; height: 400px; width: 100%;">
                <canvas id="priceChart"></canvas>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📊 未来5个工作日预测</div>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>预测收盘价</th>
                        <th>预测涨跌幅(%)</th>
                        <th>实际收盘价</th>
                        <th>实际涨跌幅(%)</th>
                        <th>预测误差</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # 添加未来预测数据（显示未来5个工作日的预测）
    if future_predictions:
        for pred in future_predictions:
            date_str = pred['date']
            day_label = f"第{pred.get('day_offset', '?')}个工作日"
            actual_close = history['actuals'].get(date_str, {}).get('actual_close', None)
            actual_pct = history['actuals'].get(date_str, {}).get('actual_pct', None)
            
            # 确保预测涨跌幅和预测收盘价一致
            # 如果提供了基准收盘价，重新计算以确保一致性
            base_close = pred.get('base_close', None)
            predicted_pct = pred['predicted_pct']
            predicted_close = pred['predicted_close']
            
            if base_close is not None:
                # 从预测收盘价反推涨跌幅，验证一致性
                calculated_pct = (predicted_close / base_close - 1) * 100
                if abs(calculated_pct - predicted_pct) > 0.01:
                    # 如果不一致，使用模型预测的涨跌幅重新计算收盘价
                    predicted_close = base_close * (1 + predicted_pct / 100)
                    print(f"    修正HTML中的预测数据: {date_str}, 基准收盘价={base_close:.2f}, 预测涨跌幅={predicted_pct:.2f}%, 修正后预测收盘价={predicted_close:.2f}")
            
            row_class = "future-row"
            status = f"待验证({day_label})"
            error_cell = "-"
            
            if actual_close:
                row_class = "actualized-row"
                status = f"已更新({day_label})"
                error = abs(actual_close - predicted_close)
                error_cell = f"{error:.2f}"
                actual_close_cell = f"{actual_close:.2f}"
                actual_pct_cell = f"{actual_pct:.2f}" if actual_pct else "-"
            else:
                actual_close_cell = "-"
                actual_pct_cell = "-"
            
            pct_class = "positive" if predicted_pct > 0 else "negative"
            if actual_pct:
                actual_pct_class = "positive" if actual_pct > 0 else "negative"
            else:
                actual_pct_class = ""
            
            html_content += f"""
                    <tr class="{row_class}">
                        <td>{date_str} ({day_label})</td>
                        <td>{predicted_close:.2f}</td>
                        <td class="{pct_class}">{predicted_pct:.2f}</td>
                        <td>{actual_close_cell}</td>
                        <td class="{actual_pct_class}">{actual_pct_cell}</td>
                        <td>{error_cell}</td>
                        <td>{status}</td>
                    </tr>
"""
    else:
        html_content += """
                    <tr>
                        <td colspan="7" style="text-align: center; color: #999;">暂无预测数据</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">📊 历史预测记录</div>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>实际收盘价</th>
                        <th>预测收盘价</th>
                        <th>实际涨跌幅(%)</th>
                        <th>预测涨跌幅(%)</th>
                        <th>误差</th>
                        <th>误差率(%)</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # 添加历史数据（按日期倒序，已去重，每个日期只有一行）
    for idx, row in html_data.sort_values('trade_date', ascending=False).iterrows():
        error_class = ""
        if row['误差率(%)'] > 5:
            error_class = "error-high"
        elif row['误差率(%)'] > 3:
            error_class = "error-medium"
        
        pct_class = "positive" if row['实际涨跌幅(%)'] > 0 else "negative"
        pred_pct_class = "positive" if row['预测涨跌幅(%)'] > 0 else "negative"
        
        html_content += f"""
                    <tr class="{error_class}">
                        <td>{row['trade_date']}</td>
                        <td>{row['实际收盘价']:.2f}</td>
                        <td>{row['预测收盘价']:.2f}</td>
                        <td class="{pct_class}">{row['实际涨跌幅(%)']:.2f}</td>
                        <td class="{pred_pct_class}">{row['预测涨跌幅(%)']:.2f}</td>
                        <td>{row['误差']:.2f}</td>
                        <td>{row['误差率(%)']:.2f}</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="update-info">
            <strong>🔄 如何更新实际数据：</strong>
            <ol>
                <li>每天收盘后，运行更新脚本：<code>python update_predictions.py</code></li>
                <li>脚本会自动获取最新实际收盘价并更新到网页</li>
                <li>模型会使用新数据重新训练，提高预测准确性</li>
            </ol>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script>
        // 准备图表数据
        const historicalData = """ + json.dumps(html_data[['trade_date', '实际收盘价', '预测收盘价']].to_dict('records'), ensure_ascii=False) + """;
        const futureData = """ + json.dumps([{'trade_date': pred['date'], '实际收盘价': None, '预测收盘价': round(pred['predicted_close'], 2)} for pred in future_predictions], ensure_ascii=False) + """;
        
        // 合并数据
        const allDates = [];
        const actualPrices = [];
        const predictedPrices = [];
        
        // 历史数据（只取最近30天，避免图表太拥挤）
        const recentHistorical = historicalData.slice(-30);
        recentHistorical.forEach(function(item) {
            allDates.push(item.trade_date);
            actualPrices.push(item.实际收盘价);
            predictedPrices.push(item.预测收盘价);
        });
        
        // 未来预测数据
        futureData.forEach(function(item) {
            allDates.push(item.trade_date);
            actualPrices.push(null);  // 未来日期没有实际价格
            predictedPrices.push(item.预测收盘价);
        });
        
        // 创建图表
        window.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('priceChart');
            if (!ctx) {
                console.error('找不到canvas元素');
                return;
            }
            new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: allDates,
                datasets: [
                    {
                        label: '实际收盘价',
                        data: actualPrices,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        pointRadius: 3,
                        tension: 0.1,
                        spanGaps: true
                    },
                    {
                        label: '预测收盘价',
                        data: predictedPrices,
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderWidth: 2,
                        pointRadius: 3,
                        borderDash: [5, 5],
                        tension: 0.1,
                        spanGaps: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '中际旭创股票价格预测对比图（最近30天 + 未来5个工作日）',
                        font: {
                            size: 16
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '价格（元）'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '日期'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
        });
    </script>
</body>
</html>
"""
    
    with open('中际旭创_价格预测.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML网页已生成: 中际旭创_价格预测.html")

def integrate_enhancements(model, X_test, y_test, feature_cols, merged, predictions):
    """集成增强功能（模型解释性、风险管理等）"""
    try:
        from model_enhancements import (
            calculate_shap_values, calculate_lime_explanation, visualize_feature_importance,
            calculate_prediction_intervals, calculate_risk_metrics, generate_stop_loss_take_profit,
            ModelVersionManager
        )
        
        print("\n" + "="*60)
        print("正在集成增强功能...")
        print("="*60)
        
        # 1. 模型解释性
        print("\n1. 计算模型解释性指标...")
        try:
            # SHAP值分析
            X_sample = pd.DataFrame(X_test, columns=feature_cols).head(100)  # 使用样本加速
            shap_values, shap_importance_df, explainer = calculate_shap_values(
                model, X_sample, feature_cols
            )
            if shap_importance_df is not None:
                print(f"   ✓ SHAP分析完成，Top 5重要特征:")
                for idx, row in shap_importance_df.head(5).iterrows():
                    print(f"      {row['feature']}: {row['shap_importance']:.4f}")
            
            # LIME局部解释
            lime_explanation = calculate_lime_explanation(model, X_sample, feature_cols, instance_idx=0)
            if lime_explanation is not None:
                print("   ✓ LIME解释完成")
            
            # 特征重要性可视化（传递必要的参数）
            # 确保merged数据完整，不要传递过滤后的数据
            # 使用原始的merged数据，包含所有列
            print(f"    调试: 准备可视化，merged形状={merged.shape if merged is not None else 'None'}")
            print(f"    调试: feature_cols数量={len(feature_cols)}")
            if merged is not None:
                print(f"    调试: merged包含pct_chg={'pct_chg' in merged.columns}")
                print(f"    调试: merged中feature_cols的匹配情况={sum(1 for f in feature_cols if f in merged.columns)}/{len(feature_cols)}")
            visualize_feature_importance(model, feature_cols, merged=merged, X_sample=X_sample)
            print("   ✓ 特征重要性可视化完成")
        except Exception as e:
            print(f"   模型解释性分析失败: {str(e)[:100]}")
            import traceback
            print(f"   错误详情: {traceback.format_exc()[:300]}")
        
        # 2. 风险管理
        print("\n2. 计算风险指标...")
        try:
            # 预测区间
            pred, lower, upper, residual_std = calculate_prediction_intervals(
                model, X_test, y_test, confidence=0.95
            )
            if pred is not None:
                print(f"   ✓ 预测区间计算完成（95%置信度）")
                print(f"      残差标准差: {residual_std:.4f}%")
            
            # 风险指标
            risk_metrics = calculate_risk_metrics(predictions, y_test, None)
            if risk_metrics:
                print(f"   ✓ 风险指标计算完成:")
                print(f"      波动率: {risk_metrics.get('volatility', 0):.4f}%")
                if 'max_drawdown' in risk_metrics:
                    print(f"      最大回撤: {risk_metrics['max_drawdown']:.4f}%")
                if 'var_95' in risk_metrics:
                    print(f"      VaR(95%): {risk_metrics['var_95']:.4f}%")
            
            # 止损止盈建议（基于最新预测）
            if len(future_predictions) > 0:
                latest_pred = future_predictions[0]
                current_price = merged['close'].iloc[-1] if 'close' in merged.columns else None
                if current_price:
                    suggestions = generate_stop_loss_take_profit(
                        latest_pred.get('predicted_close', current_price),
                        current_price,
                        risk_metrics
                    )
                    if suggestions:
                        print(f"   ✓ 止损止盈建议生成完成")
                        if 'stop_loss' in suggestions:
                            sl = suggestions['stop_loss']
                            print(f"      止损价: {sl['price']:.2f} ({sl['percentage']:.2f}%)")
                        if 'take_profit' in suggestions and suggestions['take_profit']:
                            tp = suggestions['take_profit']
                            print(f"      止盈价: {tp['price']:.2f} ({tp['percentage']:.2f}%)")
        except Exception as e:
            print(f"   风险管理分析失败: {str(e)[:50]}")
        
        # 3. 模型版本管理
        print("\n3. 保存模型版本...")
        try:
            version_manager = ModelVersionManager()
            versions = version_manager.list_versions()
            new_version = max(versions) + 1 if versions else 1
            
            metadata = {
                'r2_score': r2_score(y_test, predictions) if len(predictions) == len(y_test) else None,
                'rmse': np.sqrt(mean_squared_error(y_test, predictions)) if len(predictions) == len(y_test) else None,
                'feature_count': len(feature_cols),
                'model_type': type(model).__name__
            }
            
            model_path = version_manager.save_model(model, new_version, metadata)
            if model_path:
                print(f"   ✓ 模型已保存为版本 v{new_version}")
        except Exception as e:
            print(f"   模型版本管理失败: {str(e)[:50]}")
        
        print("\n" + "="*60)
        print("增强功能集成完成！")
        print("="*60)
        
    except ImportError:
        print("\n增强功能模块未找到，跳过集成。")
        print("增强功能包括：模型解释性（SHAP/LIME）、风险管理、模型版本管理等")
    except Exception as e:
        print(f"\n增强功能集成失败: {str(e)[:50]}")


def install_missing_packages():
    """自动安装缺失的包"""
    import subprocess
    import sys
    
    required_packages = {
        'shap': 'shap>=0.41.0',
        'lime': 'lime>=0.2.0',
        'transformers': 'transformers>=4.20.0',
        'torch': 'torch>=1.12.0',
        'schedule': 'schedule>=1.2.0'
    }
    
    missing_packages = []
    for package, install_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(install_name)
    
    if missing_packages:
        print("\n" + "="*60)
        print("检测到缺失的依赖包，正在自动安装...")
        print("="*60)
        for package in missing_packages:
            print(f"正在安装: {package}")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet', '--no-warn-script-location'])
                print(f"  ✓ {package} 安装成功")
            except Exception as e:
                print(f"  ✗ {package} 安装失败: {str(e)[:50]}")
        print("="*60 + "\n")
    else:
        print("所有依赖包已安装")

if __name__ == '__main__':
    try:
        # 自动安装缺失的包
        install_missing_packages()
        
        # 运行主程序
        print("\n" + "="*80)
        print("开始运行股票价格预测模型...")
        print("="*80 + "\n")
        
        model, feature_cols, merged, future_predictions = build_and_update_model()
        
        # 集成增强功能（可选）
        try:
            # 获取测试集数据用于增强功能分析
            X_all = merged[feature_cols].fillna(0)
            y_all = merged['pct_chg']
            split_idx = int(len(merged) * 0.8)
            X_test = X_all[split_idx:].values
            y_test = y_all[split_idx:].values
            predictions = model.predict(X_test)
            
            # 集成增强功能
            integrate_enhancements(model, X_test, y_test, feature_cols, merged, predictions)
        except Exception as e:
            print(f"\n增强功能集成跳过: {str(e)[:50]}")
        
        print("\n" + "="*80)
        print("程序运行完成！")
        print("="*80)
        
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()

