import pymysql
from wire_feeding_ca import wire_feeding_ca
from wire_feeding_others import wire_feeding_others
import pandas as pd


def wire_feeding(steel_id, weight, ca, wire_type,element_other):
    # 进行喂丝的相关计算
    dict_wire_ca, dict_wire_other = wire_feeding_api(steel_id, weight, ca, wire_type[0], wire_type[1], element_other)

    if dict_wire_ca==-1 or dict_wire_other==-1:
        return -1
    else:
        data_list=[dict_wire_ca,dict_wire_other]

    data_file = make_excel(data_list)
    return data_file

# 读取输入变量储存到一个dict里面
def read_sql_wire_feeding_ca(steel_id,weight,ca,wire_type_ca):
    """
     输入：
     db_con: 数据库连接设定
     输出：
     一个包含 （delta_ca_aim,ca_aim,ca,ca_loss,weight,yw_ca,
     cw_ca,w_wire_casi,line_number,wf_vca ）的字典
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

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取delta_ca_aim
    sql_cmd = 'SELECT delta_aim_Ca from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    dict['delta_ca_aim'] = cursor.fetchall()[0][0]

    # 从PARA_STEEL_COMPONENT（钢种成分表）中读取ca_aim
    sql_cmd = 'SELECT Ca_aim from PARA_STEEL_COMPONENT where steel_id = "' + steel_id + '"'
    cursor.execute(sql_cmd)
    dict['ca_aim'] = cursor.fetchall()[0][0]

    # 从MEAS_SIS_ANA_DATA(计算机成分分析表)表中读取ca
    dict['ca'] = ca
    dict['weight'] = weight

    # 从PARA_STEEL_GROUP_PARAMETERS(钢种组参数表)表中读取ca_loss
    sql_cmd = 'SELECT delta_loss_Ca from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    dict['ca_loss'] = cursor.fetchall()[0][0]

    # 从PARA_STEEL_GROUP_PARAMETERS(钢种组参数表)表中读取yw_ca
    sql_cmd = 'SELECT yw_Ca from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    dict['yw_ca'] = cursor.fetchall()[0][0]


    wire_type = wire_type_ca

    # 从PARA_WIRE_COMPONENT(丝线成分表)表中读取各个变量
    sql_cmd = 'SELECT Ca from PARA_WIRE_COMPONENT where wire_type = "' + wire_type + '"'
    cursor.execute(sql_cmd)
    dict['cw_ca'] = cursor.fetchall()[0][0]

    sql_cmd = 'SELECT W_wire from PARA_WIRE_COMPONENT where wire_type = "' + wire_type + '"'
    cursor.execute(sql_cmd)
    dict['w_wire_casi'] = cursor.fetchall()[0][0]

    sql_cmd = 'SELECT Wf_v from PARA_WIRE_COMPONENT where wire_type = "' + wire_type + '"'
    cursor.execute(sql_cmd)
    dict['wf_vca'] = cursor.fetchall()[0][0]

    dict['line_number'] = 1

    db_con.close()

    return dict

# 定义喂丝调整ca元素函数
def wire_feeding_ca_api(steel_id,weight,ca,wire_type_ca):

    # 读取模型输入数据
    read_dict = read_sql_wire_feeding_ca(steel_id,weight,ca,wire_type_ca)

    # 计算输入模型
    res = wire_feeding_ca(read_dict['delta_ca_aim'], read_dict['ca_aim'], read_dict['ca'],
                          read_dict['ca_loss'], read_dict['weight'], read_dict['yw_ca'], read_dict['cw_ca'],
                          read_dict['w_wire_casi'], read_dict['line_number'], read_dict['wf_vca'])

    write_dict = read_dict
    write_dict['casi_wire'] = res[0]
    write_dict['wire_strand'] = res[1]
    write_dict['p_time_strand'] = res[2]
    return write_dict

#print(wire_feeding_ca_api('Q345',10,1,['CaSi','C']))


# 读取输入变量储存到一个dict里面
def read_sql_wire_feeding_others(steel_id,weight,wire_type_others,element_other):
    """
     输入：
     db_con: 数据库连接设定
     输出：
     一个包含各个输入的字典
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

    dict['weight'] = weight

    wire_type = wire_type_others

    # 从PARA_STEEL_COMPONENT（钢种成分表）中读取element_aim
    sql_cmd = 'SELECT '+str(wire_type)+'_aim from PARA_STEEL_COMPONENT where steel_id = "' + steel_id + '"'
    cursor.execute(sql_cmd)
    dict['element_aim'] = cursor.fetchall()[0][0]

    dict['element'] = element_other

    # 从PARA_STEEL_GROUP_PARAMETERS(钢种组参数表)表中读取element_loss
    sql_cmd = 'SELECT delta_loss_'+str(wire_type)+' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    dict['element_loss'] = cursor.fetchall()[0][0]

    # 从PARA_STEEL_GROUP_PARAMETERS(钢种组参数表)表中读取yw_element
    sql_cmd = 'SELECT yw_'+str(wire_type)+' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
    cursor.execute(sql_cmd)
    dict['yw_element'] = cursor.fetchall()[0][0]

    # 从PARA_WIRE_COMPONENT(丝线成分表)表中读取cw_element,line_number,w_wire_element,wf_v_element
    line_number = 1
    dict['line_number'] = line_number
    sql_cmd = 'SELECT '+str(wire_type)+',W_wire,Wf_v from PARA_WIRE_COMPONENT where wire_type = "' + wire_type + '"'
    cursor.execute(sql_cmd)
    values = cursor.fetchall()
    dict['cw_element'],dict['w_wire_element'],dict['wf_v_element'] = values[0][0],values[0][1],values[0][2]
    db_con.close()
    return dict


