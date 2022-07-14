#!/usr/bin/env python3
# Script to retrieve 496 online Data files of 'ds083.3',
# total 101.75G. This script uses 'requests' to download data.
#
# Highlight this script by Select All, Copy and Paste it into a file;
# make the file executable and run it on command line.
#
# You need pass in your password as a parameter to execute
# this script; or you can set an environment variable RDAPSWD
# if your Operating System supports it.
#
# Contact rpconroy@ucar.edu (Riley Conroy) for further assistance.
#################################################################

import sys, os
import requests
import datetime

def check_file_status(filepath, filesize):
    sys.stdout.write('\r')
    sys.stdout.flush()
    size = int(os.stat(filepath).st_size)
    percent_complete = (size/filesize)*100
    sys.stdout.write('%.3f %s' % (percent_complete, '% Completed'))
    sys.stdout.flush()

# Try to get password
if len(sys.argv) < 2 and not 'RDAPSWD' in os.environ:
    try:
        import getpass
        input = getpass.getpass
    except:
        try:
            input = raw_input
        except:
            pass
    email = input('Input your email [user@domain.com]: ')
    print(email)
    # precisa colocar a data, por exemplo: 2020,1,15
    initial_date = input('Input the inital date [yyyy,m,d]: ')
    print(initial_date)
    # precisa colocar a data, por exemplo: 2020,12,22
    final_date = input('Input the final date [yyyy,m,d]: ')
    print(final_date)
    pswd = input('Password: ')
    # convert to datetime format
    initial = datetime.datetime.strptime(initial_date, '%Y,%m,%d')
    final = datetime.datetime.strptime(final_date, '%Y,%m,%d')
    # year = input('year (4 digits): ')
    # month = int(input('number month: '))
    # pswd = input('Password: ')
else:
    try:
        pswd = sys.argv[1]
    except:
        pswd = os.environ['RDAPSWD']

url = 'https://rda.ucar.edu/cgi-bin/login'
values = {'email' : email, 'passwd' : pswd, 'action' : 'login'}
# Authenticate
ret = requests.post(url,data=values)
if ret.status_code != 200:
    print('Bad Authentication')
    print(ret.text)
    exit(1)
dspath = 'https://rda.ucar.edu/data/ds083.3/'
filelist=[]

delta = final - initial # calculate the number of days

for i in range(delta.days + 1):
    day = initial + datetime.timedelta(days=i)
    for j in [0,6,12,18]:
        arq = f'{day.year}/{day.year}{day.month:02}/gdas1.fnl0p25.{day.year}{day.month:02}{day.day:02}{j:02}.f00.grib2'
        #print(arq)
        filelist.append(arq)
# print(filelist)
for file in filelist:
    filename=dspath+file
    file_base = os.path.basename(file)
    print('Downloading',file_base)
    req = requests.get(filename, cookies = ret.cookies, allow_redirects=True, stream=True)
    filesize = int(req.headers['Content-length'])
    with open(file_base, 'wb') as outfile:
        chunk_size=1048576
        for chunk in req.iter_content(chunk_size=chunk_size):
            outfile.write(chunk)
            if chunk_size < filesize:
                check_file_status(file_base, filesize)
    check_file_status(file_base, filesize)
    print()

