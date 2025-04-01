import cv2
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from flask import Flask, request, jsonify,Response
import cv2
import os
import numpy as np
app = Flask(__name__)

@app.route('/process', methods=['GET','POST'])
def run_task():
    if request.method == 'GET':
        return "Please use POST method to upload an image."

    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return jsonify({'error': '请求中未包含文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    # 保存上传的文件到临时位置
    input_temp_path = 'temp_input.jpg'
    file.save(input_temp_path)

    try:
        # 构建模型 pipeline
        img_cartoon = pipeline(
            Tasks.image_portrait_stylization,
            model='iic/cv_unet_person-image-cartoon-3d_compound-models'
        )
        # 使用临时保存的文件路径进行处理
        result = img_cartoon(input_temp_path)

        # 从处理结果中获取输出图像（通常是一个 NumPy 数组）
        output_img = result[OutputKeys.OUTPUT_IMG]
        # 对处理结果进行编码，编码为 PNG 格式
        ret, buf = cv2.imencode('.png', output_img)
        if not ret:
            return jsonify({'error': '图像编码失败'}), 500

        # 删除临时输入文件
        os.remove(input_temp_path)
        # 返回二进制图像数据
        return Response(buf.tobytes(), mimetype='image/png')
    except Exception as e:
        # 删除临时文件（如果存在）
        if os.path.exists(input_temp_path):
            os.remove(input_temp_path)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
