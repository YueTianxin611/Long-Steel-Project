import pymysql
import time
import numpy as np
from composition_prediction import composition_prediction
import pandas as pd

# 钙丝排在type的第一位
def com_predict(alloyX,steel_id, element, wire_type, alloyXw, weight, x_concent,
                   flux_addition_done,s_molten_last, s_total_des_time,s_molten_ini,
                   s_dregs_ini, ws_total_in, w_flux, s_molten_ini_before, s_dregs_ini_before,ws_total_before):

    # 进行成分预测的相关计算
    dict_predict = composition_prediction_api(steel_id,alloyX,element,wire_type,alloyXw,weight,x_concent,
                                              flux_addition_done, s_molten_last,s_total_des_time,s_molten_ini,
                                              s_dregs_ini,ws_total_in,w_flux,s_molten_ini_before,s_dregs_ini_before,
                                              ws_total_before)
    if dict_predict==-1:
        return -1
    else:
        data_list=[dict_predict]

    data_file = make_excel(data_list)

    return data_file

def read_sql_composition_prediction(steel_id,alloy_addition,element,wire_type,alloyxw_addition,weight,x_concent,
                                    flux_addition_done, s_molten_last,s_total_des_time,s_molten_ini, s_dregs_ini,
                                    ws_total_in,w_flux,s_molten_ini_before,s_dregs_ini_before,ws_total_before):
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
    dict['alloyX'] = np.array((alloy_addition))

    dict['alloyXw'] = np.array((alloyxw_addition))


    # 从PARA_STEEL_GROUP_PARAMETERS(钢种组参数表)中读取y
    y=[]
    for i in range(len(element)):
        sql_cmd = 'SELECT Yi_' + element[i] + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
        cursor.execute(sql_cmd)
        y.append(cursor.fetchall()[0][0])
    dict['y'] = np.array((y))

    # 从PARA_WIRE_COMPONENT(丝线成分表)中读取cw
    cw=np.zeros((len(element),len(wire_type)))
    for i in range(len(wire_type)):
        for j in range(len(element)):
            sql_cmd = 'SELECT ' + element[j] + ' from PARA_WIRE_COMPONENT where wire_type = "' + wire_type[i]+'"'
            cursor.execute(sql_cmd)
            val=cursor.fetchall()[0][0]
            cw[j][i]=val
    dict['cw'] = np.array(cw)

    # 从PARA_STEEL_GROUP_PARAMETERS(钢种组参数表)中读取yw
    yw = []
    for i in range(len(element)):
        sql_cmd = 'SELECT yw_' + element[i] + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
        cursor.execute(sql_cmd)
        yw.append(cursor.fetchall()[0][0])
    dict['yw'] = np.array((yw))

    dict['weight'] = weight

    dict['x_concent'] = np.array(x_concent)

    # 从PARA_STEEL_GROUP_PARAMETERS(钢种组参数表)中读取x_loss
    x_loss = []
    for i in range(len(element)):
        sql_cmd = 'SELECT delta_loss_' + element[i] + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(
            group_id)
        cursor.execute(sql_cmd)
        x_loss.append(cursor.fetchall()[0][0])
    dict['x_loss'] = x_loss

    dict['flux_addition_done'] = flux_addition_done

    dict['s_molten_last'] = s_molten_last

    # 从PARA_STEEL_GROUP_PARAMETERS(钢种组参数表)中读取delta_loss_S
    sql_cmd = 'SELECT delta_loss_S from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    dict['s_loss'] = cursor.fetchall()[0][0]

    dict['s_total_des_time'] = s_total_des_time

    sql_cmd = 'SELECT S_time_Des_std from PARA_SLAG_FLUX_PARAMETERS'
    cursor.execute(sql_cmd)
    dict['s_time_des_std'] = cursor.fetchall()[0][0]


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
    sql_cmd = 'SELECT s_time_des_std from PARA_SLAG_FLUX_PARAMETERS where S_upp = ' + str(S_upp) \
            + ' and flux_syn_type = "' + str(flux_syn_type) + '"'
    cursor.execute(sql_cmd)
    dict['s_time_des_std'] = cursor.fetchall()[0][0]

    dict['s_molten_ini'] = s_molten_ini

    dict['s_dregs_ini'] = s_dregs_ini

    dict['ws_total_in'] = ws_total_in

    # 从PARA_SLAG_FLUX_PARAMETERS(渣条件参数表)中读取ls
    sql_cmd = 'SELECT Ls from PARA_SLAG_FLUX_PARAMETERS where S_upp = ' + str(S_upp) \
            + ' and flux_syn_type = "' + str(flux_syn_type) + '"'
    cursor.execute(sql_cmd)
    dict['ls'] = cursor.fetchall()[0][0]

    dict['w_flux'] = w_flux

    dict['s_molten_ini_before'] = s_molten_ini_before

    dict['s_dregs_ini_before'] = s_dregs_ini_before

    dict['ws_total_before'] = ws_total_before


    sql_cmd = 'SELECT alloy_type from PARA_ALLOY_COMPONENT'
    cursor.execute(sql_cmd)
    alloy_type = np.array(cursor.fetchall())
    alloy_id = alloy_type
    c=[]
    for i in range(len(element)):
        list = []
        for j in range(len(alloy_id)):
            sql_cmd = 'SELECT ' + element[i] + ' from PARA_ALLOY_COMPONENT where alloy_type = "' + str(alloy_id[j][0]) + '"'
            cursor.execute(sql_cmd)
            list.append(cursor.fetchall()[0][0])
        c.append(list)
    dict['c'] = np.array((c))
    return dict

