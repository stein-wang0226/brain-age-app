# NeuroAge · 脑龄预测智能评估系统

基于 CLIP ViT-L/14 + MoE-4 架构的脑部 MRI 脑龄预测 Web 应用，支持认知分期评估（CN / MCI / AD）与脑区归因分析。

## 功能特性

- **影像上传**：支持拖拽或点击上传脑部 MRI（PNG / JPG / TIFF / BMP）
- **示例影像**：内置 4 组示例被试（含 axial / coronal / sagittal 多视角）
- **脑龄预测**：输出预测脑龄、脑龄差距（Brain Age Gap）
- **认知分期**：CN（认知正常）/ MCI（轻度认知障碍）/ AD（阿尔茨海默病）概率分布
- **脑区归因**：8 个关键脑区的贡献度分析（海马体、内侧颞叶、前额叶皮层等）
- **可视化报告**：环形进度图、分期概率条形图、脑区热力图

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.9+, Flask 3.0 |
| 前端 | 原生 HTML/CSS/JS（单文件，无框架依赖） |
| 图像处理 | Pillow |
| 模型（Mock） | CLIP ViT-L/14 + MoE-4（当前为模拟推理） |

## 快速开始

### 1. 环境配置

```bash
# 克隆项目
git clone git@github.com:stein-wang0226/brain-age-app.git
cd brain-age-app

# 创建虚拟环境（可选，run.sh 会自动创建）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 方式一：一键启动（推荐）
bash run.sh

# 方式二：手动启动
./venv/bin/python app.py
```

服务启动后访问 **http://localhost:5001**

### 3. 上传影像或选择示例

- **上传影像**：拖拽 MRI 图片到上传区域，或点击选择文件
- **使用示例**：点击「或使用示例影像」展开内置被试列表，选择任意被试
- 填写患者 ID、年龄、性别等基本信息

### 4. 解读评估报告

点击「开始脑龄预测」后，系统生成以下报告模块：

| 模块 | 内容 |
|------|------|
| **脑龄环** | 预测脑龄数值 + 脑龄差距（正值表示大脑老化加速） |
| **分期评估** | CN / MCI / AD 三类概率分布条形图 |
| **扫描信息** | 文件尺寸、模型版本、训练数据集、QWK 指标 |
| **脑区归因** | 8 个脑区贡献度排名，颜色编码严重程度 |

### 5. 多轮对比分析

- 修改患者年龄/性别参数后重新分析，观察预测结果变化
- 切换不同示例被试或上传新影像，进行多轮对比
- 每次分析独立，结果实时更新

## 项目结构

```
brain-age-app/
├── app.py              # Flask 后端 + Mock 推理逻辑
├── requirements.txt    # Python 依赖
├── run.sh              # 一键启动脚本
├── templates/
│   └── index.html      # 前端页面（HTML + CSS + JS 单文件）
├── samples/            # 内置示例 MRI 影像
├── uploads/            # 用户上传文件（运行时生成）
└── venv/               # Python 虚拟环境
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 前端页面 |
| GET | `/api/samples` | 获取示例影像列表 |
| GET | `/api/samples/<filename>` | 获取示例图片 |
| GET | `/api/uploads/<filename>` | 获取上传图片 |
| POST | `/api/predict` | 提交预测请求（支持文件上传和示例选择） |

### POST `/api/predict` 请求示例

```bash
# 使用示例影像
curl -X POST http://localhost:5001/api/predict \
  -F "age=72" -F "sex=male" -F "sample=sub-0001_axial.png"

# 上传图片文件
curl -X POST http://localhost:5001/api/predict \
  -F "age=65" -F "sex=female" -F "image=@brain_scan.png"
```

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 点击「使用示例影像」无响应 | `samples/` 目录缺失 | 确认 `samples/` 目录存在且包含 PNG 文件 |
| 页面报 `TemplateNotFound` | 工作目录不正确 | 确保在项目根目录下执行 `python app.py` |
| 上传后提示 `Invalid file type` | 文件格式不在白名单 | 使用 PNG / JPG / TIFF / BMP / WEBP 格式 |
| 端口 5001 被占用 | 其他服务占用端口 | 修改 `app.py` 中 `port=5001` 为其他端口 |
| `command not found: python` | 虚拟环境未激活 | 使用 `./venv/bin/python app.py` 绝对路径启动 |
| 预测结果每次不同 | 当前为 Mock 随机推理 | 接入真实模型后结果将稳定可复现 |

## License

MIT
