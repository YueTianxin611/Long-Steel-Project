import os
import logging
from flask_restplus import Api, Resource, reqparse
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, flash, request, redirect, send_file, jsonify  #
from flask_cors import CORS

# 载入模型计算函数
from COM_MOD_FLUX_ADDITION_FIRST_DATA import flux_addition_first_api
from COM_MOD_DESULFURATION_DATA import desulfuration_api
from MOD_DEOXIDATE_DATA import deoxidate_api
from MOD_COMPOSITION_PREDICTION import com_predict
from COM_MOD_ALLOY_ADDITION import alloy_add
from COM_MOD_WIRE_FEEDING import wire_feeding


# 建立api参数
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 解决前端请求跨域问题******

# 支持swagger
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='LF_Model_demo',
          description='LF精炼炉模型接口demo演示,输入测试数据时为英文符号')


# ===========================以下为不同函数的日志初始化区域================================================================
# 创建一个logger格式
formatter = logging.Formatter(
    '----------------[%(asctime)s][%(thread)d][%(filename)s][line: %(lineno)d][%(levelname)s] ## %(message)s')
# step1 time_to_distance log
loggername = 'curvedata_cut_log'
logPath = os.path.join('/file_and_log', loggername + '.log')
logger = logging.getLogger(loggername)
logger.setLevel(logging.DEBUG)
try:  # 防止本地测试时报错
    fileHandler = logging.FileHandler(logPath, encoding='utf8')
except:
    fileHandler = logging.FileHandler(loggername + '.log', encoding='utf8')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

ns_LF_flux = api.namespace('第一次造渣计算', description='LF精炼炉模型API')
ns_LF_adjust = api.namespace('成分调整', description='LF精炼炉模型API')
ns_LF_heat = api.namespace('钢水加热升温计算', description='LF精炼炉模型API')
ns_LF_temp_predict = api.namespace('钢水温度预测计算', description='LF精炼炉模型API')
ns_LF_temp_current = api.namespace('计算现在时刻的钢水预测温度', description='LF精炼炉模型API')
ns_LF_des = api.namespace('强搅拌脱硫计算', description='LF精炼炉模型API')
ns_LF_deo = api.namespace('脱氧用铝添加计算', description='LF精炼炉模型API')
ns_LF_adjust = api.namespace('成分调整计算', description='LF精炼炉模型API')

# 配置参数装饰器
# 申请配置参数
deo_parser = reqparse.RequestParser()
deo_parser.add_argument('status', type=int, required=True, help='状态号,eg:0')
deo_parser.add_argument('steel_id', type=str, required=True, help='计划钢种代码,eg:Q345')
deo_parser.add_argument('weight', type=float, required=True, help='来自上步工序的钢水重量，kg,eg:10')
deo_parser.add_argument('o_ppm', type=float, required=True, help='钢水中氧测定值（ppm）,eg:20')
deo_parser.add_argument('is_O', type=int, required=True, help='是否有氧含量测定值,1/0,eg:1')
@ns_LF_deo.route('/deoxidate')
@ns_LF_deo.expect(deo_parser)
class deoxidate(Resource):
    # 通过post 打开文件
    def post(self):
        '''
        脱氧用铝添加计算模型计算接口
        '''
        # 取参数字典
        args = deo_parser.parse_args()

        if 'steel_id' not in args:
            # 此处可用多种警告信息
            # print 会存入docker 日志
            # flash 联合前端显示包错
            # logging 存入模型日志文档
            logger.error('[error] No steel id in paras')
            print('[error] No steel ladle id in paras')
            return redirect(request.url)

        if 'status' not in args:
            # print 会存入docker 日志
            logger.error('[error] No status in paras')
            print('[error] No status in paras')
            return redirect(request.url)

        if 'weight' not in args:
            # print 会存入docker 日志
            logger.error('[error] No weight in paras')
            print('[error] No weight in paras')
            return redirect(request.url)

        if 'o_ppm' not in args:
            # print 会存入docker 日志
            logger.error('[error] No o_ppm in paras')
            print('[error] No o_ppm in paras')
            return redirect(request.url)

        if 'is_O' not in args:
            # print 会存入docker 日志
            logger.error('[error] No is_O in paras')
            print('[error] No is_O in paras')
            return redirect(request.url)


        # 取zip参数
        status = args['status']
        steel_id = args['steel_id']
        weight = args['weight']
        o_ppm = args['o_ppm']
        is_O = args['is_O']
        # if user does not select file, browser also
        # submit an empty part without filename
        try:
            if status == 0:
                res_file = deoxidate_api(steel_id, weight, o_ppm, is_O)
                logger.info('deoxidate_api runs successfully')
                print(status)  # 测试代码
                return send_file(res_file,
                          mimetype='application/octet-stream',
                          attachment_filename='deoxidate.csv',
                          as_attachment=True)
            output = {}
            output['message'] = 'model calculation succeeded'
            output['stutas'] = 1
        except Exception as e:
            print(e)
            output = {}
            output['message'] = 'model calculation failed'
            output['stutas'] = 0
            output['data'] = None
        logger.info('deoxidate runs successfully')

        return jsonify(output)

