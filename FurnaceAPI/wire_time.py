# -*- coding: utf-8 -*-
"""
Created on mon Aug 26 15:46:21 2019

@author: CISDI
"""
from wire_feeding_ca import  wire_feeding_ca
from wire_feeding_others import wire_feeding_others
import pymysql

# 计算喂丝搅拌时间
m = ['Ca', 'Ti']  # L1指定的通过喂丝进行调整的成分


def wire_time(delta_ca_aim, element_aim, element, element_loss, weight, yw_element, cw_element, w_wire_element,
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
        s_time_wire:喂丝全搅拌时间(分)
    作用：
        计算喂丝搅拌时间
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
    # 从PARA_WIRE_S_TIME中读取s_time_wca
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL",
                             charset='utf8', use_unicode=True)
    cursor = db_con.cursor()
    sql_cmd = 'SELECT S_time_w_T from PARA_WIRE_S_TIME where W_wire_T = ' + str(element_wire[0]) + ' and wire_type = "CaSi" '
    cursor.execute(sql_cmd)
    s_time_wca = cursor.fetchall()[0][0]

    #s_time_wca = 1
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
        # 从PARA_WIRE_S_TIME中读取s_time_wothers
        db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL",
                                 charset='utf8', use_unicode=True)
        cursor = db_con.cursor()
        # 确定除了Ca的另一个wire_type
        sql_cmd = 'SELECT wire_type from SETUP_WIRE_TYPE'
        cursor.execute(sql_cmd)
        wire_type_1 = cursor.fetchall()[0][0]
        sql_cmd = 'SELECT wire_type from SETUP_WIRE_TYPE'
        cursor.execute(sql_cmd)
        wire_type_2 = cursor.fetchall()[1][0]
        if wire_type_1 == 'CaSi':
            wire_type = wire_type_2
        else:
            wire_type = wire_type_1
        sql_cmd = 'SELECT S_time_w_T from PARA_WIRE_S_TIME where W_wire_T = ' + str(
            element_wire[i+1]) + ' and wire_type = "' + str(wire_type) + '"'
        cursor.execute(sql_cmd)
        s_time_wothers = cursor.fetchall()[0][0]

        #s_time_wothers = 1
        s_time_strand[i + 1] = s_time_wothers
    time_list = s_time_strand + p_time_strand
    s_time_wire = max(time_list)
    return s_time_wire
