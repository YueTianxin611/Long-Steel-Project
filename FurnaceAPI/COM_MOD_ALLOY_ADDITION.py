import pymysql
import time
from alloy_addition import alloy_addition
import numpy as np
from alloy_addition_t import alloy_addition_t
import pandas as pd

# 钙丝排在type的第一位
def alloy_add(b_al_deoxi,fesi_deoxi,steel_id, element_alloy,wire_type, alloyXw, weight, x_concent,
                   list_):

    # 进行合金加料的相关计算
    dict_alloy = alloy_addition_api(b_al_deoxi,fesi_deoxi,steel_id,element_alloy,wire_type,alloyXw,weight,x_concent,list_)

    # 进行温度计算有关的合金加料的相关计算
    dict_alloy_t = alloy_addition_t_api(steel_id, element_alloy, wire_type,alloyXw, weight, x_concent, list_)

    if dict_alloy==-1 or dict_alloy_t==-1:
        return -1
    else:
        data_list=[dict_alloy,dict_alloy_t]

    data_file = make_excel(data_list)
    return data_file

# 定义接口函数
def alloy_addition_api(b_al_deoxi,fesi_deoxi,steel_id,element_alloy,wire_type,alloyXw,weight,x_concent,list_):
    # 读取模型输入数据
    read_dict = read_sql_alloy_addition(steel_id,element_alloy,wire_type,alloyXw,weight,x_concent,list_)

    # 计算输入模型
    res = alloy_addition(read_dict['cw'], read_dict['alloyXw'], read_dict['yw'], read_dict['delta_aim'],
                        read_dict['weight'], read_dict['x_aim'], read_dict['casting_loss'], read_dict['x_concent'],
                        read_dict['x_loss'], read_dict['y'], read_dict['uc'], read_dict['c'])
    if res =='error':
        return -1
    else:
        write_dict = read_dict
        write_dict['s_time_alloy'] = time_alloy(b_al_deoxi,fesi_deoxi,res)
        write_dict['alloyX'] = res
    # 生成excel文件
    # res_file = make_csv(write_dict)
    return write_dict

#alloy_addition_api(20,'Q345',['Al','Cu','Si'],['Al','C'],['Al','C','CaSi','FeSi'],[40.0, 40.0],10,[15,15,15],['billet', 1])