# 配置参数装饰器
# 申请配置参数
des_parser = reqparse.RequestParser()
des_parser.add_argument('status', type=int, required=True, help='状态号,eg:0')
des_parser.add_argument('steel_id', type=str, required=True, help='计划钢种代码,eg:Q345')
des_parser.add_argument('weight', type=float, required=True, help='来自上步工序的钢水重量，kg,eg:20')
des_parser.add_argument('w_flux', type=float, required=True, help='造渣料的投入量，由函数flux_addition_first计算得到,eg:10')
des_parser.add_argument('ws_total_in', type=float, required=True,
                        help='钢包中当前渣量(kg/ton)，由函数flux_addition_first计算得到,eg:20')
des_parser.add_argument('w_flux_t', type=int, required=True, help='造渣料的投入量,eg:20')
des_parser.add_argument('s_des', type=int, required=True, help='强搅拌脱硫处理的基准值(%),eg:20')
@ns_LF_des.route('/desulfuration')
@ns_LF_des.expect(des_parser)
class desulfuration(Resource):
    # 通过post 打开文件
    def post(self):
        '''
        强搅拌脱硫计算模型计算接口
        '''
        # 取参数字典
        args = des_parser.parse_args()

        if 'steel_id' not in args:
            # 此处可用多种警告信息
            # print 会存入docker 日志
            # flash 联合前端显示包错
            # logging 存入模型日志文档
            logger.error('[error] No steel id in paras')
            print('[error] No steel id in paras')
            return redirect(request.url)

        if 'status' not in args:
            # print 会存入docker 日志
            logger.error('[error] No status in paras')
            print('[error] No status in paras')
            return redirect(request.url)

        if 'weight' not in args:
            # print 会存入docker 日志
            logger.error('[error] No weight in paras')
            print('[error] No weight in paras')
            return redirect(request.url)

        if 'w_flux' not in args:
            # print 会存入docker 日志
            logger.error('[error] No w_flux in paras')
            print('[error] No w_flux in paras')
            return redirect(request.url)

        if 'ws_total_in' not in args:
            # print 会存入docker 日志
            logger.error('[error] No ws_total_in in paras')
            print('[error] No ws_total_in in paras')
            return redirect(request.url)

        if 'w_flux_t' not in args:
            # print 会存入docker 日志
            logger.error('[error] No w_flux_t in paras')
            print('[error] No w_flux_t in paras')
            return redirect(request.url)

        if 's_des' not in args:
            # print 会存入docker 日志
            logger.error('[error] No s_des in paras')
            print('[error] No s_des in paras')
            return redirect(request.url)


        # 取zip参数
        status = args['status']
        steel_id = args['steel_id']
        weight = args['weight']
        w_flux = args['w_flux']
        ws_total_in = args['ws_total_in']
        w_flux_t = args['w_flux_t']
        s_des = args['s_des']
        # if user does not select file, browser also
        # submit an empty part without filename
        try:
            if status == 0:
                res = desulfuration_api(steel_id,weight,w_flux,ws_total_in,w_flux_t,s_des)
                if res[0] != '.':
                    logger.info('desulfuration_api runs failed')
                    output = {}
                    output['message'] = res
                    output['stutas'] = 0
                    output['data'] = None
                else:
                    logger.info('desulfuration_api runs successfully')
                    print(steel_id, status)  # 测试代码
                    return send_file(res,
                              mimetype='application/octet-stream',
                              attachment_filename='desulfuration.xlsx',
                              as_attachment=True)
            output = {}
            output['message'] = 'model calculation succeeded'
            output['stutas'] = 1
        except Exception as e:
            print(e)
            output = {}
            output['message'] = 'model calculation failed'
            output['stutas'] = 0
            output['data'] = None
        logger.info('desulfuration runs successfully')

        return jsonify(output)


