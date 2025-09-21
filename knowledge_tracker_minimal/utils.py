import os, sqlite3, hashlib
from PIL import Image, ImageOps
import pytesseract
from pypdf import PdfReader
import magic

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY,
        title TEXT,
        summary TEXT,
        content TEXT,
        keywords TEXT,
        category TEXT,
        filepath TEXT,
        source TEXT,
        hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    cur.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(title, summary, content, keywords, filepath, content='docs', content_rowid='id');
    ''')
    conn.commit()
    return conn

def insert_doc(conn, title, summary, content, keywords, category, filepath, source):
    cur = conn.cursor()
    h = hashlib.sha256((content or '').encode('utf-8')).hexdigest()
    cur.execute('SELECT id FROM docs WHERE hash = ?', (h,))
    if cur.fetchone():
        return None
    cur.execute('INSERT INTO docs (title, summary, content, keywords, category, filepath, source, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (title, summary, content, keywords, category, filepath, source, h))
    rowid = cur.lastrowid
    cur.execute('INSERT INTO docs_fts(rowid, title, summary, content, keywords, filepath) VALUES (?, ?, ?, ?, ?, ?)',
                (rowid, title, summary, content, keywords, filepath))
    conn.commit()
    return rowid

def extract_text_from_pdf(path):
    try:
        reader = PdfReader(path)
        texts = []
        for p in reader.pages:
            texts.append(p.extract_text() or '')
        return '\n'.join(texts)
    except Exception as e:
        print('PDF extract error', e)
        return ''

def extract_text_from_image(path):
    try:
        img = Image.open(path)
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass
        return pytesseract.image_to_string(img)
    except Exception as e:
        print('Image OCR error', e)
        return ''

def guess_mime(path):
    try:
        return magic.from_file(path, mime=True)
    except Exception:
        ext = os.path.splitext(path)[1].lower()
        if ext=='.pdf': return 'application/pdf'
        if ext in ['.png','.jpg','.jpeg']: return 'image/jpeg'
        return 'application/octet-stream'
