# 人脸评分系统

一个基于 Flask 的人脸评分系统，可以分析人脸特征并提供综合评分。系统支持面部对称性分析、比例分析、清晰度评估以及性别识别等功能。

## 功能特点

- 面部特征完整性评分 (30%)
- 面部对称性分析 (20%)
- 面部比例评估 (20%)
- 面部清晰度评分 (15%)
- 面部表情自然度评估 (15%)
- 性别识别（基于预训练模型）
- 实时评分反馈
- 详细的评分报告和改进建议

## 系统要求

- Python 3.8 或更高版本
- 操作系统：Windows/Linux/MacOS

## 安装步骤

1. 克隆或下载项目代码

2. 创建并激活虚拟环境（推荐）：
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 下载必要的模型文件：
   - 将人脸关键点检测模型 `shape_predictor_68_face_landmarks.dat` 下载到 `models` 目录
   - 将性别识别模型 `gender_model.h5` 下载到 `models` 目录

   模型下载地址：
   - 人脸关键点检测模型：[dlib 官方模型](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)
   - 性别识别模型：[预训练模型](https://github.com/arunponnusamy/cvlib/releases/download/v0.2.0/gender_detection.model)（下载后重命名为 `gender_model.h5`）

5. 创建必要的目录：
```bash
mkdir models
```

## 使用方法

1. 启动应用：
```bash
python face_rating.py
```

2. 在浏览器中访问：
```
http://localhost:5000
```

3. 上传包含人脸的图片，系统将自动进行分析并显示评分结果

## 评分标准说明

- **面部特征完整性** (30%)：评估面部关键点的完整程度
- **面部对称性** (20%)：分析面部左右对称程度
- **面部比例** (20%)：评估面部各部位的比例关系
- **面部清晰度** (15%)：评估图像清晰度和质量
- **面部表情自然度** (15%)：评估面部表情的自然程度

## 注意事项

- 上传图片时请确保人脸清晰可见
- 建议使用正面照片以获得最佳效果
- 图片格式支持：JPG、PNG、JPEG
- 图片大小建议不超过 5MB

## 常见问题

1. 如果遇到模型文件缺失错误，请确保：
   - `models` 目录存在
   - 模型文件已正确下载并放置在 `models` 目录中
   - 模型文件名正确

2. 如果评分结果不准确，请检查：
   - 图片是否清晰
   - 人脸是否正面朝向
   - 光线是否充足

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进项目。 