# 配置参数装饰器
# 申请配置参数
flux_parser = reqparse.RequestParser()
flux_parser.add_argument('status', type=int, required=True, help='状态号,eg:0')
flux_parser.add_argument('steel_id', type=str, required=True, help='计划钢种代码,eg:Q345')
flux_parser.add_argument('weight', type=float, required=True, help='来自上步工序的钢水重量，kg,eg:20')
flux_parser.add_argument('s_total_des_time', type=float, required=True, help='造渣料搅拌时间（分）,eg:10')
flux_parser.add_argument('flux_addition_done', type=int, required=True, help='造渣料添加完毕状态标示,1/0')
@ns_LF_flux.route('/flux_addition_first')
@ns_LF_flux.expect(flux_parser)
class desulfuration(Resource):
    # 通过post 打开文件
    def post(self):
        '''
        第一次造渣料计算模型计算接口
        '''
        # 取参数字典
        args = flux_parser.parse_args()

        if 'steel_id' not in args:
            # 此处可用多种警告信息
            # print 会存入docker 日志
            # flash 联合前端显示包错
            # logging 存入模型日志文档
            logger.error('[error] No steel id in paras')
            print('[error] No steel id in paras')
            return redirect(request.url)

        if 'status' not in args:
            # print 会存入docker 日志
            logger.error('[error] No status in paras')
            print('[error] No status in paras')
            return redirect(request.url)

        if 'weight' not in args:
            # print 会存入docker 日志
            logger.error('[error] No weight in paras')
            print('[error] No weight in paras')
            return redirect(request.url)

        if 's_total_des_time' not in args:
            # print 会存入docker 日志
            logger.error('[error] No s_total_des_time in paras')
            print('[error] No s_total_des_time in paras')
            return redirect(request.url)

        if 'flux_addition_done' not in args:
            # print 会存入docker 日志
            logger.error('[error] No flux_addition_done in paras')
            print('[error] No flux_addition_done in paras')
            return redirect(request.url)


        # 取zip参数
        status = args['status']
        steel_id = args['steel_id']
        weight = args['weight']
        s_total_des_time = args['s_total_des_time']
        flux_addition_done = args['flux_addition_done']
        # if user does not select file, browser also
        # submit an empty part without filename
        try:
            if status == 0:
                res = flux_addition_first_api(steel_id,s_total_des_time,weight,flux_addition_done)
                if res[0] != '.':
                    logger.info('flux_addition_first_api runs failed')
                    output = {}
                    output['message'] = res
                    output['stutas'] = 0
                    output['data'] = None
                else:
                    logger.info('flux_addition_first_api runs successfully')
                    print(steel_id, status)  # 测试代码
                    return send_file(res,
                              mimetype='application/octet-stream',
                              attachment_filename='flux_addition_first.xlsx',
                              as_attachment=True)
            output = {}
            output['message'] = 'model calculation succeeded'
            output['stutas'] = 1
        except Exception as e:
            print(e)
            output = {}
            output['message'] = 'model calculation failed'
            output['stutas'] = 0
            output['data'] = None
        logger.info('flux_addition_first runs successfully')

        return jsonify(output)

