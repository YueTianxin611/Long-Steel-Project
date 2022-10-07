# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 09:38:33 2019

@author: 018614
"""


# 温度计算用强搅拌脱硫
def desulfuration_t(s_aim, s_des, t_fe_last, t_fe_f, mno_last, mno_f, sio2_last, sio2_f, p2o5_last, p2o5_f, ws_last,
                    ws_total_in, weight, w_flux_t):
    """
    输入：
        s_aim：钢种的S成分目标值(%)，由钢种成分表定义
        s_des：强搅拌脱硫处理的基准值(%)	，设定值，暂定0.0020%
        t_fe_last：上步工序带来的渣中t-fe(%)，由钢种组参数表定义
        mno_last：上步工序带来的渣中mno(%)，由钢种组参数表定义
        sio2_last：上步工序带来的渣中sio2(%)，由钢种组参数表定义
        p2o5_last：上步工序带来的渣中p2o5(%)，由钢种组参数表定义
        t_fe_f：强搅拌脱硫后渣中t-fe(%)，由渣条件参数表定义
        mno_f：强搅拌脱硫后渣中mno(%)，由渣条件参数表定义
        sio2_f：强搅拌脱硫后渣中sio2(%)，由渣条件参数表定义
        p2o5_f：强搅拌脱硫后渣中p2o5(%)	，由渣条件参数表定义
        ws_last：上步工序带来的渣量( kg )，由钢种组参数表定义
        weight:钢水重量(ton)，称量值，来自上步工序
        ws_total_in：钢包中当前渣量(kg/ton)，由函数flux_addition_first计算得到
        w_flux_t:造渣料的投入量
        b_al_t:温度计算用成分调整al,由丝线和合金铁调整两部分组成

    输出：
        b_al_des_t：强搅拌脱硫al投入量，计算得到
        ws_exe_t:下次处理的钢水中的渣量(kg)
    作用：
        温度计算用计算强搅拌脱硫用al量
    """
    if s_aim < s_des:
        b_al_des_t = ((t_fe_last - t_fe_f) / (72 * 3) + (mno_last - mno_f) / (71 * 3) + (sio2_last - sio2_f) / (
                    60 * 3) * 2 + (p2o5_last - p2o5_f) / (142 * 3) * 5) * 2 * 27 * ws_last
        ws_exe_t = ws_total_in * weight + w_flux_t
    else:
        return '温度计算用脱硫计算失败'
    return b_al_des_t, ws_exe_t