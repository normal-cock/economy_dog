


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

1.07+(1.07*1.06)+(1.07*1.06*1.06)+(1.07*1.06*1.06*1.06)+(1.07*1.06*1.06*1.06*1.06)+(1.07*1.06*1.06*1.06*1.06*1.06)

def cal_avg_roi(begin_roi, avg_roe, dividend_pay_rate, duration_year):
    total_roi = 0
    roi_inc_rate = 1+ (avg_roe*(1-dividend_pay_rate))
    for i in range(duration_year):
        total_roi += begin_roi * (roi_inc_rate**i)
    return total_roi

if __name__ == '__main__':
    print(cal_avg_roi(0.07, 0.15, 0.6, 6))
    # print(future_avg_dr_cal(0.025, 0.15, 10))
    # print(future_avg_dr_cal(0.025, 0.1, 10))
    # print(future_avg_dr_cal(0.0317, 0.1, 10))
    # print(future_avg_dr_cal(0.0453, 0.1, 10))
    # print(future_avg_dr_cal(0.0453, 0.05, 10))
    # print(future_avg_dr_cal(0.0417, 0.08, 10))
    # print(future_avg_dr_cal(0.035, 0.118, 10))
    # print(future_avg_dr_cal(0.0515, 0.1038, 10))
    # print(future_avg_dr_cal(0.0503, 0.1098, 10))
    # print(future_avg_dr_cal(0.0538, 0.08, 10))
