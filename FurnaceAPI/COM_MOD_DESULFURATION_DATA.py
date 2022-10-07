import pymysql
import time
from desulfuration import desulfuration
from desulfuration_t import desulfuration_t
import pandas as pd

# 读取输入变量储存到一个dict里面
def read_sql_desulfuration(steel_id,weight,w_flux,ws_total_in):
    """
    :param
    db_con:数据库连接设定
    :return: 一个包含各个输入的字典
    """

    # 链接数据库
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL_PARA",
                             charset='utf8', use_unicode=True)

    cursor = db_con.cursor()

    dict = {}

    dict['steel_id'] = steel_id

    # 从PARA_STEEL_GROUP（钢种分组表）中读取group_id
    sql_cmd = 'SELECT group_id from PARA_STEEL_GROUP where steel_id="' + steel_id + '"'
    cursor.execute(sql_cmd)
    group_id = cursor.fetchall()[0][0]

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取各个变量
    list = ['t_fe_last', 'mno_last', 'sio2_last', 'p2o5_last', 'ws_last']
    for i in range(len(list)):
        sql_cmd = 'SELECT ' + list[i] + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
        cursor.execute(sql_cmd)
        dict[list[i]] = cursor.fetchall()[0][0]

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取flux_synthetic_assigned
    sql_cmd = 'SELECT flux_synthetic_assigned from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    flux_synthetic_assigned = cursor.fetchall()[0][0]
    if flux_synthetic_assigned == 0:
        flux_synthetic_assigned = False
    else:
        flux_synthetic_assigned = True

    # 为读取渣条件参数表准备条件
    if flux_synthetic_assigned == True:
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
    list = ['t_fe_f', 'mno_f', 'sio2_f', 'p2o5_f']
    for i in range(len(list)):
        sql_cmd = 'SELECT ' + list[i] + ' from PARA_SLAG_FLUX_PARAMETERS where S_upp = ' + str(S_upp) \
                  + ' and flux_syn_type = "' + str(flux_syn_type) + '"'
        cursor.execute(sql_cmd)
        dict[list[i]] = cursor.fetchall()[0][0]

    dict['weight'] = weight

    dict['w_flux']=w_flux

    # 从LF_CURRENT_STATUS（跟模型计算相关的当前状态）中读取ws_total_in
    dict['ws_total_in'] = ws_total_in

    db_con.close()

    return dict


def read_sql_desulfuration_t(steel_id,weight,w_flux_t,s_des,ws_total_in):
    """
    :param
    db_con:数据库连接设定
    :return: 一个包含各个输入的字典
    """

    # 链接数据库
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL_PARA",
                             charset='utf8', use_unicode=True)

    cursor = db_con.cursor()

    dict = {}

    dict['steel_id'] = steel_id

    # 从PARA_STEEL_GROUP（钢种分组表）中读取group_id
    sql_cmd = 'SELECT group_id from PARA_STEEL_GROUP where steel_id="' + steel_id + '"'
    cursor.execute(sql_cmd)
    group_id = cursor.fetchall()[0][0]

    # 从PARA_STEEL_COMPONENT（钢种成分表）中读取 S_aim
    sql_cmd = 'SELECT s_aim from PARA_STEEL_COMPONENT where steel_id = "' + steel_id + '"'
    cursor.execute(sql_cmd)
    dict['s_aim'] = cursor.fetchall()[0][0]

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取中读取各个变量
    list = ['t_fe_last','mno_last', 'sio2_last', 'p2o5_last', 'ws_last']
    for i in range(len(list)):
        sql_cmd = 'SELECT '+ list[i] + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
        cursor.execute(sql_cmd)
        dict[list[i]] = cursor.fetchall()[0][0]

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取flux_synthetic_assigned
    sql_cmd = 'SELECT flux_synthetic_assigned from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    flux_synthetic_assigned = cursor.fetchall()[0][0]
    if flux_synthetic_assigned == 0:
        flux_synthetic_assigned = False
    else:
        flux_synthetic_assigned = True

    # 为读取渣条件参数表准备条件
    if flux_synthetic_assigned == True:
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
    list = ['t_fe_f', 'mno_f', 'sio2_f', 'p2o5_f']
    for i in range(len(list)):
        sql_cmd = 'SELECT '+ list[i] + ' from PARA_SLAG_FLUX_PARAMETERS where S_upp = ' + str(S_upp) \
                  + ' and flux_syn_type = "' + str(flux_syn_type) +'"'
        cursor.execute(sql_cmd)
        dict[list[i]] = cursor.fetchall()[0][0]
    dict['weight']=weight

    dict['ws_total_in'] = ws_total_in

    # 从LF_MOD_CAL_RESULT(模型计算结果)中读取w_flux_t
    dict['w_flux_t'] = w_flux_t

    # 有问题
    dict['s_des'] = s_des

    db_con.close()

    return dict


