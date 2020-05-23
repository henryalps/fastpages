"""Converts Jupyter Notebooks to Jekyll compliant blog posts"""
from datetime import datetime
import re, os, logging
from nbdev import export2html
from nbdev.export2html import Config, Path, _re_digits, _to_html, _re_block_notes
from fast_template import rename_for_jekyll
import shutil
import json
import base64
warnings = set()

# Cell
_re_att_ref = re.compile(r' *!\[(.*)\]\(attachment:image.png(?: "(.*)")?\)')

# Cell
try: from PIL import Image
except: pass # Only required for _update_att_ref

# Cell
_tmpl_img = '<img alt="{title}" caption="{title}" id="{id}" src="data:{mime};base64,{img}">'

# Cell
def first(x):
    "First element of `x`, or None if missing"
    try: return next(iter(x))
    except StopIteration: return None

def _update_att_ref(line, mime, img):
    m = _re_att_ref.match(line)
    if not m: return line
    alt,title = m.groups()
    if not title: title = "TK: add title"
    return _tmpl_img.format(title=title, id='TK: add it', mime=mime, img=img)

# Cell
def _nb_detach_cell(cell, dest, use_img):
    att,src = cell['attachments'],cell['source']
    print(att)
    print(att.values())
    mime,img = first(first(att.values()).items())
#    ext = mime.split('/')[1]
#    for i in range(99999):
#        p = dest/(f'att_{i:05d}.{ext}')
#        if not p.exists(): break
#    img_decode = base64.b64decode(img)
#    p.write_bytes(img_decode)
    del(cell['attachments'])
    print('***************************')
    if use_img:  return [_update_att_ref(o,mime,img) for o in src]
    else: return [o.replace('attachment:image.png', str(p)) for o in src]

# Cell
def nb_detach_cells(path_nb, dest=None, replace=True, use_img=True):
    "Export cell attachments to `dest` and update references"
    path_nb = Path(path_nb)
    if not dest: dest = f'{path_nb.stem}_files'
    dest = Path(dest)
    dest.mkdir(exist_ok=True, parents=True)
    j = json.load(path_nb.open())
    atts = [o for o in j['cells'] if 'attachments' in o]
    for o in atts: o['source'] = _nb_detach_cell(o, dest, use_img)
    if atts and replace: json.dump(j, path_nb.open('w'))
    if not replace: return j

# Modify the naming process such that destination files get named properly for Jekyll _posts
def _nb2htmlfname(nb_path, dest=None):
    fname = rename_for_jekyll(nb_path, warnings=warnings)
    if dest is None: dest = Config().doc_path
    return Path(dest)/fname

# TODO: Open a GitHub Issue in addition to printing warnings
for original, new in warnings:
    print(f'{original} has been renamed to {new} to be complaint with Jekyll naming conventions.\n')

## apply monkey patches
export2html._nb2htmlfname = _nb2htmlfname
arrs = os.listdir('_notebooks')
print('************')
for arr in arrs:
    if arr.endswith('ipynb'):
        nb_detach_cells('_notebooks/' + arr,dest='images/')
#        if Path('_notebooks/'+arr.replace('.ipynb', '')+'_files').is_dir():
#            shutil.rmtree('_notebooks/'+arr.replace('.ipynb', '')+'_files')
#        shutil.move(arr.replace('.ipynb', '')+'_files', '_notebooks/')
export2html.notebook2html(fname='_notebooks/*.ipynb', dest='_posts/', template_file='/fastpages/fastpages.tpl')
