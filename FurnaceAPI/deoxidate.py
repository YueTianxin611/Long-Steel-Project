import pymysql
import pandas as pd
import numpy as np
import math
import time

def deoxidate(staus_al_addition_permitted, o_ppm, weight, yal_deoxi, c_al_al, is_o, si_aim, yfesi_deoxi, c_fesi_si):
    """
    输入：
        staus_al_addition_permitted：铝投入可否标示,在钢种组参数表中定义
        o_ppm: 钢水中氧测定值（ppm），来自LF的level1
        weight:钢水重量(ton)，称量值，来自上步工序
        yal_deoxi:脱氧用铝收得率(%)	,在钢种组参数表中定义
        c_al_al:铁合金al的al成分含有率(%),由铁合金成分表定义
        is_o:bool,是否有氧含量测定值
        si_aim：钢种的Si成分目标值(%)，由钢种成分表定义
        yfesi_deoxi：脱氧用Si收得率(%)	，在钢种组参数表中定义
        c_fesi_Si:铁合金fesi的Si成分含有率(%),由铁合金成分表定义

    输出：
        b_al_deoxi：钢水脱氧用铝投入量(kg)
        fesi_deoxi：钢水脱氧用Si投入量(kg)
    作用：
        钢水脱氧用al（fesi）投入量(kg)计算
    表格：钢种分组表、钢种组参数表、铁合金成分表
    """

    if staus_al_addition_permitted == True:
        fesi_deoxi = 0
        if is_o is True:
            if o_ppm > 15:
                b_al_deoxi = (0.00112 * o_ppm * weight) / (yal_deoxi * c_al_al)
            else:
                b_al_deoxi = 0
        else:
            b_al_deoxi = 0
    elif staus_al_addition_permitted == False:
        print("al脱氧不允许")
        b_al_deoxi = 0
        if is_o is True:
            if o_ppm > 70:
                o_equi = math.sqrt(1 / math.exp(29150 / 1873 - 11.01) / si_aim)
                fesi_deoxi = (o_ppm - o_equi) * 0.000878 * weight / (yfesi_deoxi * c_fesi_si)
                if fesi_deoxi < 0:
                    fesi_deoxi = 0
            else:
                fesi_deoxi = 0
        else:
            fesi_deoxi = 0
    return b_al_deoxi, fesi_deoxi
