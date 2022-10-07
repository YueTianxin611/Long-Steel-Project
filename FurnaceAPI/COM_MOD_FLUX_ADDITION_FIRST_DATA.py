# -*- coding: utf-8 -*-

import pymysql
import time
from flux_addition_first import flux_addition_first
from flux_addition_t import flux_addition_t
import pandas as pd

# 读取输入变量储存到一个dict里面
def read_sql_flux_addition_first(steel_id,s_total_des_time,weight,flux_addition_done):
    """
    :param
    db_con:数据库连接设定
    :return: 一个包含各个输入的字典
    """

    # 链接数据库
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL",
                             charset='utf8', use_unicode=True)

    cursor = db_con.cursor()

    dict = {}

    # 从PARA_STEEL_GROUP（钢种分组表）中读取group_id
    sql_cmd = 'SELECT group_id from PARA_STEEL_GROUP where steel_id="' + steel_id + '"'
    cursor.execute(sql_cmd)
    group_id = cursor.fetchall()[0][0]

    dict['steel_id'] = steel_id
    dict['s_total_des_time'] = s_total_des_time
    dict['weight'] = weight

    if flux_addition_done == 1:
        dict['flux_addition_done'] = True
    else:
        dict['flux_addition_done'] = False

    # 从PARA_TEMP_PARAMETERS（温度计算相关参数表）中读取eeff
    sql_cmd = 'SELECT eeff from PARA_TEMP_PARAMETERS'
    cursor.execute(sql_cmd)
    dict['eeff'] = cursor.fetchall()[0][0]

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取ws_last
    sql_cmd = 'SELECT ws_last from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    dict['ws_last'] = cursor.fetchall()[0][0]


    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取flux_synthetic_assigned
    sql_cmd = 'SELECT flux_synthetic_assigned from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    dict['flux_synthetic_assigned'] = cursor.fetchall()[0][0]

    if dict['flux_synthetic_assigned'] == 1:
        dict['flux_synthetic_assigned'] = True
    else:
        dict['flux_synthetic_assigned'] = False

    # 为读取渣条件参数表准备条件
    if dict['flux_synthetic_assigned'] == True:
        flux_syn_type = 'syn1'
        S_upp = 0
        # flux_syn_type 未想好输入类型
    else:
        # 从PARA_STEEL_COMPONENT（钢种成分表）中读取 S_upp
        sql_cmd = 'SELECT S_upp from PARA_STEEL_COMPONENT where steel_id = "' + steel_id + '"'
        cursor.execute(sql_cmd)
        S_upp = cursor.fetchall()[0][0]
        flux_syn_type = 'no'
        sql_cmd = 'SELECT S_upp from PARA_SLAG_FLUX_PARAMETERS  where flux_syn_type = "no"'
        cursor.execute(sql_cmd)
        S_upp_list = cursor.fetchall()
        S_upp_list_sort = []
        for n in S_upp_list:
            S_upp_list_sort.append(n[0])
        S_upp_list_sort.append(S_upp)
        S_upp_list_sort.sort()
        S_upp_loc = S_upp_list_sort.index(S_upp)
        S_upp = S_upp_list_sort[int(S_upp_loc + 1)]

    # 从PARA_SLAG_FLUX_PARAMETERS（渣条件参数表）中读取各个变量
    list = ['s_time_des_std', 'cmf_caf2', 'cmf_cao', 'ws_minimum']
    for i in range(len(list)):
        sql_cmd = 'SELECT '+ list[i] + ' from PARA_SLAG_FLUX_PARAMETERS where S_upp = ' + str(S_upp) \
                  + ' and flux_syn_type = "' + str(flux_syn_type) + '"'
        cursor.execute(sql_cmd)
        dict[list[i]] = cursor.fetchall()[0][0]

    # 从PARA_SLAG_FLUX_PARAMETERS（渣条件参数表）中读取cmf_synthetic
    sql_cmd = 'SELECT Cmf_flux_syn from PARA_SLAG_FLUX_PARAMETERS where S_upp = ' + str(S_upp) \
              + ' and flux_syn_type = "' + str(flux_syn_type) + '"'
    cursor.execute(sql_cmd)
    dict['cmf_synthetic'] = cursor.fetchall()[0][0]

    Ws_exe_T_1 = dict['ws_last']
    sql_cmd = 'SELECT Ws_exe_T from PARA_SLAG_MELT_TAP '
    cursor.execute(sql_cmd)
    ws_exe_t_list = cursor.fetchall()
    ws_exe_t_list_sort = []
    for n in ws_exe_t_list:
        ws_exe_t_list_sort.append(n[0])
    ws_exe_t_list_sort.append(Ws_exe_T_1)
    ws_exe_t_list_sort.sort()
    Ws_exe_T_loc = ws_exe_t_list_sort.index(Ws_exe_T_1)
    Ws_exe_T_1 = ws_exe_t_list_sort[int(Ws_exe_T_loc + 1)]

    # 从PARA_SLAG_MELT_TAP（造渣料溶解TAP表）中读取ps
    sql_cmd = 'SELECT Ps from PARA_SLAG_MELT_TAP where Ws_exe_T =' + str(Ws_exe_T_1)
    cursor.execute(sql_cmd)
    dict['Ps'] = cursor.fetchall()[0][0]

    return dict

