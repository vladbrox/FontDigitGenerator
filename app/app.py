# app.py
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, ImageColor
import os
import zipfile
import io
import tempfile
import logging
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
app.logger.setLevel(logging.DEBUG)

ALLOWED_EXTENSIONS = {'ttf', 'otf'}
SUPPORTED_FORMATS = ['png', 'jpeg']
DEFAULT_QUALITY = 85

class FontProcessor:
    def __init__(self, font_stream):
        self.font_stream = font_stream
        self._validate_font()

    def _validate_font(self):
        try:
            ImageFont.truetype(self.font_stream, 10)
            self.font_stream.seek(0)
        except Exception as e:
            raise ValueError(f"Invalid font file: {str(e)}")

    def calculate_font_size(self, digit, max_width, max_height):
        self.font_stream.seek(0)
        low, high = 1, 2 * max(max_width, max_height)
        best_size = 1
        last_successful = None

        for _ in range(20):
            mid = (low + high) // 2
            try:
                font = ImageFont.truetype(self.font_stream, mid)
                self.font_stream.seek(0)
                bbox = font.getbbox(str(digit))
                
                if not bbox:
                    continue

                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                if text_width <= max_width * 0.9 and text_height <= max_height * 0.9:
                    last_successful = font
                    best_size = mid
                    low = mid + 1
                else:
                    high = mid - 1
            except:
                high = mid - 1

        if last_successful is None:
            try:
                return 1, ImageFont.truetype(self.font_stream, 1)
            except:
                raise RuntimeError("Font size calculation failed")
        
        return best_size, last_successful

def validate_color(color_str):
    try:
        color = ImageColor.getrgb(color_str)
        return color + (255,) if len(color) == 3 else color
    except ValueError:
        try:
            return ImageColor.getrgba(color_str)
        except:
            raise ValueError(f"Invalid color: {color_str}")

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    try:
        if 'font_file' not in request.files:
            return jsonify(error="No font file uploaded"), 400
            
        font_file = request.files['font_file']
        if not font_file or not allowed_file(font_file.filename):
            return jsonify(error="Invalid font file"), 400

        width = int(request.form.get('width', 200))
        height = int(request.form.get('height', 200))
        text_color = validate_color(request.form.get('text_color', '#000000'))
        bg_color = validate_color(request.form.get('bg_color', '#ffffff'))
        image_format = request.form.get('format', 'png').lower()
        quality = int(request.form.get('quality', DEFAULT_QUALITY))

        if image_format not in SUPPORTED_FORMATS:
            return jsonify(error="Unsupported image format"), 400

        font_stream = io.BytesIO(font_file.read())
        processor = FontProcessor(font_stream)
        
        digit = int(request.form.get('preview_digit', 0))
        font_size, font = processor.calculate_font_size(digit, width, height)

        img = Image.new('RGBA', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        bbox = font.getbbox(str(digit))
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) / 2 - bbox[0]
        y = (height - text_height) / 2 - bbox[1]
        
        draw.text((x, y), str(digit), font=font, fill=text_color)

        if image_format == 'jpeg':
            img = img.convert('RGB')

        img_bytes = io.BytesIO()
        img.save(img_bytes, format=image_format, quality=quality, optimize=True)
        img_bytes.seek(0)

        return send_file(img_bytes, mimetype=f'image/{image_format}')

    except Exception as e:
        app.logger.error(f"Preview error: {str(e)}")
        return jsonify(error=str(e)), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        start_time = datetime.now()
        font_file = request.files['font_file']
        width = int(request.form['width'])
        height = int(request.form['height'])
        text_color = validate_color(request.form['text_color'])
        bg_color = validate_color(request.form['bg_color'])
        image_format = request.form.get('format', 'png').lower()
        quality = int(request.form.get('quality', DEFAULT_QUALITY))

        if image_format not in SUPPORTED_FORMATS:
            raise ValueError("Unsupported image format")

        font_stream = io.BytesIO(font_file.read())
        processor = FontProcessor(font_stream)
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            with tempfile.TemporaryDirectory() as tmp_dir:
                for digit in range(10):
                    font_size, font = processor.calculate_font_size(digit, width, height)
                    img = Image.new('RGBA', (width, height), bg_color)
                    draw = ImageDraw.Draw(img)
                    
                    bbox = font.getbbox(str(digit))
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x = (width - text_width) / 2 - bbox[0]
                    y = (height - text_height) / 2 - bbox[1]
                    
                    draw.text((x, y), str(digit), font=font, fill=text_color)

                    if image_format == 'jpeg':
                        img = img.convert('RGB')

                    filename = f"{digit}.{image_format}"
                    img_path = os.path.join(tmp_dir, filename)
                    img.save(img_path, format=image_format, quality=quality, optimize=True)
                    zip_file.write(img_path, filename)

        zip_buffer.seek(0)
        app.logger.info(f"Generation completed in {(datetime.now() - start_time).total_seconds()}s")
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'digits_{datetime.now().strftime("%Y%m%d%H%M%S")}.zip'
        )

    except Exception as e:
        app.logger.error(f"Generation error: {str(e)}")
        return jsonify(error=str(e)), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(port=5000)