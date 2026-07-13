"""
NeuroAge - Brain Age Prediction System
Flask backend with image upload API
"""

import os
import json
import random
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['SAMPLES_FOLDER'] = os.path.join(os.path.dirname(__file__), 'brain')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'webp'}

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_prediction(image_path, age, sex):
    """
    Mock brain age prediction — returns random but clinically reasonable values.
    In production, this would call the actual CLIP + MoE model.
    """
    # Generate brain age: normally distributed around chronological age
    # Mean offset +2yr (slight aging bias), std 4yr for variety
    age_offset = random.gauss(2.0, 4.0)
    brain_age = round(age + age_offset, 1)
    brain_age = max(30, min(100, brain_age))  # clamp

    delta = round(brain_age - age, 1)

    # Generate staging probabilities
    if brain_age - age > 5:
        ad_prob = random.uniform(0.55, 0.85)
        mci_prob = random.uniform(0.10, 0.30)
        cn_prob = round(1 - ad_prob - mci_prob, 3)
        staging = 'AD'
        staging_desc = '阿尔茨海默病'
    elif brain_age - age > 1:
        mci_prob = random.uniform(0.55, 0.85)
        cn_prob = random.uniform(0.05, 0.25)
        ad_prob = round(1 - mci_prob - cn_prob, 3)
        staging = 'MCI'
        staging_desc = '轻度认知障碍'
    else:
        cn_prob = random.uniform(0.75, 0.92)
        mci_prob = random.uniform(0.05, 0.15)
        ad_prob = round(1 - cn_prob - mci_prob, 3)
        staging = 'CN'
        staging_desc = '认知正常'

    cn_prob = round(max(0.01, cn_prob), 3)
    mci_prob = round(max(0.01, mci_prob), 3)
    ad_prob = round(max(0.01, ad_prob), 3)

    # Normalize
    total = cn_prob + mci_prob + ad_prob
    cn_prob = round(cn_prob / total * 100, 1)
    mci_prob = round(mci_prob / total * 100, 1)
    ad_prob = round(100 - cn_prob - mci_prob, 1)

    # Brain region attribution scores
    region_base = {
        '海马体': (0.7, 0.2),
        '内侧颞叶': (0.6, 0.2),
        '前额叶皮层': (0.5, 0.2),
        '脑室系统': (0.45, 0.2),
        '顶叶': (0.35, 0.15),
        '基底节': (0.3, 0.15),
        '小脑': (0.25, 0.12),
        '枕叶': (0.2, 0.1),
    }

    region_sub = {
        '海马体': 'Hippocampus',
        '内侧颞叶': 'Medial Temporal',
        '前额叶皮层': 'Prefrontal Cortex',
        '脑室系统': 'Ventricular System',
        '顶叶': 'Parietal Lobe',
        '基底节': 'Basal Ganglia',
        '小脑': 'Cerebellum',
        '枕叶': 'Occipital Lobe',
    }

    # Scale region scores by staging severity
    severity = max(0.3, min(1.0, (brain_age - age + 5) / 15))
    regions = []
    for name, (base, std) in region_base.items():
        score = int(min(99, max(5, (base * severity + random.gauss(0, std)) * 100)))
        regions.append({
            'name': name,
            'sub': region_sub[name],
            'score': score,
        })
    regions.sort(key=lambda x: x['score'], reverse=True)

    # Image info
    try:
        img = Image.open(image_path)
        w, h = img.size
    except:
        w, h = 256, 256

    return {
        'brain_age': brain_age,
        'chronological_age': age,
        'delta': delta,
        'staging': staging,
        'staging_desc': staging_desc,
        'probabilities': {
            'cn': cn_prob,
            'mci': mci_prob,
            'ad': ad_prob,
        },
        'confidence': round(max(cn_prob, mci_prob, ad_prob), 1),
        'regions': regions,
        'image_info': {
            'width': w,
            'height': h,
            'filename': os.path.basename(image_path),
        },
        'model_info': {
            'version': 'NeuroAge v1.0',
            'backbone': 'CLIP ViT-L/14 + MoE-4',
            'dataset': 'OASIS-3 + ADNI',
            'qwk': 0.823,
        },
    }


# ── Routes ──

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/samples')
def list_samples():
    """List available sample brain MRI images."""
    samples_dir = app.config['SAMPLES_FOLDER']
    if not os.path.isdir(samples_dir):
        return jsonify([])

    files = sorted([
        f for f in os.listdir(samples_dir)
        if allowed_file(f)
    ])

    # Group by subject
    subjects = {}
    for f in files:
        parts = f.rsplit('_', 1)
        if len(parts) == 2:
            sub_id = parts[0]
            view = parts[1].rsplit('.', 1)[0]
            if sub_id not in subjects:
                subjects[sub_id] = {'id': sub_id, 'views': {}}
            subjects[sub_id]['views'][view] = f

    return jsonify(list(subjects.values()))


@app.route('/api/samples/<path:filename>')
def serve_sample(filename):
    """Serve a sample image."""
    return send_from_directory(app.config['SAMPLES_FOLDER'], filename)


@app.route('/api/uploads/<path:filename>')
def serve_upload(filename):
    """Serve an uploaded image."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Accept an image upload and return brain age prediction.
    Supports both file upload (multipart) and sample selection (JSON).
    """
    age = int(request.form.get('age', 72))
    sex = request.form.get('sex', 'male')
    image_path = None
    saved_filename = None

    # Case 1: Sample image selected
    sample_name = request.form.get('sample')
    if sample_name:
        image_path = os.path.join(app.config['SAMPLES_FOLDER'], secure_filename(sample_name))
        if not os.path.isfile(image_path):
            return jsonify({'error': f'Sample not found: {sample_name}'}), 404

    # Case 2: File upload
    elif 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file and allowed_file(file.filename):
            saved_filename = secure_filename(file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(image_path)
        else:
            return jsonify({'error': 'Invalid file type'}), 400

    else:
        return jsonify({'error': 'No image provided. Upload a file or select a sample.'}), 400

    # Run prediction
    result = generate_prediction(image_path, age, sex)

    # Add image URL for display
    if saved_filename:
        result['image_url'] = f'/api/uploads/{saved_filename}'
    elif sample_name:
        result['image_url'] = f'/api/samples/{sample_name}'

    return jsonify(result)


if __name__ == '__main__':
    print("\n  NeuroAge - Brain Age Prediction System")
    print("  http://localhost:5001\n")
    app.run(host='0.0.0.0', port=5001, debug=True)
