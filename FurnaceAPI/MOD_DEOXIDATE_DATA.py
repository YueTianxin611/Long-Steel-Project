import pymysql
from deoxidate import deoxidate
import pandas as pd

# 读取输入变量储存到一个dict里面
def read_sql_deoxidate(db_con,steel_id,weight,o_ppm,is_O):
    cursor = db_con.cursor()

    dict = {}

    dict['steel_id'] = steel_id

    # 从PARA_STEEL_GROUP（钢种分组表）中读取group_id
    sql_cmd = 'SELECT group_id from PARA_STEEL_GROUP where steel_id="' + steel_id + '"'
    cursor.execute(sql_cmd)
    group_id = cursor.fetchall()[0][0]

    # 从PARA_STEEL_GROUP_PARAMETERS（钢种组参数表）中读取各个变量
    list = ['Staus_Al_addition_permitted', 'yal_deoxi', 'yfesi_deoxi']
    for i in range(len(list)):
        sql_cmd = 'SELECT ' + list[i] + ' from PARA_STEEL_GROUP_PARAMETERS where group_id = ' + str(group_id)
        cursor.execute(sql_cmd)
        dict[list[i]] = cursor.fetchall()[0][0]

    # 从PARA_STEEL_COMPONENT（钢种成分表）中读取Si_aim
    sql_cmd = 'SELECT Si_aim from PARA_STEEL_COMPONENT where steel_id="' + steel_id + '"'
    cursor.execute(sql_cmd)
    dict['si_aim'] = cursor.fetchall()[0][0]

    # 从PARA_ALLOY_COMPONENT（铁合金成分表）中读取各个变量
    sql_cmd = 'SELECT Si from PARA_ALLOY_COMPONENT where alloy_type="FeSi"'
    cursor.execute(sql_cmd)
    dict['c_fesi_si'] = cursor.fetchall()[0][0]

    sql_cmd = 'SELECT Al from PARA_ALLOY_COMPONENT where alloy_type="Al"'
    cursor.execute(sql_cmd)
    dict['c_al_al'] = cursor.fetchall()[0][0]

    # 从前端界面输入
    dict['o_ppm'] = o_ppm
    dict['weight']= weight
    if is_O == 0:
        dict['is_o'] = False
    else:
        dict['is_o'] = True

    return dict

def make_csv(res_dict):
    matrix = list(res_dict)
    res_dict = [res_dict]
    df = pd.DataFrame(res_dict, columns= matrix)
    res_file = r"./deoxidate.csv"
    df.to_csv(res_file, index= False)
    return res_file

# 定义除氧接口函数
def deoxidate_api(steel_id,weight,o_ppm,is_O):
    # 链接数据库
    db_con = pymysql.connect(host="10.75.4.20", port=3305, user="intern", password="123456", database="LF_MODEL_PARA",
                             charset='utf8', use_unicode=True)

    # 读取模型输入数据
    read_dict = read_sql_deoxidate(db_con,steel_id,weight,o_ppm,is_O)

    # 计算输入模型
    res = deoxidate(read_dict['Staus_Al_addition_permitted'], read_dict['o_ppm'], read_dict['weight'],
                    read_dict['yal_deoxi'],
                    read_dict['c_al_al'], read_dict['is_o'], read_dict['si_aim'], read_dict['yfesi_deoxi'],
                    read_dict['c_fesi_si'])
    res_dict = read_dict
    res_dict['b_al_deoxi'] = res[0]
    res_dict['fesi_deoxi'] = res[1]

    db_con.close()

    # 生成csv文件
    res_file = make_csv(read_dict)

    return res_file


if __name__ == "__main__":
    res_file = deoxidate_api('Q345', 1, 10, 20, 1)