# 配置参数装饰器
# 申请配置参数
alloy_addition_parser = reqparse.RequestParser()
alloy_addition_parser.add_argument('status', type=int, required=True, help='状态号')
alloy_addition_parser.add_argument('steel_id', type=str, required=True, help='钢包号 eg:Q345')
alloy_addition_parser.add_argument('b_al_deoxi',type=float, required=True, help='钢水脱氧用铝投入量(kg),由函数deoxidate得到,eg:3')
alloy_addition_parser.add_argument('fesi_deoxi', type=float, required=True, help='钢水脱氧用Si投入量(kg),由函数deoxidate得到,eg:2 ')
alloy_addition_parser.add_argument('element_alloy', type=str, required=True, help="通过合金添加调整的成分 eg:['Al','Cu','Si']")
alloy_addition_parser.add_argument('wire_type', type=str, required=True, help="喂的丝线种类,eg:['CaSi','Al'] 钙丝在前，其他丝在后")
alloy_addition_parser.add_argument('alloyXw', type=str, required=True, help='丝线的喂入量(kg),eg:[10,2]')
alloy_addition_parser.add_argument('weight', type=float, required=True, help='钢水重量(ton),eg:10')
alloy_addition_parser.add_argument('x_concent', type=str, required=True, help='钢水中的成分测定值(%),eg:[1,2,2]')
alloy_addition_parser.add_argument('list_', type=str, required=True, help="[浇铸方法,是否为连浇第一炉（是为1，否为0）]eg:['billet', 0]")
@ns_LF_adjust.route('/alloy_addition')
@ns_LF_adjust.expect(alloy_addition_parser)
class alloy_addition(Resource):
    # 通过post 打开文件
    def post(self):
        '''
        合金添加计算模型计算接口
        '''
        # 取参数字典
        args = alloy_addition_parser.parse_args()

        if 'steel_id' not in args:
            # 此处可用多种警告信息
            # print 会存入docker 日志
            # flash 联合前端显示包错
            # logging 存入模型日志文档
            logger.error('[error] No steel id in paras')
            print('[error] No steel id in paras')
            return redirect(request.url)

        if 'status' not in args:
            # print 会存入docker 日志
            logger.error('[error] No status in paras')
            print('[error] No status in paras')
            return redirect(request.url)
        if 'b_al_deoxi' not in args:
            # print 会存入docker 日志
            logger.error('[error] No b_al_deoxi in paras')
            print('[error] No b_al_deoxi in paras')
            return redirect(request.url)

        if 'fesi_deoxi' not in args:
            # print 会存入docker 日志
            logger.error('[error] No fesi_deoxi in paras')
            print('[error] No fesi_deoxi in paras')
            return redirect(request.url)

        if 'element_alloy' not in args:
            # print 会存入docker 日志
            logger.error('[error] No element_alloy in paras')
            print('[error] No element_alloy in paras')
            return redirect(request.url)

        if 'wire_type' not in args:
            # print 会存入docker 日志
            logger.error('[error] No wire_type in paras')
            print('[error] No wire_type in paras')
            return redirect(request.url)

        if 'alloyXw' not in args:
            # print 会存入docker 日志
            logger.error('[error] No alloyXw in paras')
            print('[error] No alloyXw in paras')
            return redirect(request.url)

        if 'weight' not in args:
            # print 会存入docker 日志
            logger.error('[error] No weight in paras')
            print('[error] No weight in paras')
            return redirect(request.url)

        if 'x_concent' not in args:
            # print 会存入docker 日志
            logger.error('[error] No x_concent in paras')
            print('[error] No x_concent in paras')
            return redirect(request.url)

        if 'list_' not in args:
            # print 会存入docker 日志
            logger.error('[error] No list_ in paras')
            print('[error] No list_ in paras')
            return redirect(request.url)

        # 取zip参数
        status = args['status']
        b_al_deoxi = args['b_al_deoxi']
        fesi_deoxi = args['fesi_deoxi']
        steel_id= args['steel_id']
        element_alloy=args['element_alloy']
        element_alloy=eval(element_alloy)
        wire_type=args['wire_type']
        wire_type=eval(wire_type)
        alloyXw=args['alloyXw']
        alloyXw=eval(alloyXw)
        weight=args['weight']
        x_concent=args['x_concent']
        x_concent=eval(x_concent)
        list_=args['list_']
        list_=eval(list_)

        # if user does not select file, browser also
        # submit an empty part without filename
        try:
            if status == 0:
                res_file = alloy_add(b_al_deoxi,fesi_deoxi,steel_id, element_alloy,wire_type, alloyXw, weight, x_concent,
                                     list_)
                print(res_file)
                if res_file==-1:
                    logger.error('[error] alloy addition calculation fails')
                    print('[error] alloy addition calculation fails')
                else:
                    logger.info('composition_adjustment_api runs successfully')
                    print(steel_id, status)  # 测试代码
                    return send_file(res_file,mimetype='application/octet-stream',as_attachment=True,
                                     attachment_filename="alloy_addition.xlsx")
            output = {}
            output['message'] = 'model calculation succeeded'
            output['stutas'] = 1
        except Exception as e:
            print(e)
            output = {}
            output['message'] = 'model calculation failed'
            output['stutas'] = 0
            output['data'] = None
        logger.info('composition_adjustment runs successfully')

        return jsonify(output)