# 定义除氧接口函数
def flux_addition_first_api(steel_id,s_total_des_time,weight,flux_addition_done):
    # 读取模型输入数据
    read_dict = read_sql_flux_addition_first(steel_id,s_total_des_time,weight,flux_addition_done)

    # 计算输入模型
    res = flux_addition_first(read_dict['flux_addition_done'], read_dict['s_total_des_time'], read_dict['s_time_des_std'],
                              read_dict['ws_last'], read_dict['weight'], read_dict['flux_synthetic_assigned'],
                        read_dict['cmf_caf2'], read_dict['cmf_cao'], read_dict['cmf_synthetic'],
                              read_dict['eeff'], read_dict['Ps'], read_dict['ws_minimum'])
    if isinstance(res,str) == True:
        return res
    else:
        write_dict = read_dict
        write_dict['wflux_synthetic'] = res[0]
        write_dict['wflux_cao'] = res[1]
        write_dict['wflux_caf2'] = res[2]
        write_dict['ws_total_in'] = res[3]
        write_dict['ws_total_before'] = res[4]
        write_dict['ws_exe'] = res[5]
        write_dict['qs_melt1'] = res[6]
        write_dict['ts1'] = res[7]
        W_flux_T=res[0]+res[1]+res[2]
        write_dict['s_time_flux'] = time_flux(W_flux_T)

        write_dict1 = write_dict

        # 读取模型输入数据
        # 计算温度计算输入模型
        read_dict = read_sql_flux_addition_first(steel_id,s_total_des_time,weight,flux_addition_done)
        res_t = flux_addition_t(read_dict['flux_addition_done'], read_dict['s_total_des_time'], read_dict['s_time_des_std'],
                                read_dict['ws_last'], read_dict['weight'], read_dict['flux_synthetic_assigned'],
                                read_dict['cmf_caf2'], read_dict['cmf_cao'], read_dict['cmf_synthetic'],
                                read_dict['eeff'], read_dict['Ps'], read_dict['ws_minimum'])
        if isinstance(res_t, str) == True:
            return res_t
        else:
            write_dict_t = read_dict
            write_dict_t['wflux_synthetic_t'] = res_t[0]
            write_dict_t['wflux_cao_t'] = res_t[1]
            write_dict_t['wflux_caf2_t'] = res_t[2]
            write_dict_t['ws_total_in'] = res_t[3]
            write_dict_t['ws_total_before'] = res_t[4]
            write_dict_t['ws_exe_t'] = res_t[5]
            write_dict_t['qs_melt1_t'] = res_t[6]
            write_dict_t['ts1_t'] = res_t[7]
            w_flux_t = res_t[0] + res_t[1] + res_t[2]
            write_dict_t['s_time_flux_t'] = time_flux(w_flux_t)

            write_dict2 = write_dict_t

            res_file = make_excel(write_dict1, write_dict2)

            return res_file

def time_flux(w_flux_T):
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL_PARA",
                             charset='utf8', use_unicode=True)
    cursor = db_con.cursor()

    sql_cmd = 'SELECT W_flux_T from PARA_SLAG_S_TIME '
    cursor.execute(sql_cmd)
    ws_exe_t_list = cursor.fetchall()
    ws_exe_t_list_sort = []
    for n in ws_exe_t_list:
        ws_exe_t_list_sort.append(n[0])
    ws_exe_t_list_sort.append(w_flux_T)
    ws_exe_t_list_sort.sort()
    Ws_exe_T_loc = ws_exe_t_list_sort.index(w_flux_T)
    W_flux_t = ws_exe_t_list_sort[int(Ws_exe_T_loc + 1)]

    # 根据W-flux，从造渣料后搅拌时间表中查出时间值赋予s_time_flux
    sql_cmd = 'SELECT S_time_flux_T from PARA_SLAG_S_TIME where W_flux_T="' + str(W_flux_t) +'"'
    cursor.execute(sql_cmd)
    s_time_flux = cursor.fetchall()[0][0]

    return s_time_flux

def make_excel(data1, data2):
    res_file = r"./flux_addition_first.xlsx"
    writer = pd.ExcelWriter(res_file)
    matrix = list(data1)
    res_dict = [data1]
    data1 = pd.DataFrame(res_dict, columns=matrix)
    matrix2 = list(data2)
    res_dict2 = [data2]
    data2 = pd.DataFrame(res_dict2, columns=matrix2)
    data1.to_excel(writer, sheet_name='第一次造渣料计算', index=False)
    data2.to_excel(writer, sheet_name='温度计算用第一次造渣料', index=False)
    writer.save()
    return res_file

if __name__ == "__main__":
    flux_addition_first_api('Q345',100,10,0)