# AgroVision – Severity and Recent Analysis add-on

This package adds a separate experimental color-based severity dashboard, persistent SQLite history, and individual saved reports, using the existing `model` object. It does not replace the original app, detector, EigenCAM, trained weights or knowledge base.

## Install on a fresh feature branch
Copy the package contents into the root of the repository. In `app.py`, immediately before the existing `if __name__ == '__main__':` block, insert:

```python
from severity_routes import register_severity_routes
register_severity_routes(app, model, allowed_file)

```

In `templates/index.html`, inside the sidebar after the Disease detector link, add:

```html
<a class="nav-item" href="/severity"><span class="nav-icon">◉</span> Disease Severity Estimation</a>
<a class="nav-item" href="/history"><span class="nav-icon">◷</span> Recent Analysis</a>
```

Append these lines to the existing `.gitignore` (do not replace it):

```text
/analysis_history.sqlite3*
/static/severity_uploads/
```

Run in the original Python environment: `py -m flask --app app run --port 5001`.

Test `/` (original detection and EigenCAM), `/severity`, `/history` and `/history/<id>` (via View Report). Test a valid image with an uncertain mask, a valid image with a usable mask, and a corrupt image. Check history remains accessible after restarting. No new Python packages needed if the original app's Flask/OpenCV/NumPy environment is installed.

The last 20 analyses appear on `/severity`; all saved analyses appear on `/history`. The database is created automatically. Old local history can be migrated by copying its database and the corresponding saved image files into their original relative locations, but never upload them to GitHub. Each installation has shared local history, not user-specific accounts. Do not expose the app publicly without authentication and upload size/resource limits.

The severity measure uses classical OpenCV GrabCut with an HSV fallback. It is experimental, not a validated disease-specific lesion measurement. Invalid files are rejected; valid decodable leaf images can still be viewed and saved with unavailable severity if a reliable mask cannot be generated. Existing YOLO predictions are separate from severity.