# 配置参数装饰器
# 申请配置参数
wire_parser = reqparse.RequestParser()
wire_parser.add_argument('status', type=int, required=True, help='状态号')
wire_parser.add_argument('steel_id', type=str, required=True, help='钢包号 eg:Q345')
wire_parser.add_argument('element', type=float, required=True, help='钢水中的其他丝线成分测定值(%) eg:1')
wire_parser.add_argument('wire_type', type=str, required=True, help="喂的丝线种类,eg:['CaSi','Al'] 钙丝在前，其他丝在后")
wire_parser.add_argument('weight', type=float, required=True, help='钢水重量(ton),eg:10')
wire_parser.add_argument('ca', type=float, required=True, help='钢水中的成分测定值(%),eg:0.5')
@ns_LF_adjust.route('/wire_feeding')
@ns_LF_adjust.expect(wire_parser)
class wire_feeding_cal(Resource):
    # 通过post 打开文件
    def post(self):
        '''
        喂丝计算模型计算接口
        '''
        # 取参数字典
        args = wire_parser.parse_args()

        if 'steel_id' not in args:
            # 此处可用多种警告信息
            # print 会存入docker 日志
            # flash 联合前端显示包错
            # logging 存入模型日志文档
            logger.error('[error] No steel id in paras')
            print('[error] No steel id in paras')
            return redirect(request.url)

        if 'status' not in args:
            # print 会存入docker 日志
            logger.error('[error] No status in paras')
            print('[error] No status in paras')
            return redirect(request.url)

        if 'element' not in args:
            # print 会存入docker 日志
            logger.error('[error] No element_other in paras')
            print('[error] No element_other in paras')
            return redirect(request.url)

        if 'wire_type' not in args:
            # print 会存入docker 日志
            logger.error('[error] No wire_type in paras')
            print('[error] No wire_type in paras')
            return redirect(request.url)

        if 'weight' not in args:
            # print 会存入docker 日志
            logger.error('[error] No weight in paras')
            print('[error] No weight in paras')
            return redirect(request.url)

        if 'ca' not in args:
            # print 会存入docker 日志
            logger.error('[error] No ca in paras')
            print('[error] No ca in paras')
            return redirect(request.url)

        # 取zip参数
        status = args['status']
        steel_id= args['steel_id']
        element = args['element']
        wire_type=args['wire_type']
        wire_type=eval(wire_type)
        weight=args['weight']
        ca=args['ca']
        # if user does not select file, browser also
        # submit an empty part without filename
        try:
            if status == 0:
                res_file = wire_feeding(steel_id, weight, ca, wire_type, element)
                print(res_file)
                if res_file==-1:
                    logger.error('[error] wire feeding calculation fails')
                    print('[error] wire feeding calculation fails')
                else:
                    logger.info('wire feeding calculation runs successfully')
                    print(steel_id, status)  # 测试代码
                    return send_file(res_file,mimetype='application/octet-stream',as_attachment=True,
                                     attachment_filename="wire_feeding.xlsx")
            output = {}
            output['message'] = 'model calculation succeeded'
            output['stutas'] = 1
        except Exception as e:
            print(e)
            output = {}
            output['message'] = 'model calculation failed'
            output['stutas'] = 0
            output['data'] = None
        logger.info('wire feeding calculation runs successfully')

        return jsonify(output)

