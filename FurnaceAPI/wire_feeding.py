import pymysql
import time
from alloy_addition import alloy_addition
import numpy as np
from wire_feeding_ca import wire_feeding_ca
from wire_feeding_others import wire_feeding_others
from wire_time import wire_time
from alloy_addition_t import alloy_addition_t
from wire_feeding_t import wire_time_t
from composition_prediction import composition_prediction
import pandas as pd


# 读取输入变量储存到一个dict里面
def read_sql_wire_feeding_ca(steel_id,weight,ca,wire_type_ca,wire_type_other,element_other):
    """
     输入：
     db_con: 数据库连接设定
     输出：
     一个包含 （delta_ca_aim,ca_aim,ca,ca_loss,weight,yw_ca,
     cw_ca,w_wire_casi,line_number,wf_vca ）的字典
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

    # 从PARA_WIRE_COMPONENT(丝线成分表)表中读取cw_ca,line_number,w_wire_casi,wf_vca

    wire_type = wire_type_ca

    sql_cmd = 'SELECT Ca from PARA_WIRE_COMPONENT where wire_type = "' + wire_type + '"'
    cursor.execute(sql_cmd)
    dict['cw_ca'] = cursor.fetchall()[0][0]

    sql_cmd = 'SELECT W_wire from PARA_WIRE_COMPONENT where wire_type = "' + wire_type + '"'
    cursor.execute(sql_cmd)
    dict['w_wire_casi'] = cursor.fetchall()[0][0]

    sql_cmd = 'SELECT Wf_v from PARA_WIRE_COMPONENT where wire_type = "' + wire_type + '"'
    cursor.execute(sql_cmd)
    dict['wf_vca'] = cursor.fetchall()[0][0]
    db_con.close()
    return dict
# 读取输入变量储存到一个dict里面
def read_sql_wire_feeding_others(steel_id,weight,wire_type_others,element_other):
    """
     输入：
     db_con: 数据库连接设定
     输出：
     一个包含各个输入的字典
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

    dict['weight'] = weight


    wire_type = wire_type_others

    # 从PARA_STEEL_COMPONENT（钢种成分表）中读取element_aim
    sql_cmd = 'SELECT '+str(wire_type)+'_aim from PARA_STEEL_COMPONENT where steel_id = "' + steel_id + '"'
    cursor.execute(sql_cmd)
    dict['element_aim'] = cursor.fetchall()[0][0]

    # 从MEAS_SIS_ANA_DATA(计算机成分分析表)表中读取element

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
