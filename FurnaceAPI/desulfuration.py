# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 15:24:33 2019

@author: 018614
"""


# 2.3.5强搅拌脱硫计算，通过加入al降低渣中的氧含量，为强脱硫创造良好的脱硫环境
def desulfuration(t_fe_last, t_fe_f, mno_last, mno_f, sio2_last, sio2_f, p2o5_last, p2o5_f, ws_last, ws_total_in,
                  weight, w_flux):
    """
    输入：
        t_fe_last：上步工序带来的渣中t-fe(%)，由钢种组参数表定义
        mno_last：上步工序带来的渣中mno(%)，由钢种组参数表定义
        sio2_last：上步工序带来的渣中sio2(%)，由钢种组参数表定义
        p2o5_last：上步工序带来的渣中p2o5(%)，由钢种组参数表定义
        t_fe_f：强搅拌脱硫后渣中t-fe(%)，由渣条件参数表定义
        mno_f：强搅拌脱硫后渣中mno(%)，由渣条件参数表定义
        sio2_f：强搅拌脱硫后渣中sio2(%)，由渣条件参数表定义
        p2o5_f：强搅拌脱硫后渣中p2o5(%)，由渣条件参数表定义
        ws_last：上步工序带来的渣量( kg )，由钢种组参数表定义
        weight:钢水重量(ton)，称量值，来自上步工序
        w_flux:造渣料的投入量，由函数flux_addition_first计算得到
        ws_total_in：钢包中当前渣量(kg/ton)，添加一次造渣料更新一次

    输出：
        b_al_des：强搅拌脱硫al投入量
        ws_exe:下次处理的钢水中的渣量(kg)
    作用：
        计算强搅拌脱硫用al量
    """
    b_al_des = ((t_fe_last - t_fe_f) / (72 * 3) + (mno_last - mno_f) / (71 * 3) + (sio2_last - sio2_f) / (
                60 * 3) * 2 + (p2o5_last - p2o5_f) / (142 * 3) * 5) * 2 * 27 * ws_last
    ws_exe = ws_total_in * weight + w_flux
    return b_al_des, ws_exe