# 配置参数装饰器
# 申请配置参数
composition_predict_parser = reqparse.RequestParser()
composition_predict_parser.add_argument('status', type=int, required=True, help='状态号')
composition_predict_parser.add_argument('steel_id', type=str, required=True, help='钢包号 eg:Q345')
composition_predict_parser.add_argument('alloyX',type=str, required=True, help='成分调整的合金铁j的投入量(kg),alloy_addition函数计算得到,eg:[0. 0. 0. 0.]')
composition_predict_parser.add_argument('element', type=str, required=True, help="通过合金添加调整的成分 eg:['Al','Cu','Si']")
composition_predict_parser.add_argument('wire_type', type=str, required=True, help="喂的丝线种类,eg:['CaSi','Al']钙丝在前，其他丝在后")
composition_predict_parser.add_argument('alloyXw', type=str, required=True, help='丝线的喂入量(kg),eg:[10,2]')
composition_predict_parser.add_argument('weight', type=float, required=True, help='钢水重量(ton),eg:10')
composition_predict_parser.add_argument('x_concent', type=str, required=True, help='钢水中的成分测定值(%),eg:[1,2,2]')
composition_predict_parser.add_argument('flux_addition_done', type=bool, required=True, help='造渣料是否添加完毕')
composition_predict_parser.add_argument('s_molten_last', type=float, required=True, help='上步工序带来的钢水中S(%),eg:2')
composition_predict_parser.add_argument('s_total_des_time', type=float, required=True, help='造渣料搅拌时间（分）eg:3')
composition_predict_parser.add_argument('s_molten_ini', type=float, required=True, help='由造渣料添加得到，eg:1')
composition_predict_parser.add_argument('s_dregs_ini', type=float, required=True, help='由造渣料添加得到，eg:2')
composition_predict_parser.add_argument('ws_total_in', type=float, required=True, help='钢包中当前渣量(kg/ton)，eg:3')
composition_predict_parser.add_argument('w_flux', type=float, required=True, help='造渣料的投入量，由造渣料添加得到eg:2')
composition_predict_parser.add_argument('s_molten_ini_before', type=float, required=True, help='前次渣料添加前钢水中的S(%)，由造渣料添加得到eg:3')
composition_predict_parser.add_argument('s_dregs_ini_before', type=float, required=True, help='前次渣料添加前渣中的S(%)，由造渣料添加得到eg:2')
composition_predict_parser.add_argument('ws_total_before', type=float, required=True, help='前次渣料添加前钢包中的渣量(kg/ton)，由造渣料添加得到eg:3')
@ns_LF_adjust.route('/composition_prediction')
@ns_LF_adjust.expect(composition_predict_parser)
class composition_prediction(Resource):
    # 通过post 打开文件
    def post(self):
        '''
        成分预测计算模型计算接口
        '''
        # 取参数字典
        args = composition_predict_parser.parse_args()

        if 'steel_id' not in args:
            # 此处可用多种警告信息
            # print 会存入docker 日志
            # flash 联合前端显示包错
            # logging 存入模型日志文档
            logger.error('[error] No steel id in paras')
            print('[error] No steel id in paras')
            return redirect(request.url)

        if 'status' not in args:
            # print 会存入docker 日志
            logger.error('[error] No status in paras')
            print('[error] No status in paras')
            return redirect(request.url)

        if 'alloyX' not in args:
            # print 会存入docker 日志
            logger.error('[error] No alloyX in paras')
            print('[error] No alloyX in paras')
            return redirect(request.url)

        if 'element' not in args:
            # print 会存入docker 日志
            logger.error('[error] No element in paras')
            print('[error] No element in paras')
            return redirect(request.url)

        if 'wire_type' not in args:
            # print 会存入docker 日志
            logger.error('[error] No wire_type in paras')
            print('[error] No wire_type in paras')
            return redirect(request.url)

        if 'alloyXw' not in args:
            # print 会存入docker 日志
            logger.error('[error] No alloyXw in paras')
            print('[error] No alloyXw in paras')
            return redirect(request.url)

        if 'weight' not in args:
            # print 会存入docker 日志
            logger.error('[error] No weight in paras')
            print('[error] No weight in paras')
            return redirect(request.url)

        if 'x_concent' not in args:
            # print 会存入docker 日志
            logger.error('[error] No x_concent in paras')
            print('[error] No x_concent in paras')
            return redirect(request.url)

        if 'flux_addition_done' not in args:
            # print 会存入docker 日志
            logger.error('[error] No flux_addition_done in paras')
            print('[error] No flux_addition_done in paras')
            return redirect(request.url)

        if 's_molten_last' not in args:
            # print 会存入docker 日志
            logger.error('[error] No s_molten_last in paras')
            print('[error] No s_molten_last in paras')
            return redirect(request.url)

        if 's_total_des_time' not in args:
            # print 会存入docker 日志
            logger.error('[error] No s_total_des_time in paras')
            print('[error] No s_total_des_time in paras')
            return redirect(request.url)

        if 's_molten_ini' not in args:
            # print 会存入docker 日志
            logger.error('[error] No s_molten_ini in paras')
            print('[error] No s_molten_ini in paras')
            return redirect(request.url)

        if 's_dregs_ini' not in args:
            # print 会存入docker 日志
            logger.error('[error] No s_dregs_ini in paras')
            print('[error] No s_dregs_ini in paras')
            return redirect(request.url)

        if 'ws_total_in' not in args:
            # print 会存入docker 日志
            logger.error('[error] No ws_total_in in paras')
            print('[error] No ws_total_in in paras')
            return redirect(request.url)

        if 'w_flux' not in args:
            # print 会存入docker 日志
            logger.error('[error] No w_flux in paras')
            print('[error] No w_flux in paras')
            return redirect(request.url)

        if 's_molten_ini_before' not in args:
            # print 会存入docker 日志
            logger.error('[error] No s_molten_ini_before in paras')
            print('[error] No s_molten_ini_before in paras')
            return redirect(request.url)

        if 's_dregs_ini_before' not in args:
            # print 会存入docker 日志
            logger.error('[error] No s_dregs_ini_before in paras')
            print('[error] No s_dregs_ini_before in paras')
            return redirect(request.url)

        if 'ws_total_before' not in args:
            # print 会存入docker 日志
            logger.error('[error] No ws_total_before in paras')
            print('[error] No ws_total_before in paras')
            return redirect(request.url)

        # 取zip参数
        status = args['status']
        alloyX = args['alloyX']
        alloyX = eval(alloyX)
        steel_id= args['steel_id']
        element=args['element']
        element=eval(element)
        wire_type=args['wire_type']
        wire_type=eval(wire_type)
        alloyXw=args['alloyXw']
        alloyXw=eval(alloyXw)
        weight=args['weight']
        x_concent=args['x_concent']
        x_concent=eval(x_concent)
        flux_addition_done=args['flux_addition_done']
        s_molten_last=args['s_molten_last']
        s_total_des_time=args['s_total_des_time']
        s_molten_ini=args['s_molten_ini']
        s_dregs_ini=args['s_dregs_ini']
        ws_total_in=args['ws_total_in']
        w_flux=args['w_flux']
        s_molten_ini_before=args['s_molten_ini_before']
        s_dregs_ini_before=args['s_dregs_ini_before']
        ws_total_before=args['ws_total_before']
        # if user does not select file, browser also
        # submit an empty part without filename
        try:
            if status == 0:
                res_file = com_predict(alloyX,steel_id, element, wire_type, alloyXw, weight, x_concent,
                   flux_addition_done,s_molten_last, s_total_des_time,s_molten_ini,
                   s_dregs_ini, ws_total_in, w_flux, s_molten_ini_before, s_dregs_ini_before,ws_total_before)
                print(res_file)
                if res_file==-1:
                    logger.error('[error] composition prediction calculation fails')
                    print('[error] composition prediction calculation fails')
                else:
                    logger.info('composition_prediction runs successfully')
                    print(steel_id, status)  # 测试代码
                    return send_file(res_file,mimetype='application/octet-stream',as_attachment=True, attachment_filename="composition_adjustment.xlsx")
            output = {}
            output['message'] = 'model calculation succeeded'
            output['stutas'] = 1
        except Exception as e:
            print(e)
            output = {}
            output['message'] = 'model calculation failed'
            output['stutas'] = 0
            output['data'] = None
        logger.info('composition prediction runs successfully')

        return jsonify(output)

if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=1989, debug=True)
    # app.run(port=9428, debug=True,processes=4)
    app.run(port=9429, debug=True)