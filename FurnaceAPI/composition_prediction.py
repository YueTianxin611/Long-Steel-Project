# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 17:18:52 2019

@author: 018614
"""
import numpy as np
# 2.3.6.4 成分预测计算


def composition_prediction(c,alloyX,y,cw,alloyXw,yw,weight,x_concent,x_loss,flux_addition_done,s_molten_last,\
                           s_loss,s_total_des_time,s_time_des_std,s_molten_ini,s_dregs_ini,ws_total_in,ls,w_flux,\
                           s_molten_ini_before,s_dregs_ini_before,ws_total_before):
    """
    输入：
        c:合金铁j的i成分含有率(%),由铁合金成分表定义 1
        alloyX：成分调整的合金铁j的投入量(kg),alloy_addition函数计算得到 1
        y:合金的i成分收得率,由钢种组参数表定义 1
        cw：丝线j成分i的含有率(%)	，由丝线成分表定义 1
        alloyXw：丝线j的喂入量(kg)，计算值 1
        yw：喂丝时的i成分收得率，由钢种组参数表定义 1
        weight:钢水重量(ton),来自上步工序或人工输入 1
        x_concent:钢水中的成分测定值(%)	,来自分析计算机 1
        x_loss:成分调整时的损失量(%)	,由钢种组参数表定义 1
        flux_addition_done:bool,造渣料是否添加完毕
        s_molten_last:上步工序带来的钢水中S(%),为测定值
        s_loss：成分调整时S的损失量(%)	,由钢种组参数表定义
        s_total_des_time:造渣料搅拌时间（分）,计算值
        s_time_des_std:标准搅拌时间（分）,由渣条件参数表定义
        s_molten_ini:由造渣料添加得到 1
        s_dregs_ini：由造渣料添加得到 1
        ws_total_in：钢包中当前渣量(kg/ton)，每加入一次造渣料更新一次1
        ls：S分配比，由渣条件参数表定义 1
        w_flux：w_flux:造渣料的投入量，由造渣料添加得到
        s_molten_ini_before：前次渣料添加前钢水中的S(%)，由造渣料添加得到 1
        s_dregs_ini_before：前次渣料添加前渣中的S(%)	，由造渣料添加得到 1
        ws_total_before：前次渣料添加前钢包中的渣量(kg/ton)，由造渣料添加得到
        
    输出：
        x_exp：成分调整后的预测成分值(%)
        s_exp：成分调整后的s预测成分值(%)
    作用：分别预测各元素及S的含量
    """
    x_exp = (np.dot(c, alloyX)*y+np.dot(cw, alloyXw)*yw)/(10*weight)+x_concent-x_loss
    # 对于[%S]exp，按以下方式进行计算：

    if flux_addition_done != True:
        # 假设S在第三个
        s_exp = ((np.dot(c, alloyX)*y+np.dot(cw, alloyXw)*yw)/(10*weight))[2]+s_molten_last-s_loss
    elif s_total_des_time > s_time_des_std:
        s_exp = ((np.dot(c, alloyX)*y+np.dot(cw, alloyXw)*yw)/(10*weight))[2]-s_loss + \
        (s_molten_ini+s_dregs_ini*ws_total_in/1000)/(1+ls*(ws_total_in+w_flux/weight)/1000)
    else:
        s_exp = ((np.dot(c, alloyX)*y+np.dot(cw, alloyXw)*yw)/(10*weight))[2]-s_loss + \
        (s_molten_ini_before+s_dregs_ini_before*ws_total_before/1000)/(1+ls*ws_total_in/1000)
    return x_exp, s_exp
