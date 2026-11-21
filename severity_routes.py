"""Add-on for the original AgroVision Flask app. No detector code is replaced."""
import logging
import os
from pathlib import Path
from uuid import uuid4

import cv2
from flask import abort, render_template, request, url_for
from werkzeug.utils import secure_filename
from analysis_history import save_analysis, recent_analyses, get_analysis, all_analyses
from severity_segmentation import estimate_leaf_lesion_pixels

logger = logging.getLogger(__name__)


def register_severity_routes(app, model, allowed_file):
    """Register independent severity/history endpoints using the existing model."""
    upload_folder = str(Path(app.static_folder) / 'severity_uploads')
    os.makedirs(upload_folder, exist_ok=True)

    @app.route('/severity', methods=['GET', 'POST'])
    def severity_dashboard():
        """Pixel-level experimental color segmentation severity dashboard."""
        error = None
        image_url = None
        overlay_url = None
        leaf_mask_url = None
        filename = None
        detections_data = []
        severity_percent = None
        severity_label = None
        leaf_pixels = None
        lesion_pixels = None

        if request.method == 'POST':
            uploaded = request.files.get('file')
            if not uploaded or uploaded.filename == '':
                error = 'Please choose a rice leaf image.'
            elif not allowed_file(uploaded.filename):
                error = 'Only PNG, JPG and JPEG images are supported.'
            else:
                filename = secure_filename(uploaded.filename) or 'leaf.jpg'
                stamp = uuid4().hex
                saved_name = f'severity_{stamp}_{filename}'
                filepath = os.path.join(upload_folder, saved_name)
                uploaded.save(filepath)
                image = cv2.imread(filepath)
                if image is None:
                    error = 'The uploaded image could not be opened.'
                    os.remove(filepath)
                else:
                    image_url = url_for('static', filename=f'severity_uploads/{saved_name}')
                    try:
                        result = model.predict(source=image, verbose=False)[0]
                        if result.boxes is not None:
                            for box in result.boxes:
                                name = str(result.names[int(box.cls[0])])
                                detections_data.append({'name': name, 'confidence': round(float(box.conf[0])*100, 1)})
                    except Exception:
                        logger.exception('YOLO prediction failed')
                        error = 'Image accepted, but disease detection could not complete.'
                    try:
                        segmentation = estimate_leaf_lesion_pixels(image)
                        overlay_name = f'severity_overlay_{stamp}.jpg'
                        leaf_mask_name = f'severity_leafmask_{stamp}.png'
                        if not cv2.imwrite(os.path.join(upload_folder, overlay_name), segmentation['overlay']):
                            raise ValueError('Could not save overlay')
                        if not cv2.imwrite(os.path.join(upload_folder, leaf_mask_name), segmentation['leaf_mask']):
                            raise ValueError('Could not save mask')
                        severity_percent = segmentation['severity_percent']
                        leaf_pixels = segmentation['leaf_pixels']
                        lesion_pixels = segmentation['lesion_pixels']
                        severity_label = 'Experimental estimate — ' + segmentation.get('method', 'GrabCut')
                        overlay_url = url_for('static', filename=f'severity_uploads/{overlay_name}')
                        leaf_mask_url = url_for('static', filename=f'severity_uploads/{leaf_mask_name}')
                    except Exception:
                        logger.exception('Severity estimation failed')
                        severity_label = 'Severity unavailable: uncertain leaf boundary'
                        error = ((error + ' ') if error else '') + 'Image accepted. A reliable leaf mask could not be generated; disease detection is independent of severity.'
                    try:
                        save_analysis(filename, detections_data, severity_percent, image_url, overlay_url, leaf_mask_url, leaf_pixels, lesion_pixels, severity_label, error)
                    except Exception:
                        logger.exception('History save failed')
                        error = ((error + ' ') if error else '') + 'History could not be saved.'

        return render_template('severity.html', error=error, image_url=image_url,
                               overlay_url=overlay_url, leaf_mask_url=leaf_mask_url,
                               filename=filename, detections_data=detections_data,
                               severity_percent=severity_percent, severity_label=severity_label,
                               leaf_pixels=leaf_pixels, lesion_pixels=lesion_pixels, recent=recent_analyses())

    @app.route('/history')
    def history_dashboard():
        return render_template('history.html', recent=all_analyses(), full_history=True)

    @app.route('/history/<int:analysis_id>')
    def view_report(analysis_id):
        report = get_analysis(analysis_id)
        if report is None:
            abort(404)
        return render_template('report.html', report=report)