def composition_prediction_api(steel_id,alloy_addition_value,element,wire_type,alloyxw_addition,weight,x_concent,flux_addition_done, s_molten_last,s_total_des_time,
                                    s_molten_ini, s_dregs_ini,ws_total_in,w_flux,s_molten_ini_before,s_dregs_ini_before,ws_total_before):

    # 读取模型输入数据
    read_dict = read_sql_composition_prediction(steel_id,alloy_addition_value,element,wire_type,alloyxw_addition,weight,
                                                x_concent,flux_addition_done, s_molten_last,s_total_des_time,
                                    s_molten_ini, s_dregs_ini,ws_total_in,w_flux,s_molten_ini_before,s_dregs_ini_before,
                                                ws_total_before)

    # 计算输入模型
    res = composition_prediction(read_dict['c'], read_dict['alloyX'], read_dict['y'],
                                 read_dict['cw'], read_dict['alloyXw'], read_dict['yw'], read_dict['weight'],
                                 read_dict['x_concent'], read_dict['x_loss'], read_dict['flux_addition_done'],
                                 read_dict['s_molten_last'], read_dict['s_loss'], read_dict['s_total_des_time'],
                                 read_dict['s_time_des_std'], read_dict['s_molten_ini'], read_dict['s_dregs_ini'],
                                 read_dict['ws_total_in'], read_dict['ls'], read_dict['w_flux'],
                                 read_dict['s_molten_ini_before'], read_dict['s_dregs_ini_before'],
                                 read_dict['ws_total_before'])

    write_dict = read_dict
    write_dict['steel_id'] = read_dict['steel_id']
    write_dict = read_dict
    write_dict['x_exp'] = res[0]
    write_dict['s_exp'] = res[1]

    return write_dict

def make_excel(data_list):
    res_file = r"./composition_adjustment.xlsx"
    writer = pd.ExcelWriter(res_file)
    data_name_list=['成分预测计算']
    for i in range(len(data_list)):
        matrix = list(data_list[i])
        res_dict=[data_list[i]]
        data=pd.DataFrame(res_dict,columns=matrix)
        data.to_excel(writer, sheet_name=data_name_list[i],index= False)
    writer.save()
    return res_file