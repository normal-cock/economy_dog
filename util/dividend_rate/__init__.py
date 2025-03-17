


def future_avg_dr_cal(current_dr, interest_growth_rate, duration_year):
    '''
        current_dr: 0.08
        interest_growth_rate: 0.1
        duration_year: 5
    '''

    sum_dr = 0
    for i in range(duration_year):
        sum_dr += current_dr*((1+interest_growth_rate)**i)

    return sum_dr/duration_year


# 营业收入: 5,698,158,853.
# 营业成本: 4,408,209,268.
# 销售费用: 1,630,293,023
# 库存余额: 12,354,323,751 11,622,043,947


if __name__ == '__main__':
    print(future_avg_dr_cal(0.025, 0.15, 10))
    print(future_avg_dr_cal(0.025, 0.1, 10))
    # print(future_avg_dr_cal(0.0317, 0.1, 10))
    # print(future_avg_dr_cal(0.0453, 0.1, 10))
    # print(future_avg_dr_cal(0.0453, 0.05, 10))
    # print(future_avg_dr_cal(0.0417, 0.08, 10))
    # print(future_avg_dr_cal(0.035, 0.118, 10))
    # print(future_avg_dr_cal(0.0515, 0.1038, 10))
    # print(future_avg_dr_cal(0.0503, 0.1098, 10))
    # print(future_avg_dr_cal(0.0538, 0.08, 10))
