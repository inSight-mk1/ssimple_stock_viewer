import pandas as pd
import numpy as np


def analyze_strategy_from_csv(csv_path, consecutive_losses=2, target_win_rate=40.0):
    """
    按照连败跟单策略，基于csv每段交易详情进行回测，
    统计策略交易的胜率、赔率、胜负中位数、最大连败次数、总盈利
    """
    df = pd.read_csv(csv_path, encoding='utf-8')
    # 兼容无表头情况
    if df.columns[0] != '段号' and not df.columns[0].startswith('Unnamed'):
        df.columns = ['段号','交易方向','开始日期','结束日期','交易笔数','盈利笔数','亏损笔数','总盈亏','结果']

    results_seq = df['结果'].tolist()
    profits_seq = df['总盈亏'].tolist()

    # 策略回测主逻辑
    following = False
    loss_count = 0
    follow_indices = []  # 记录所有被策略选中的段的索引
    current_follow = []  # 当前一轮跟单的索引

    for i, result in enumerate(results_seq):
        if not following:
            if result == '负':
                loss_count += 1
                if loss_count >= consecutive_losses:
                    following = True
                    loss_count = 0
                    current_follow = [i]
            else:
                loss_count = 0
        else:
            current_follow.append(i)
            # 统计当前跟单胜率
            streak_results = [results_seq[idx] for idx in current_follow]
            wins = streak_results.count('胜')
            win_rate = wins / len(streak_results) * 100
            if win_rate >= target_win_rate:
                follow_indices.extend(current_follow)
                following = False
                current_follow = []
    # 处理结尾还在跟单的情况
    if following and current_follow:
        follow_indices.extend(current_follow)

    # 去重并保持顺序
    follow_indices = sorted(set(follow_indices), key=follow_indices.index)

    # 提取策略选中的段的数据
    strat_df = df.iloc[follow_indices]
    strat_results = strat_df['结果'].tolist()
    strat_profits = strat_df['总盈亏'].tolist()

    win_count = strat_results.count('胜')
    lose_count = strat_results.count('负')
    total = len(strat_results)
    win_rate = win_count / total if total > 0 else 0

    win_profit = strat_df[strat_df['结果']=='胜']['总盈亏'].sum()
    lose_profit = strat_df[strat_df['结果']=='负']['总盈亏'].sum()
    payout_ratio = win_profit / abs(lose_profit) if lose_profit != 0 else np.nan

    win_median = strat_df[strat_df['结果']=='胜']['总盈亏'].median() if win_count > 0 else np.nan
    lose_median = strat_df[strat_df['结果']=='负']['总盈亏'].median() if lose_count > 0 else np.nan

    # 最大连败次数（只统计策略选中的段）
    max_consec_lose = 0
    current_lose = 0
    for res in strat_results:
        if res == '负':
            current_lose += 1
            max_consec_lose = max(max_consec_lose, current_lose)
        else:
            current_lose = 0

    total_profit = sum(strat_profits)

    # 输出
    print(f"策略实际交易段数: {total}")
    print(f"策略胜率: {win_rate*100:.2f}% ({win_count}/{total})")
    print(f"策略赔率(盈亏比): {payout_ratio:.2f}")
    print(f"策略胜的中位数: {win_median}")
    print(f"策略负的中位数: {lose_median}")
    print(f"策略最大连败次数: {max_consec_lose}")
    print(f"策略总盈利: {total_profit}")
    print("-"*40)

    # 全跟单策略
    all_results = df['结果'].tolist()
    all_profits = df['总盈亏'].tolist()
    all_win_count = all_results.count('胜')
    all_lose_count = all_results.count('负')
    all_total = len(all_results)
    all_win_rate = all_win_count / all_total if all_total > 0 else 0
    all_win_profit = df[df['结果']=='胜']['总盈亏'].sum()
    all_lose_profit = df[df['结果']=='负']['总盈亏'].sum()
    all_payout_ratio = all_win_profit / abs(all_lose_profit) if all_lose_profit != 0 else float('nan')
    all_win_median = df[df['结果']=='胜']['总盈亏'].median() if all_win_count > 0 else float('nan')
    all_lose_median = df[df['结果']=='负']['总盈亏'].median() if all_lose_count > 0 else float('nan')
    all_max_consec_lose = 0
    all_current_lose = 0
    for res in all_results:
        if res == '负':
            all_current_lose += 1
            all_max_consec_lose = max(all_max_consec_lose, all_current_lose)
        else:
            all_current_lose = 0
    all_total_profit = sum(all_profits)

    print(f"全跟单策略段数: {all_total}")
    print(f"全跟单胜率: {all_win_rate*100:.2f}% ({all_win_count}/{all_total})")
    print(f"全跟单赔率(盈亏比): {all_payout_ratio:.2f}")
    print(f"全跟单胜的中位数: {all_win_median}")
    print(f"全跟单负的中位数: {all_lose_median}")
    print(f"全跟单最大连败次数: {all_max_consec_lose}")
    print(f"全跟单总盈利: {all_total_profit}")

    # 返回详细轮次
    return {
        '策略交易段数': total,
        '策略胜率': win_rate,
        '策略赔率': payout_ratio,
        '策略胜中位数': win_median,
        '策略负中位数': lose_median,
        '策略最大连败': max_consec_lose,
        '策略总盈利': total_profit,
        '策略明细': strat_df.reset_index(drop=True)
    }


def main():
    csv_path = 'im_250425_analysis.csv'
    try:
        consecutive_losses = int(input("请输入触发跟单的连败次数: "))
    except ValueError:
        consecutive_losses = 2
        print(f"输入有误，使用默认值: {consecutive_losses}")
    try:
        target_win_rate = float(input("请输入停止跟单的目标胜率(%): "))
    except ValueError:
        target_win_rate = 40.0
        print(f"输入有误，使用默认值: {target_win_rate}%")
    results = analyze_strategy_from_csv(csv_path, consecutive_losses, target_win_rate)
    if results:
        print("\n--- 策略回测统计结果 ---")
        print(f"策略交易段数: {results['策略交易段数']}")
        print(f"策略胜率: {results['策略胜率']*100:.2f}%")
        print(f"策略赔率: {results['策略赔率']:.2f}")
        print(f"策略胜的中位数: {results['策略胜中位数']}")
        print(f"策略负的中位数: {results['策略负中位数']}")
        print(f"策略最大连败: {results['策略最大连败']}")
        print(f"策略总盈利: {results['策略总盈利']}")
        # 保存明细
        output_file = csv_path.rsplit('.csv', 1)[0] + f'_winrate{int(target_win_rate)}_n{consecutive_losses}_strategy_analysis.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"策略回测统计结果\n")
            f.write(f"策略交易段数: {results['策略交易段数']}\n")
            f.write(f"策略胜率: {results['策略胜率']*100:.2f}%\n")
            f.write(f"策略赔率: {results['策略赔率']:.2f}\n")
            f.write(f"策略胜的中位数: {results['策略胜中位数']}\n")
            f.write(f"策略负的中位数: {results['策略负中位数']}\n")
            f.write(f"策略最大连败: {results['策略最大连败']}\n")
            f.write(f"策略总盈利: {results['策略总盈利']}\n\n")
            f.write("策略明细:\n")
            results['策略明细'].to_string(f, index=False)
        print(f"\n策略明细已保存至: {output_file}")

if __name__ == "__main__":
    main()
