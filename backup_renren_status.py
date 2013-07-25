"""
Login renren.com with given credentials and output status into files.
The files are saved in JSON format to the directory named by current user's ID.
The files are utf8-encoded and named as <page-number>.json, e.g. 0.json.
The smaller the page number is, the newer the statuses are.
Each file corresponds to a page of statuses.
"""

import os
import re
import sys
import math
import json
import time
import requests


RESULT_DIR = 'results'
LOGIN_PAGE = 'http://www.renren.com/GLogin.do'
LOGIN_URL = 'http://www.renren.com/PLogin.do'
LOGOUT_URL = 'http://www.renren.com/Logout.do'
STATUS_API = 'http://status.renren.com/GetSomeomeDoingList.do'
STATUS_PER_PAGE = 20.0


def get_page_statuses(user_id, page_no, session):
    r = session.get(STATUS_API, params={'userId': user_id, 'curpage': page_no})
    return json.loads(r.text)


def get_status_meta(user_id, session):
    data = get_page_statuses(user_id, 0, session)
    return data['name'], data['count']


def backup_status(user_email, user_passwd):
    # start a http session
    s = requests.Session()
    # get initial cookies, dunno if it's necessary.
    # but let's be safe.
    s.get(LOGIN_PAGE)
    headers = {
        'email': user_email,
        'password': user_passwd,
        'domain': 'renren.com',
        'isplogin': 'true'
    }
    r = s.post(LOGIN_URL, headers)

    if 'SysHome.do' in r.url:
        # login failed
        raise StandardError('Invalid credentials')

    # get user ID
    user_id = int(re.search(r'\d+', r.url).group(0))
    print 'User id is', user_id

    if not os.path.exists(RESULT_DIR):
        print 'Create result dir <%s>...' % RESULT_DIR
        os.mkdir(RESULT_DIR)

    dir_name = os.path.join(RESULT_DIR, str(user_id))
    if os.path.exists(dir_name):
        raise StandardError('Target directory name %s already exists' % dir_name)

    # create directory for better organization
    os.mkdir(dir_name)

    # get first page of statuses
    user_name, status_count = get_status_meta(user_id, s)
    print 'Owner name:', user_name
    print 'Status count:', status_count
    pages = int(math.ceil(status_count/STATUS_PER_PAGE))
    print 'Page count:', pages

    # save statuses
    for i in range(pages):
        data = get_page_statuses(user_id, i, s)
        file_name = os.path.join(dir_name, '%d.json'%i)
        with open(file_name, 'wb') as f:
            json_str = json.dumps(data['doingArray'], ensure_ascii=False)
            f.write(json_str.encode('utf-8'))

        progress_bar(1.0*(i+1)/pages)
        # sleep for one second to avoid quota exceeding
        time.sleep(1)

    # put cursor to new line
    print

    # logout
    s.get(LOGOUT_URL)
    print 'All set, congratulations!'


def progress_bar(progress, col_width=80):
    """
    Text progress bar in command line.
    pre-condition: the cursor is at a new line.
    post-condition: the cursor is at the end of the same line.
    """
    progress_width = col_width - 10
    finished = int(progress * progress_width)
    progress_str = '#'*finished + '-'*(progress_width-finished)
    sys.stdout.write('\r[%s](%.1f%%)' % (progress_str, 100*progress))
    sys.stdout.flush()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage: python %s <user_email> [<user_password>|-p]' % sys.argv[0]
        print '      use -p option to input password without echoing'
        sys.exit(1)

    user_email = sys.argv[1]
    user_pass = sys.argv[2]
    if user_pass == '-p':
        from getpass import getpass
        user_pass = getpass()

    backup_status(user_email, user_pass)
