def analyze_win_rate_strategy(file_path, consecutive_losses=2, target_win_rate=40.0):
    """
    分析连败后跟单直到达到目标胜率的策略

    参数:
    file_path (str): 包含胜负序列的文件路径
    consecutive_losses (int): 触发跟单的连续亏损次数
    target_win_rate (float): 停止跟单的目标胜率(%)

    返回:
    dict: 包含跟单结果的字典
    """
    # 读取胜负序列
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            win_lose_sequence = f.read().strip()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

    # 检查序列是否为空
    if not win_lose_sequence:
        print("胜负序列为空")
        return None

    print(f"原始胜负序列: {win_lose_sequence}")
    print(f"策略: 等待{consecutive_losses}连败后跟单，直到胜率达到{target_win_rate}%")

    # 初始化变量
    following = False  # 是否处于跟单状态
    loss_count = 0  # 当前连败计数

    follow_trades = []  # 记录所有跟单交易
    current_follow_streak = []  # 当前一轮跟单

    # 遍历胜负序列
    for i, result in enumerate(win_lose_sequence):
        if not following:  # 未在跟单状态
            if result == '负':
                loss_count += 1
                if loss_count >= consecutive_losses:
                    # 触发跟单条件
                    following = True
                    loss_count = 0
                    print(f"位置 {i + 1}: 检测到{consecutive_losses}连败，开始跟单")
                    # 当前这个负也要算作跟单中的一个
                    current_follow_streak.append(result)
            else:
                # 遇到胜，重置连败计数
                loss_count = 0
        else:  # 已在跟单状态
            # 记录当前交易
            current_follow_streak.append(result)

            # 计算当前胜率
            wins_count = current_follow_streak.count('胜')
            current_win_rate = (wins_count / len(current_follow_streak)) * 100

            # 检查是否达到目标胜率
            if current_win_rate >= target_win_rate:
                # 跟单胜率达标，停止跟单
                following = False
                follow_trades.append(current_follow_streak)
                print(
                    f"位置 {i + 1}: 跟单胜率达到{current_win_rate:.2f}%，结束本轮跟单，本轮结果: {''.join(current_follow_streak)}")
                current_follow_streak = []

    # 处理序列结束时仍在跟单的情况
    if following and current_follow_streak:
        wins_count = current_follow_streak.count('胜')
        current_win_rate = (wins_count / len(current_follow_streak)) * 100
        follow_trades.append(current_follow_streak)
        print(
            f"序列结束，最后一轮跟单未达到目标胜率，当前胜率: {current_win_rate:.2f}%，结果: {''.join(current_follow_streak)}")

    # 统计结果
    total_followed = sum(len(streak) for streak in follow_trades)
    wins = sum(streak.count('胜') for streak in follow_trades)
    losses = sum(streak.count('负') for streak in follow_trades)

    # 计算每轮跟单的结果
    round_results = []
    for i, streak in enumerate(follow_trades):
        round_wins = streak.count('胜')
        round_losses = streak.count('负')
        round_win_rate = (round_wins / len(streak)) * 100 if len(streak) > 0 else 0
        round_results.append({
            '轮次': i + 1,
            '跟单次数': len(streak),
            '胜': round_wins,
            '负': round_losses,
            '胜率': round_win_rate,
            '结果': ''.join(streak)
        })

    # 计算总体胜率
    win_rate = wins / total_followed * 100 if total_followed > 0 else 0

    return {
        '连败触发阈值': consecutive_losses,
        '目标胜率': target_win_rate,
        '跟单轮数': len(follow_trades),
        '总跟单次数': total_followed,
        '总胜利次数': wins,
        '总亏损次数': losses,
        '总胜率': win_rate,
        '详细轮次': round_results,
        '跟单序列': [''.join(streak) for streak in follow_trades]
    }


def main():
    # 文件路径，应该是包含胜负序列的txt文件
    file_path = 'ag_250424_win_lose_seq.txt'

    # 设置连败阈值
    try:
        consecutive_losses = int(input("请输入触发跟单的连败次数: "))
    except ValueError:
        consecutive_losses = 2  # 默认值
        print(f"输入有误，使用默认值: {consecutive_losses}")

    # 设置目标胜率
    try:
        target_win_rate = float(input("请输入停止跟单的目标胜率(%): "))
    except ValueError:
        target_win_rate = 40.0  # 默认值
        print(f"输入有误，使用默认值: {target_win_rate}%")

    # 分析策略
    results = analyze_win_rate_strategy(file_path, consecutive_losses, target_win_rate)

    if results:
        print("\n--- 基于胜率目标的连败跟单策略分析结果 ---")
        print(f"连败触发阈值: {results['连败触发阈值']}")
        print(f"目标胜率: {results['目标胜率']}%")
        print(f"跟单轮数: {results['跟单轮数']}")
        print(f"总跟单次数: {results['总跟单次数']}")
        print(f"总胜利次数: {results['总胜利次数']}")
        print(f"总亏损次数: {results['总亏损次数']}")
        print(f"总胜率: {results['总胜率']:.2f}%")

        print("\n各轮次跟单详情:")
        for round_info in results['详细轮次']:
            print(
                f"第{round_info['轮次']}轮: {round_info['结果']} (胜:{round_info['胜']}, 负:{round_info['负']}, 胜率:{round_info['胜率']:.2f}%)")

        # 保存结果到文件
        output_file = file_path.rsplit('_win_lose_seq.txt', 1)[
                          0] + f'_winrate{int(target_win_rate)}_n{consecutive_losses}_analysis.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"基于胜率目标的连败跟单策略分析结果\n")
            f.write(f"连败触发阈值: {results['连败触发阈值']}\n")
            f.write(f"目标胜率: {results['目标胜率']}%\n")
            f.write(f"跟单轮数: {results['跟单轮数']}\n")
            f.write(f"总跟单次数: {results['总跟单次数']}\n")
            f.write(f"总胜利次数: {results['总胜利次数']}\n")
            f.write(f"总亏损次数: {results['总亏损次数']}\n")
            f.write(f"总胜率: {results['总胜率']:.2f}%\n\n")

            f.write("各轮次跟单详情:\n")
            for round_info in results['详细轮次']:
                f.write(
                    f"第{round_info['轮次']}轮: {round_info['结果']} (胜:{round_info['胜']}, 负:{round_info['负']}, 胜率:{round_info['胜率']:.2f}%)\n")

        print(f"\n分析结果已保存至: {output_file}")


if __name__ == "__main__":
    main()
