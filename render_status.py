"""
Render status JSON to HTML.
"""

import os
import sys
import json
import jinja2
import shutil
import itertools
from glob import glob
from datetime import datetime


TEMPLATE_DIR = 'templates'
STYLESHEET_FILE = os.path.join(TEMPLATE_DIR, 'stylesheets/main.css')


def render_status(directory):
    files = glob(os.path.join(directory, '*.json'))

    if not files:
        raise StandardError('No json found in %s' % directory)

    # read all statuses
    status_lists = [json.load(open(f)) for f in files]
    # sort statuses by id
    extract_id = lambda s: s['id']
    statuses = sorted(itertools.chain(*status_lists), key=extract_id, reverse=True)

    # group statuses by year
    status_groups = itertools.groupby(statuses, lambda s: int(s['dtime'][:s['dtime'].index('-')]))

    # load template
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
        extensions=['pyjade.ext.jinja.PyJadeExtension']
    )
    template = env.get_template('page.html')

    args = {
        'author': statuses[0]['name'],
        'year': datetime.now().year,
        'status_groups': status_groups,
    }

    page = template.render(args)

    outfile = os.path.join(directory, 'page.html')
    with open(outfile, 'w') as output:
        output.write(page.encode('utf-8'))

    # copy css
    shutil.copy(STYLESHEET_FILE, directory)

    print 'File saved to', outfile

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python %s <status_directory>' % sys.argv[0]
        sys.exit(1)

    render_status(sys.argv[1])
