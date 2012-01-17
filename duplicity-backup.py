#! /usr/bin/env python

# Run in a cron as:
# ./duplicity-backup.py config_file 2>&1 | mail -s 'Daily Backup' you@your_email.com

import os
import re
import subprocess
import sys

# quick and dirty way of doing configuration files
CONFIG_VARS = ('DIRS', 'DBS', 'TTL', 'BASE_URL', 'ENV', 
               'DUP_OPTIONS', 'SQL_OPTIONS', 'TMP_DIR')

def read_config(path):
    cf = {}; execfile(path, cf, cf)
    for v in CONFIG_VARS:
        globals()[v] = cf[v]

def get_envs():
    return ' '.join('%s="%s"' % (a,b) for a, b in ENV.items())

def get_mysqldump_cmd(dbname, out):
    return 'mysqldump %s -r %s %s' % (SQL_OPTIONS, out, dbname)

def get_duplicity_cmd(source_dir, turl):
    ttl = re.match('(^\d+)(.*)', TTL)
    ttl = '%s%s' % (2*int(ttl.group(1)), ttl.group(2))
    return '%s duplicity %s --full-if-older-than %s %s %s' % (get_envs(), DUP_OPTIONS, ttl, source_dir, turl)

def call(cmd, test=False):
    print '>> Running:  %s' % cmd
    if not test:
        out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print out.stdout.read()

def get_target_url(path):
    return os.path.join(BASE_URL, path)

def cleanup():
    def get_cleanup_cmd(turl):
        return '%s duplicity remove-older-than %s %s --force %s' % (get_envs(), TTL, DUP_OPTIONS, turl)
    for i, o in DBS + DIRS:
        call(get_cleanup_cmd(get_target_url(o)))
    
def backup_dbs():
    for i, o in DBS:
        out = os.path.join(TMP_DIR, o)
        call(get_mysqldump_cmd(i, out))
        call(get_duplicity_cmd(out, get_target_url(o)))
        
def backup_files():
    for i, o in DIRS:
        call(get_duplicity_cmd(i, get_target_url(o)))
        
def get_stats():
    def get_list_cmd(turl):
        return '%s duplicity collection-status %s %s' % (get_envs(), DUP_OPTIONS, turl)
    for i, o in DBS + DIRS:
        call(get_list_cmd(get_target_url(o)))

def run(config_path):
    read_config(config_path)
    print '#' * 80
    print '1) Cleaning up files older than "%s" ...' % TTL
    cleanup()
    print '#' * 80
    print '2) Backing up databases "%s" ...' % ' '.join(d[0] for d in DBS)
    backup_dbs()
    print '#' * 80
    print '3) Backing up directories "%s" ...' % ' '.join(d[0] for d in DIRS)
    backup_files()
    print '#' * 80
    print '4) Getting some stats ...'
    get_stats()
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Usage: python duplicity-backup.py config_path'
    else:
        run(sys.argv[1])
