# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 17:01:54 2019

@author: 018614
"""

#其它成分调整时：选择是否采用丝线调整成分由操作工人在level1画面上决定(包括al、ti、C三种成分)
def wire_feeding_others(element_aim,element,element_loss,weight,yw_element,cw_element,w_wire_element,line_number,wf_v_element):
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
    if element_aim!=0:
        if element_aim-element>0:
            element_wire = (element_aim-element+element_loss)*10*weight / (yw_element * cw_element)
        else:
            element_wire = 0
        wire_strand = element_wire/w_wire_element/line_number
        p_time_strand = element_wire/w_wire_element/wf_v_element/line_number
    else:
        return 'error'
    return element_wire,wire_strand,p_time_strand