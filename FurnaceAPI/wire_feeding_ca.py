# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 16:27:42 2019

@author: 018614
"""

#2.3.6.3喂丝计算
#由于钢水中的[ca]调整只有通过喂入钙丝实现，故钙丝计算可以自动进行
def wire_feeding_ca(delta_ca_aim,ca_aim,ca,ca_loss,weight,yw_ca,cw_ca,w_wire_casi,line_number,wf_vca):
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
    if delta_ca_aim == 0 or ca_aim-ca <= delta_ca_aim:
        if ca_aim!=0:
            casi_wire = (ca_aim-ca+ca_loss)*10*weight / (yw_ca * cw_ca)
            wire_strand = casi_wire/w_wire_casi/line_number
            p_time_strand = casi_wire/w_wire_casi/wf_vca/line_number

        else:
            return 'error'
    else:
        return 'error'
    return casi_wire ,wire_strand,p_time_strand


