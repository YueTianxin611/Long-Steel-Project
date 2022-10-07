# -*- coding: utf-8 -*-

import numpy as np
from scipy.optimize import linprog

# 2.3.6.2合金添加计算
def alloy_addition(cw, alloyXw, yw, delta_aim, weight, x_aim, casting_loss, x_concent, x_loss, y, uc, c):
    """
    输入：
        cw：丝线j成分i的含有率(%)，由丝线成分表定义
        alloyXw：丝线j的喂入量(kg),计算值
        yw：喂丝时的i成分收得率，由钢种组参数表定义
        delta_aim:成分粗调整时目标值下方调整带,由钢种组参数表定义
        weight:钢水重量(ton),来自上步工序或人工输入
        x_aim:钢种的成分目标值(%),由钢种成分表定义
        casting_loss:由于浇铸方法及浇铸位置的不同带来的成分损失,p28
        x_concent:钢水中的成分测定值(%)	,来自分析计算机
        x_loss:成分调整时的损失量(%)	,由钢种组参数表定义
        y:合金的i成分收得率,由钢种组参数表定义
        uc:铁合金j的单价(Rmb / kg),由铁合金成分表定义
        c:合金铁j的i成分含有率(%),由铁合金成分表定义
    输出：
        alloyX:成分调整的合金铁j的投入量(kg)
    作用：
        计算出使得合金配方价格最低的合金投入量
    """
    b = []
    wire_cor = np.dot(cw, alloyXw) * yw / (10 * weight)
    # 补偿由于浇铸方法及浇铸位置的不同带来的成分损失
    # 只有 al、ca、ti三种元素casting_loss不为0，其余元素均为0
    x_aim = list(map(lambda x, y: x + y, x_aim, casting_loss))
    temp = zip(delta_aim, x_concent, x_aim, x_loss, y, wire_cor)
    for i, j, x, y, z, k in temp:
        if i != 0 and x - j >= i:
            b.append((x - i - j + y - k) * 10 * weight / z)
        else:
            b.append((x - j + y - k) * 10 * weight / z)
    number_of_steel = len(uc)

    b = np.array(b)

    bounds = []
    for i in range(number_of_steel):
        bounds.append((0, 10000))

    res = linprog(uc, A_eq=c, b_eq=b, bounds=bounds)

    alloyX = res.x
    if res.success == False:
        alloyX = np.zeros(number_of_steel)

    return alloyX
