# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 09:31:18 2019

@author: 018614
"""
import numpy as np
from scipy.optimize import linprog


def alloy_addition_t(cw, alloyXw, yw, delta_aim, weight, x_aim, casting_loss, x_concent, x_loss, y, uc, c):
    """
    输入：
        cw：丝线j成分i的含有率(%)	，由丝线成分表定义
        alloyXw：丝线j的喂入量(kg)
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
        alloyX_t:温度计算用成分调整的合金铁j的投入量(kg)
        alloyX2_t:温度计算用成分微调整的合金铁j的投入量(kg)
        w_alloy_t: 温度计算用铁合金投入量(kg)
        w_alloy2_t:温度计算用微调整铁合金投入量(kg)
    作用：
        温度计算用合金投入量计算
    """
    # 铁合金成分调整及微调
    b = []
    b2 = []
    wire_cor = np.dot(cw, alloyXw) * yw / (10 * weight)
    # 补偿由于浇铸方法及浇铸位置的不同带来的成分损失
    # 只有 al、ca、ti三种元素casting_loss不为0，其余元素均为0
    x_aim = list( map(lambda x,y: x+y,x_aim,casting_loss))
    temp = zip(delta_aim, x_concent, x_aim, x_loss, y, wire_cor)
    for i, j, x, y, z, k in temp:
        if i != 0 and x - j >= i:
            b.append((x - i - j + y - k) * 10 * weight / z)
            b2.append((i + y - k) * 10 * weight / z)
        else:
            b.append((x - j + y - k) * 10 * weight / z)  # xi = al、ca、ti
            b2.append(0)
    b = np.array(b)
    b2 = np.array(b2)
    number_of_steel = len(uc)

    bounds = []
    for i in range(number_of_steel):
        bounds.append((0, 10000))

    res = linprog(uc, A_eq=c, b_eq=b, bounds=bounds)

    alloyX_t = res.x

    if res.success == False:
        alloyX_t = np.zeros(number_of_steel)

    w_alloy_t = sum(alloyX_t)

    bounds = []
    for i in range(number_of_steel):
        bounds.append((0, 10000))

    res2 = linprog(uc, A_eq=c, b_eq=b2, bounds=bounds)

    alloyX2_t = res2.x
    if res.success == False:
        alloyX2_t = np.zeros(number_of_steel)

    w_alloy2_t = sum(alloyX2_t)
    return alloyX_t, w_alloy_t, alloyX2_t, w_alloy2_t