# 读取输入变量储存到一个dict里面
def read_sql_alloy_addition(steel_id,element_alloy,wire_type,alloyXw,weight,x_concent,list_):
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

    dict['element_alloy'] = element_alloy

    dict['list_'] = list_

    # 从PARA_STEEL_GROUP（钢种分组表）中读取group_id
    sql_cmd = 'SELECT group_id from PARA_STEEL_GROUP where steel_id="' + steel_id + '"'
    cursor.execute(sql_cmd)
    group_id = cursor.fetchall()[0][0]

    # element_alloy=['Al','Cu'] 目标元素
    if len(element_alloy) == 1:
        element_alloy_index = element_alloy[0]
        yw_index = 'yw_' + element_alloy[0]
        delta_aim_index = 'delta_aim_' + element_alloy[0]
        delta_loss_index = 'delta_loss_' + element_alloy[0]
        Yi_index = 'Yi_' + element_alloy[0]
    else:
        element_alloy_index = element_alloy[0]
        yw_index = 'yw_' + element_alloy[0]
        delta_aim_index = 'delta_aim_' + element_alloy[0]
        delta_loss_index = 'delta_loss_' + element_alloy[0]
        Yi_index = 'Yi_' + element_alloy[0]
        for i in range(len(element_alloy)-1):
            element_alloy_index += ',' + element_alloy[i+1]
            yw_index += ', yw_' + element_alloy[i + 1]
            delta_aim_index += ', delta_aim_' + element_alloy[i + 1]
            delta_loss_index += ',delta_loss_' + element_alloy[i + 1]
            Yi_index += ',Yi_' + element_alloy[i + 1]

    wire_type = np.array(wire_type)
    dict['wire_type'] = wire_type

    # 从PARA_ALLOY_COMPONENT(铁合金成分表)中读取alloy_type
    sql_cmd = 'SELECT alloy_type from PARA_ALLOY_COMPONENT'
    cursor.execute(sql_cmd)
    alloy_type = np.array(cursor.fetchall())
    dict['alloy_type'] = alloy_type

    # 从PARA_WIRE_COMPONENT（丝线成分表）中读取cw
    cw=np.zeros((len(element_alloy),len(wire_type)))
    for i in range(len(wire_type)):
        for j in range(len(element_alloy)):
            sql_cmd = 'SELECT ' + element_alloy[j] + ' from PARA_WIRE_COMPONENT where wire_type = "' + wire_type[i]+'"'
            cursor.execute(sql_cmd)
            val=cursor.fetchall()[0][0]
            cw[j][i]=val
    dict['cw'] = np.array(cw)

    dict['alloyXw'] = np.array((alloyXw))

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取yw
    sql_cmd = 'SELECT ' + yw_index + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    yw = cursor.fetchall()
    dict['yw'] = np.array((yw[0]))

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取delta_aim
    sql_cmd = 'SELECT ' + delta_aim_index + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    delta_aim = cursor.fetchall()
    dict['delta_aim'] = np.array(delta_aim[0])

    dict['weight'] = weight

    # 从PARA_STEEL_COMPONENT（钢种成分表）中读取x_aim
    x_aim = []
    for i in range(len(element_alloy)):
        if element_alloy[i][0] in ['B', 'Re', 'Sn', 'Te', 'N', 'Mo']:
            x_aim.append(0)
        else:
            sql_cmd = 'SELECT ' + element_alloy[i] +  '_aim from PARA_STEEL_COMPONENT where steel_id = "' + str(steel_id) + '"'
            cursor.execute(sql_cmd)
            temporary = cursor.fetchall()[0][0]
            x_aim.append(temporary)
    dict['x_aim'] = np.array((x_aim))

    dict['x_concent'] = np.array(x_concent)

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取x_loss
    sql_cmd = 'SELECT ' + delta_aim_index + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    x_loss = cursor.fetchall()
    dict['x_loss'] = np.array(x_loss[0])

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取y
    sql_cmd = 'SELECT ' + Yi_index + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    Yi_index = cursor.fetchall()
    dict['y'] = np.array(Yi_index[0])

    # 从PARA_ALLOY_COMPONENT（铁合金成分表）中读取uc
    uc = []
    for i in range(len(alloy_type)):
        sql_cmd = 'SELECT uc from PARA_ALLOY_COMPONENT where alloy_type = "' + str(alloy_type[i][0]) + '"'
        cursor.execute(sql_cmd)
        uc.append(cursor.fetchall()[0][0])
    dict['uc'] = np.array(uc)

    # 从PARA_ALLOY_COMPONENT（铁合金成分表）中读取c
    sql_cmd = 'SELECT ' + element_alloy_index + ' from PARA_ALLOY_COMPONENT'
    cursor.execute(sql_cmd)
    c = cursor.fetchall()
    c = np.array((c))
    dict['c'] = np.transpose(c)

    # 从PARA_CASTING_LOSS(目标成分补偿表)中读取casting_loss
    casting_loss = []
    for i in range(len(element_alloy)):
        if element_alloy[i][0] in ['Al', 'Ca', 'Ti']:
            sql_cmd = 'SELECT casting_loss_' + element_alloy[i][0] + ' from PARA_CASTING_LOSS where casting_type = "' + str(
                list_[0]) + '" and is_first_batch = ' + str(list_[1])
            cursor.execute(sql_cmd)
            temporary = cursor.fetchall()[0][0]
            casting_loss.append(temporary)
        else:
            casting_loss.append(0)
    dict['casting_loss'] = np.array((casting_loss))

    # 关闭数据库链接
    db_con.close()

    return dict

