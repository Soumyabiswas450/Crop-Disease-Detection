import sqlite3, json
from pathlib import Path
from datetime import datetime
from contextlib import closing
DB = Path(__file__).resolve().parent / 'analysis_history.sqlite3'
EXTRA = {'leaf_mask':'TEXT','leaf_pixels':'INTEGER','lesion_pixels':'INTEGER','severity_label':'TEXT','warning':'TEXT'}
def connect():
    conn = sqlite3.connect(DB, timeout=15)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute('BEGIN IMMEDIATE')
        conn.execute('CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY, created TEXT, filename TEXT, diseases TEXT, severity REAL, image TEXT, overlay TEXT)')
        cols = {r[1] for r in conn.execute('PRAGMA table_info(analyses)')}
        for name, kind in EXTRA.items():
            if name not in cols: conn.execute(f'ALTER TABLE analyses ADD COLUMN {name} {kind}')
    return conn
def save_analysis(filename, diseases, severity, image, overlay, leaf_mask=None, leaf_pixels=None, lesion_pixels=None, severity_label=None, warning=None):
    with closing(connect()) as conn, conn:
        conn.execute('INSERT INTO analyses (created,filename,diseases,severity,image,overlay,leaf_mask,leaf_pixels,lesion_pixels,severity_label,warning) VALUES (?,?,?,?,?,?,?,?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),filename,json.dumps(diseases),severity,image,overlay,leaf_mask,leaf_pixels,lesion_pixels,severity_label,warning))
def decode(row):
    if row is None: return None
    row = dict(row); row['diseases'] = json.loads(row['diseases']); return row
def recent_analyses():
    with closing(connect()) as conn: return [decode(r) for r in conn.execute('SELECT * FROM analyses ORDER BY id DESC LIMIT 20')]
def all_analyses():
    with closing(connect()) as conn: return [decode(r) for r in conn.execute('SELECT * FROM analyses ORDER BY id DESC')]
def get_analysis(analysis_id):
    with closing(connect()) as conn: return decode(conn.execute('SELECT * FROM analyses WHERE id=?',(analysis_id,)).fetchone())
