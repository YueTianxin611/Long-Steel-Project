# 第一次造渣料添加计算
# 造渣料起着造脱硫渣及改变夹杂物形态的作用，有cao、合成渣和caf2三种
def flux_addition_first(flux_addition_done, s_total_des_time, s_time_des_std, ws_last, weight, flux_synthetic_assigned,
                        cmf_caf2, cmf_cao, cmf_synthetic, eeff, ps, ws_minimum):
    """
    输入：
        flux_addition_done：造渣料添加完毕状态标示
        s_total_des_time:造渣料搅拌时间（分）,监控吹氩流量大于固定值的搅拌时间,为传入参数
        s_time_des_std:标准搅拌时间（分）,由渣条件参数表定义
        ws_last：上步工序带来的渣量( kg )，由钢种组参数表定义
        flux_synthetic_assigned:合成渣添加规定，由钢种组参数表定义
        weight:钢水重量(ton)，称量值，来自上步工序
        cmf_caf2：造渣料caf2的冷却能(kcal/kg)，由造渣料成分表定义
        cmf_cao：造渣料cao的冷却能(kcal/kg)，由造渣料成分表定义
        cmf_synthetic：合成渣的冷却能(kcal/kg)，由造渣料成分表定义
        eeff：二次短网系数，设定值
        ps：造渣料熔解tap号，由造渣料熔解tap表定义
        ws_minimum:基本造渣料投入量，由渣条件参数表定义
    输出：
        wflux_synthetic:投入渣料中的合成渣量(kg)
        wflux_cao:投入渣料中的CaO量(kg)
        wflux_caf2:投入渣料中的CaF2量(kg)
        ws_total_in:钢包中当前渣量(kg/ton)
        ws_total_before:前次渣料添加前钢包中的渣量(kg/ton)
        ws_exe:下次处理的钢水中的渣量(kg)
        qs_melt1:第一次添加渣料熔解需要的热量(Kcal)
        ts1：第一次添加渣料熔解的时 间(分)

    作用：本炉次第一次造渣料的计算
    """

    if flux_addition_done == True:
        if s_total_des_time < s_time_des_std:
            out = "造渣料搅拌时间不足"
            return out
        else:
            out = "造渣料计算已完成"
            return out
    elif flux_addition_done == False:
        ws_total_in = ws_last / weight
    if flux_synthetic_assigned == True:
        # 从渣条件参数表中得到合成渣条件参数
        flux_synthetic = 1
        flux_cao = 0
        flux_caf2 = 0
    else:
        # 从渣条件参数表中得到其它渣件参数Flux-cao、Flux-caf2
        flux_synthetic = 0
        flux_cao = 1
        flux_caf2 = 1

    ws_total_before = ws_total_in
    w_flux = (flux_cao + flux_caf2 + flux_synthetic) * weight
    # 加一个基本投入量的判断
    #if w_flux < ws_minimum:
        #w_flux = ws_minimum
        #return
        # w_flux确定为基本投入量后，生产实绩应该如何添加
    ws_exe = ws_last + w_flux
    wflux_caf2 = weight * flux_caf2
    wflux_cao = weight * flux_cao
    wflux_synthetic = weight * flux_synthetic
    qs_melt1 = cmf_caf2 * wflux_caf2 + cmf_cao * wflux_cao + cmf_synthetic * wflux_synthetic
    ts1 = (qs_melt1 * 60) / (ps * 860 * eeff)
    return wflux_synthetic, wflux_cao, wflux_caf2, ws_total_in, ws_total_before, ws_exe, qs_melt1, ts1

