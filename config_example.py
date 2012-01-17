# list of directories to backup
DIRS = [('source_path_1', 'target_1'),
        ('source_path_n', 'target_n')]

# list of databases to backup
DBS = [('db_name_1', 'target_1'),
       ('db_name_n', 'target_n')]

# how long to keep each archive 
TTL = '14D'

# target url where to save backup (see duplicity url format ...)
BASE_URL = 'ftp://user[:password]@other.host[:port]'

# options to pass to duplicity
DUP_OPTIONS = '--no-encryption --ftp-regular -v4'  
ENV = {'FTP_PASSWORD':''}

# mysqldump options
SQL_OPTIONS = '--opt -u user --password=password'

# path to temp directory to save sql dump
TMP_DIR = '/tmp'