def time_alloy(b_al_deoxi,fesi_deoxi,alloy):
    # 链接数据库
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL_PARA",
                             charset='utf8', use_unicode=True)

    # 申请数据游标
    cursor = db_con.cursor()
    w_alloy = b_al_deoxi+fesi_deoxi+sum(alloy)
    sql_cmd = 'SELECT W_alloy_T from PARA_ALLOY_S_TIME '
    cursor.execute(sql_cmd)
    ws_exe_t_list = cursor.fetchall()
    ws_exe_t_list_sort = []
    for n in ws_exe_t_list:
        ws_exe_t_list_sort.append(n[0])
    ws_exe_t_list_sort.append(w_alloy)
    ws_exe_t_list_sort.sort()
    Ws_exe_T_loc = ws_exe_t_list_sort.index(w_alloy)
    w_alloy = ws_exe_t_list_sort[int(Ws_exe_T_loc + 1)]

    # 根据w_alloy，在铁合金后搅拌时间表中查出s_time_alloy（铁合金投入后的后搅拌时间）
    sql_cmd = 'SELECT S_time_alloy_T from PARA_ALLOY_S_TIME where W_alloy_T = ' + str(w_alloy)
    cursor.execute(sql_cmd)
    s_time_alloy = cursor.fetchall()[0][0]

    return s_time_alloy

def time_alloy_t(w_alloy):
    # 链接数据库
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL_PARA",
                             charset='utf8', use_unicode=True)

    # 申请数据游标
    cursor = db_con.cursor()

    sql_cmd = 'SELECT W_alloy_T from PARA_ALLOY_S_TIME '
    cursor.execute(sql_cmd)
    ws_exe_t_list = cursor.fetchall()
    ws_exe_t_list_sort = []
    for n in ws_exe_t_list:
        ws_exe_t_list_sort.append(n[0])
    ws_exe_t_list_sort.append(w_alloy)
    ws_exe_t_list_sort.sort()
    Ws_exe_T_loc = ws_exe_t_list_sort.index(w_alloy)
    w_alloy = ws_exe_t_list_sort[int(Ws_exe_T_loc + 1)]

    # 根据w_alloy，在铁合金后搅拌时间表中查出s_time_alloy（铁合金投入后的后搅拌时间）
    sql_cmd = 'SELECT S_time_alloy_T from PARA_ALLOY_S_TIME where W_alloy_T = ' + str(w_alloy)
    cursor.execute(sql_cmd)
    s_time_alloy = cursor.fetchall()[0][0]

    return s_time_alloy
def alloy_addition_t_api(steel_id,element_alloy,wire_type,alloyXw,weight,x_concent,list_):

    # 读取模型输入数据
    read_dict = read_sql_alloy_addition(steel_id,element_alloy,wire_type,alloyXw,weight,x_concent,list_)

    # 计算输入模型
    res = alloy_addition_t(read_dict['cw'], read_dict['alloyXw'], read_dict['yw'], read_dict['delta_aim'],
                        read_dict['weight'], read_dict['x_aim'], read_dict['casting_loss'], read_dict['x_concent'],
                        read_dict['x_loss'], read_dict['y'], read_dict['uc'], read_dict['c'])

    write_dict = read_dict
    write_dict['alloyX_t'], write_dict['w_alloy_t'], write_dict['alloyX2_t'], write_dict['w_alloy2_t'] = \
        res[0], res[1], res[2], res[3]
    write_dict['s_time_alloy_t']=time_alloy_t(write_dict['w_alloy_t'])
    write_dict['s_time2_alloy_t']=time_alloy_t(write_dict['w_alloy2_t'])

    return write_dict


def make_excel(data_list):
    res_file = r"./alloy_addition.xlsx"
    writer = pd.ExcelWriter(res_file)
    data_name_list=['合金添加计算','合金添加温度计算']
    for i in range(len(data_list)):
        matrix = list(data_list[i])
        res_dict=[data_list[i]]
        data=pd.DataFrame(res_dict,columns=matrix)
        data.to_excel(writer, sheet_name=data_name_list[i],index= False)
    writer.save()
    return res_file