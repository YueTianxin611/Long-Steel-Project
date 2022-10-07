# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 11:38:44 2019

@author: 018614
"""


# 2.3.6.3喂丝计算
# 由于钢水中的[ca]调整只有通过喂入钙丝实现，故钙丝计算可以自动进行
def wire_feeding_ca(delta_ca_aim, ca_aim, ca, ca_loss, weight, yw_ca, cw_ca, w_wire_casi, line_number, wf_vca):
    """
    输入：
        delta_ca_aim:成分粗调整时目标值下方调整带(%),由钢种组参数表定义
        ca_aim:钢种的成分目标值(%),由钢种成分表定义
        ca:钢水中的成分测定值(%),来自分析计算机
        ca_loss:成分调整时的损失量(%),由钢种组参数表定义
        weight:钢水重量(ton),来自上步工序或人工输入
        yw_ca:喂丝时的ca成分收得率(%),由钢种组参数表定义
        cw_ca:丝线的ca成分含有率(%),由丝线成分表定义
        w_wire_casi:丝线单位长度的重量(kg/m),由丝线成分表定义
        line_number:同时喂入同种丝线的数量,来自L1设定值
        wf_vca:丝线喂入速度(m/分),由丝线成分表定义

    输出：
        casi_wire:丝的添加重量(kg)
        wire_strand:对应流号的丝线添加长度(m)
        p_time_strand:对应流号的丝线喂入时间(分)
    作用：
        喂丝调整ca元素
    """
    if delta_ca_aim == 0 or ca_aim - ca <= delta_ca_aim:
        if ca_aim != 0:
            casi_wire = (ca_aim - ca + ca_loss) * 10 * weight / (yw_ca * cw_ca)
            wire_strand = casi_wire / w_wire_casi / line_number
            p_time_strand = casi_wire / w_wire_casi / wf_vca / line_number
    return casi_wire, wire_strand, p_time_strand


# 其它成分调整时：选择是否采用丝线调整成分由操作工人在level1画面上决定(包括al、ti、C三种成分)
def wire_feeding_others(element_aim, element, element_loss, weight, yw_element, cw_element, w_wire_element, line_number,
                        wf_v_element):
    """
    输入：
        element_aim:钢种的成分目标值(%),由钢种成分表定义
        element:钢水中的成分测定值(%),来自分析计算机
        element_loss:成分调整时的损失量(%),由钢种组参数表定义
        weight:钢水重量(ton),来自上步工序或人工输入
        yw_element:喂丝时的element成分收得率(%),由钢种组参数表定义
        cw_element:丝线的element成分含有率(%),由丝线成分表定义
        w_wire_element:丝线单位长度的重量(kg/m),由丝线成分表定义
        line_number:同时喂入同种丝线的数量,来自L1设定值
        wf_v_element:丝线喂入速度(m/分),由丝线成分表定义

    输出：
        element_wire:丝的添加重量(kg)
        wire_strand:对应流号的丝线添加长度(m)
        p_time_strand:对应流号的丝线喂入时间(分)
    作用：
        喂丝调整element元素
    """
    if element_aim != 0:
        if element_aim - element > 0:
            element_wire = (element_aim - element + element_loss) * 10 * weight / (yw_element * cw_element)
        else:
            element_wire = 0
        wire_strand = element_wire / w_wire_element / line_number
        p_time_strand = element_wire / w_wire_element / wf_v_element / line_number
    return element_wire, wire_strand, p_time_strand


# 计算喂丝搅拌时间
m = ['Ca', 'Ti']  # L1指定的通过喂丝进行调整的成分


def wire_time_t(delta_ca_aim, element_aim, element, element_loss, weight, yw_element, cw_element, w_wire_element,
                line_number, wf_v_element):
    """
    输入：
        delta_ca_aim:成分粗调整时目标值下方调整带(%),由钢种组参数表定义
        element_aim:钢种的成分目标值(%),由钢种成分表定义,此处为使用丝线进行成分调整的元素组成的字典
        element:钢水中的成分测定值(%),来自分析计算机
        element_loss:成分调整时的损失量(%),由钢种组参数表定义
        weight:钢水重量(ton),来自上步工序或人工输入
        yw_element:喂丝时的ca成分收得率(%),由钢种组参数表定义
        cw_element:丝线的ca成分含有率(%),由丝线成分表定义
        w_wire_element:丝线单位长度的重量(kg/m),由丝线成分表定义
        line_number:同时喂入同种丝线的数量,来自L1设定值
        wf_v_element:丝线喂入速度(m/分),由丝线成分表定义

    输出：
        s_time_wire_t:温度计算用喂丝全搅拌时间(分)
    作用：
        温度计算用喂丝搅拌时间
    """
    wire_strand = [0]*len(m)
    element_wire = [0]*len(m)
    s_time_strand = [0]*len(m)
    p_time_strand = [0]*len(m)
    element_wire[0], wire_strand[0], p_time_strand[0] = wire_feeding_ca(delta_ca_aim, element_aim['Ca'], element['Ca'],
                                                                        element_loss['Ca'], weight, yw_element['Ca'],
                                                                        cw_element['Ca'], w_wire_element['Ca'],
                                                                        line_number['Ca'], wf_v_element['Ca'])
    # 根据element_wire[0]在喂丝后搅拌时间表中查出s_time_wca
    s_time_wca = 1
    s_time_strand[0] = s_time_wca

    m.remove('Ca')
    for i in range(len(m)):
        element_wire[i + 1], wire_strand[i + 1], p_time_strand[i + 1] = wire_feeding_others(element_aim[m[i]],
                                                                                            element[m[i]],
                                                                                            element_loss[m[i]], weight,
                                                                                            yw_element[m[i]],
                                                                                            cw_element[m[i]],
                                                                                            w_wire_element[m[i]],
                                                                                            line_number[m[i]],
                                                                                            wf_v_element[m[i]])
        # 根据element_wire[i+1]在喂丝后搅拌时间表中查出s_time_wothers
        s_time_wothers = 1
        s_time_strand[i + 1] = s_time_wothers
    time_list = s_time_strand + p_time_strand
    s_time_wire_t = max(time_list)
    return s_time_wire_t