def time_des(val):
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL_PARA",
                             charset='utf8', use_unicode=True)

    cursor = db_con.cursor()
    sql_cmd = 'SELECT Ws_exe_T from PARA_DESULFURATION_S_TIME '
    cursor.execute(sql_cmd)
    ws_exe_t_list = cursor.fetchall()
    ws_exe_t_list_sort = []
    for n in ws_exe_t_list:
        ws_exe_t_list_sort.append(n[0])
    ws_exe_t_list_sort.append(val)
    ws_exe_t_list_sort.sort()
    Ws_exe_T_loc = ws_exe_t_list_sort.index(val)
    Ws_exe_t = ws_exe_t_list_sort[int(Ws_exe_T_loc + 1)]
    # 根据ws_exe在强搅拌脱硫后搅拌时间表中查出时间值赋予式s_time_des
    sql_cmd = 'SELECT S_time_Des_T from PARA_DESULFURATION_S_TIME where Ws_exe_T="' + str(Ws_exe_t) + '"'
    cursor.execute(sql_cmd)
    s_time_des = cursor.fetchall()[0][0]

    db_con.close()
    return s_time_des


def make_excel(data1, data2):
    res_file = r"./desulfuration.xlsx"
    writer = pd.ExcelWriter(res_file)
    matrix = list(data1)
    res_dict = [data1]
    data1 = pd.DataFrame(res_dict, columns= matrix)
    matrix2 = list(data2)
    res_dict2 = [data2]
    data2 = pd.DataFrame(res_dict2, columns= matrix2)
    data1.to_excel(writer, sheet_name='强搅拌脱硫计算',index= False)
    data2.to_excel(writer, sheet_name='强搅拌脱硫温度计算',index= False)
    writer.save()
    return res_file


# 定义脱硫接口函数
def desulfuration_api(steel_id,weight,w_flux,ws_total_in,w_flux_t,s_des):
    # 读取模型输入数据
    read_dict = read_sql_desulfuration(steel_id,weight,w_flux,ws_total_in)

    # 计算输入模型
    res = desulfuration(read_dict['t_fe_last'], read_dict['t_fe_f'], read_dict['mno_last'], read_dict['mno_f'],
                        read_dict['sio2_last'], read_dict['sio2_f'], read_dict['p2o5_last'], read_dict['p2o5_f'],
                        read_dict['ws_last'], read_dict['ws_total_in'], read_dict['weight'], read_dict['w_flux'])

    write_dict = read_dict
    write_dict['b_al_des'] = res[0]
    write_dict['ws_exe'] = res[1]
    ws_exe = res[1]
    write_dict['s_time_des'] = time_des(ws_exe)

    # 读取模型输入数据
    read_dict = read_sql_desulfuration_t(steel_id,weight,w_flux_t,s_des,ws_total_in)
    # 计算温度计算输入模型
    res_t = desulfuration_t(read_dict['s_aim'], read_dict['s_des']
                            , read_dict['t_fe_last'], read_dict['t_fe_f'], read_dict['mno_last']
                            , read_dict['mno_f'], read_dict['sio2_last'], read_dict['sio2_f'], read_dict['p2o5_last']
                            , read_dict['p2o5_f'], read_dict['ws_last'], read_dict['ws_total_in'], read_dict['weight']
                            , read_dict['w_flux_t'])
    if isinstance(res,str) == True:
        return res
    else:
        write_dict_t = read_dict
        write_dict_t['b_al_des_t'] = res_t[0]
        write_dict_t['ws_exe_t'] = res_t[1]
        ws_exe_t = res_t[1]
        write_dict_t['s_time_des_t'] = time_des(ws_exe_t)
        # 生成excel文件
        res_file = make_excel(write_dict,write_dict_t)
        return res_file


if __name__ == "__main__":
    res_file = desulfuration_api('Q345',1,2,3,4,2)