# 定义喂丝调整其他(Al,Ti,C)元素函数
def wire_feeding_others_api(steel_id,weight,wire_type_others,element_other):

    # 读取模型输入数据
    read_dict = read_sql_wire_feeding_others(steel_id,weight,wire_type_others,element_other)

    # 计算输入模型
    res = wire_feeding_others(read_dict['element_aim'], read_dict['element'], read_dict['element_loss'],
                              read_dict['weight'], read_dict['yw_element'],read_dict['cw_element'],
                              read_dict['w_wire_element'],read_dict['line_number'], read_dict['wf_v_element'])
    if res=='error':
        return -1
    else:
        write_dict = read_dict
        write_dict['element_wire'] = res[0]
        write_dict['wire_strand'] = res[1]
        write_dict['p_time_strand'] = res[2]

    return write_dict

def wire_feeding_api(steel_id,weight,ca,wire_type_ca,wire_type_others,element_other):
    # 读取模型输入数据
    read_dict_ca = read_sql_wire_feeding_ca(steel_id, weight, ca, wire_type_ca)

    # 计算输入模型
    res_ca = wire_feeding_ca(read_dict_ca['delta_ca_aim'], read_dict_ca['ca_aim'], read_dict_ca['ca'],
                          read_dict_ca['ca_loss'], read_dict_ca['weight'], read_dict_ca['yw_ca'], read_dict_ca['cw_ca'],
                          read_dict_ca['w_wire_casi'], read_dict_ca['line_number'], read_dict_ca['wf_vca'])

    write_dict_ca = read_dict_ca
    write_dict_ca['casi_wire'] = res_ca[0]
    write_dict_ca['wire_strand'] = res_ca[1]
    write_dict_ca['p_time_strand'] = res_ca[2]


    # 读取模型输入数据
    read_dict_other = read_sql_wire_feeding_others(steel_id, weight, wire_type_others, element_other)

    # 计算输入模型
    res_other = wire_feeding_others(read_dict_other['element_aim'], read_dict_other['element'], read_dict_other['element_loss'],
                              read_dict_other['weight'], read_dict_other['yw_element'], read_dict_other['cw_element'],
                              read_dict_other['w_wire_element'], read_dict_other['line_number'], read_dict_other['wf_v_element'])

    write_dict_other = read_dict_other
    write_dict_other['element_wire'] = res_other[0]
    write_dict_other['wire_strand'] = res_other[1]
    write_dict_other['p_time_strand'] = res_other[2]

    ca_wire = write_dict_ca['casi_wire']
    p_time_strand_ca = write_dict_ca['p_time_strand']
    other_wire = write_dict_other['element_wire']
    p_time_strand_other = write_dict_other['p_time_strand']


    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL_PARA",
                             charset='utf8', use_unicode=True)
    cursor = db_con.cursor()


    sql_cmd = 'SELECT W_wire_T from PARA_WIRE_S_TIME where wire_type= "' + wire_type_ca + '"'
    cursor.execute(sql_cmd)
    time1_list = cursor.fetchall()
    time1_list_sort = []
    for n in time1_list:
        time1_list_sort.append(n[0])
    time1_list_sort.append(ca_wire)
    time1_list_sort.sort()
    time1_loc = time1_list_sort.index(ca_wire)
    Ca_wire = time1_list_sort[int(time1_loc+ 1)]

    sql_cmd = 'SELECT S_time_w_T from PARA_WIRE_S_TIME where W_wire_T = ' + str(Ca_wire) + ' and wire_type = "'+ wire_type_ca+'"'
    cursor.execute(sql_cmd)
    s_time_strand_ca = cursor.fetchall()[0][0]


    sql_cmd = 'SELECT W_wire_T from PARA_WIRE_S_TIME where wire_type= "' + wire_type_others+'"'
    cursor.execute(sql_cmd)
    time2_list = cursor.fetchall()
    time2_list_sort = []
    for n in time2_list:
        time2_list_sort.append(n[0])
    time2_list_sort.append(other_wire)
    time2_list_sort.sort()
    time2_loc = time2_list_sort.index(other_wire)
    Other_wire = time2_list_sort[int(time2_loc+ 1)]
    sql_cmd = 'SELECT S_time_w_T from PARA_WIRE_S_TIME where W_wire_T = ' + str(Other_wire) + ' and wire_type ="'+wire_type_others+'"'
    cursor.execute(sql_cmd)
    s_time_strand_other = cursor.fetchall()[0][0]

    wire_time_ca = s_time_strand_ca+p_time_strand_ca
    wire_time_other=s_time_strand_other+p_time_strand_other

    res_time = max(wire_time_ca,wire_time_other)
    res_time_t = res_time
    write_dict_other['s_time_wire'] = res_time
    write_dict_other['s_time_wire_t'] = res_time_t
    return write_dict_ca,write_dict_other

def make_excel(data_list):
    res_file = r"./wire_feeding.xlsx"
    writer = pd.ExcelWriter(res_file)
    data_name_list=['喂钙丝计算','喂其他丝线计算']
    for i in range(len(data_list)):
        matrix = list(data_list[i])
        res_dict=[data_list[i]]
        data=pd.DataFrame(res_dict,columns=matrix)
        data.to_excel(writer, sheet_name=data_name_list[i],index= False)
    writer.save()
    return res_file

wire_feeding('Q345', 10, 1, ['CaSi','C'],1)

