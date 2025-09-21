import os, argparse
from utils import init_db, extract_text_from_pdf, extract_text_from_image, insert_doc, guess_mime

def ingest(base_folder, db_path, dry_run=False):
    conn = init_db(db_path)
    for root, dirs, files in os.walk(base_folder):
        for f in files:
            path = os.path.join(root, f)
            mime = guess_mime(path)
            title = os.path.relpath(path, base_folder)
            if mime == 'application/pdf':
                text = extract_text_from_pdf(path)
            elif mime.startswith('image'):
                text = extract_text_from_image(path)
            else:
                text = ''
            summary = '\n'.join([l for l in text.splitlines() if l][:5])
            if not dry_run:
                insert_doc(conn, title, summary, text, '', os.path.basename(root), path, 'local')
    print('Ingest complete.')

if __name__=='__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--base-folder', required=True)
    p.add_argument('--db', default='knowledge.db')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    ingest(args.base_folder, args.db, args.dry_run)
