import pandas as pd
import numpy as np


def analyze_trades(file_path):
    # 读取txt文件
    try:
        rows = []
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            # 跳过可能的标题行
            start_idx = 0
            if '进场日期' in lines[0] and '出场日期' in lines[0]:
                start_idx = 1

            # 处理数据行
            for i in range(start_idx, len(lines)):
                line = lines[i].strip()
                if not line:  # 跳过空行
                    continue

                # 使用制表符(\t)分割
                cols = line.split('\t')
                if len(cols) == 7:  # 确保有正确的列数
                    rows.append(cols)
                else:
                    print(f"警告：行 {i + 1} 格式不正确，列数 = {len(cols)}，内容: {line}")

        # 创建DataFrame
        if rows:
            df = pd.DataFrame(rows, columns=['进场日期', '出场日期', '进场价格', '出场价格',
                                             '单笔盈亏', '累计毛收益', '累计净收益'])
        else:
            print("没有找到有效数据行")
            return None

    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

    # 确保数据类型正确
    df['进场价格'] = pd.to_numeric(df['进场价格'], errors='coerce')
    df['出场价格'] = pd.to_numeric(df['出场价格'], errors='coerce')
    df['单笔盈亏'] = pd.to_numeric(df['单笔盈亏'], errors='coerce')

    # 添加交易方向列
    df['交易方向'] = np.where(df['进场价格'] > 0, '多', '空')

    # 改进后的震荡过滤逻辑（带详细注释）
    direction_series = df['交易方向'].values
    group_ids = []
    current_group = 0
    main_direction = direction_series[0] if len(direction_series) > 0 else None
    reverse_count = 0
    reverse_indices = []

    for i, d in enumerate(direction_series):
        if d == main_direction:
            reverse_count = 0
            reverse_indices = []
            group_ids.append(current_group)
        else:
            reverse_count += 1
            reverse_indices.append(i)
            group_ids.append(current_group)
            if reverse_count == 3:
                # 从第一次反向单开始新段
                for j in range(reverse_indices[0], i+1):
                    group_ids[j] = current_group + 1
                current_group += 1
                main_direction = direction_series[reverse_indices[0]]
                reverse_count = 0
                reverse_indices = []

    # 如果最后还有未切分的，全部归入最后一段
    if reverse_indices and len(reverse_indices) < 3:
        for j in range(reverse_indices[0], len(direction_series)):
            group_ids[j] = current_group
        for j in range(i+1, len(direction_series)):
            group_ids[j] = current_group

    
    df['段落ID'] = group_ids

    # 分析结果
    results = []

    # 按段分组计算
    for segment_id, segment in df.groupby('段落ID'):
        direction = segment['交易方向'].iloc[0]
        total_profit = segment['单笔盈亏'].sum()
        win_count = len(segment[segment['单笔盈亏'] > 0])
        lose_count = len(segment[segment['单笔盈亏'] < 0])

        start_date = segment['进场日期'].iloc[0]
        end_date = segment['出场日期'].iloc[-1]

        result = {
            '段号': segment_id,
            '交易方向': direction,
            '开始日期': start_date,
            '结束日期': end_date,
            '交易笔数': len(segment),
            '盈利笔数': win_count,
            '亏损笔数': lose_count,
            '总盈亏': total_profit,
            '结果': '胜' if total_profit > 0 else '负'
        }
        results.append(result)

    return pd.DataFrame(results)


def main():
    file_path = 'ic_250425.txt'
    results = analyze_trades(file_path)

    if results is not None:
        # 获取胜负序列
        win_lose_sequence = ''.join(results['结果'].tolist())

        # 输出胜负序列到文本文件
        sequence_file = file_path.rsplit('.', 1)[0] + '_win_lose_seq.txt'
        with open(sequence_file, 'w', encoding='utf-8') as f:
            f.write(win_lose_sequence)
        print(f"\n胜负序列已保存至: {sequence_file}")

        # 保存详细结果到CSV
        output_file = file_path.rsplit('.', 1)[0] + '_analysis.csv'
        results.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"详细分析结果已保存至: {output_file}")

        # 输出总体统计
        win_segments = len(results[results['结果'] == '胜'])
        total_segments = len(results)
        print(f"\n总体胜率: {win_segments}/{total_segments} ({win_segments / total_segments * 100:.2f}%)")

        # 按方向统计
        direction_stats = results.groupby('交易方向').agg(
            交易段数=('段号', 'count'),
            胜利段数=('结果', lambda x: (x == '胜').sum()),
            总盈亏=('总盈亏', 'sum')
        )
        direction_stats['胜率'] = direction_stats['胜利段数'] / direction_stats['交易段数'] * 100

        print("\n按交易方向统计:")
        print(direction_stats)


if __name__ == "__main__":
    main()
