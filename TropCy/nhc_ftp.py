import os
import ftplib
from datetime import datetime
import time as _time

################################
################################
######## FTP library. 
#  open NHC ftp connection 
# def open_atcf():
#   ftp = ftplib.FTP("ftp.nhc.noaa.gov")
#   ftp.login("anonymous","abrammer@albany.edu")
#   ftp.cwd("atcf/")
#   return ftp
#   
# def check_ftp(ftp):
#   try:
#     ret = ftp.voidcmd("NOOP")
#   except AttributeError:
#     print("Reopening ftp")
#     ftp = open_atcf()
#   return ftp
# 
#   pull down new file from ftp; set access and modified times to match the server time
# def grab_file(ftp, f):
#     ftp.retrbinary("RETR "+f, open(f,"wb").write)
#     resp = ftp.sendcmd("MDTM "+f)
#     timestamp = _time.mktime(datetime.strptime(resp[4:18],"%Y%m%d%H%M%S").timetuple())
#     os.utime(f, (timestamp, timestamp))  # set a/m time to match server time
# 
#  Check modified time on server against local, if server is newer pull new file and return true
# def fetch_recent_ftp(ftp, f):  
#   ftp = check_ftp(ftp)
#   print( "Checking recent "+f)
#   if not os.path.isfile(f):
#     grab_file(ftp, f)
#     ret = True
#   else:
#     ftp_mt = ftp.sendcmd("MDTM "+f)
#     ftp_mt = int(datetime.strptime(ftp_mt[4:], "%Y%m%d%H%M%S").strftime("%s"))
#     loc_mt = int(os.path.getmtime(f))
#     if ftp_mt > loc_mt: 
#       grab_file(ftp, f)
#       ret = True
#     else:
#       ret = False
#   return ret
# 
# 
# def cwd_ftp(ftp,type, year):
#   if type == "aid": 
#     type = "aid_public"
#   try:
#     ftp.cwd("archive/"+str(year) )
#   except:
#     ftp.cwd(type)
#   return ftp
# 
# 


class ftp_connect():
    def __init__(self):
        print('opening ftp')
        self.open_connection()
        self.retries = 0
        self.local_parent = os.getcwd()+"/"
    
    def open_connection(self):
        self.ftp = ftplib.FTP("ftp.nhc.noaa.gov")
        self.ftp.login("anonymous","abrammer@albany.edu")
    
    def check_connection(self):
        try:
            ret = self.ftp.voidcmd("NOOP")
        except:
            pprint("Reopening ftp")
            self.open_connection()
    
    def change_dir(self):
        self.check_connection()
        self.ftp.cwd( self.remote_cwd() )
        os.makedirs( self.local_cwd(), exist_ok = True)
        os.chdir(    self.local_cwd() )
    
    def remote_cwd(self):
        if(self.year == datetime.today().year):
            type = self.type
            if type == "aid": 
                type = "aid_public"
            return "/atcf/"+type
        else:
            return "/atcf/"+"archive/{year}".format(year=self.year)
          
    def local_cwd(self):
        return self.local_parent+self.type

    def list_remote_files(self):
        self.change_dir()
        type = self.type
        if type=='fst':
            fsearch = "*{year}*.fst".format(year=self.year)
        else:
            fsearch = "{type}*{year}*".format(type=type[0], year=self.year)
        try:
            f_files = self.ftp.nlst(fsearch)
        except ftplib.error_temp:
            f_files = None
        return f_files
        
    def download_file(self, f):
        self.change_dir()
        try:
            self.ftp.retrbinary("RETR "+f, open(f,"wb").write)
            resp = self.ftp.sendcmd("MDTM "+f)
            timestamp = _time.mktime(datetime.strptime(resp[4:18],"%Y%m%d%H%M%S").timetuple())
            os.utime(f, (timestamp, timestamp))  # set a/m time to match server time
            self.retries = 0
            return True
        except Exception:
            _time.sleep(5)
            self.retries += 1
            return False
    
    def is_remote_file_newer(self, f):
        self.change_dir()
        if not os.path.exists( f ):
            return True
        if os.path.getsize( f ) < 10000:
            return True
        ftp_mt = self.ftp.sendcmd("MDTM "+f )
        ftp_mt = int(datetime.strptime(ftp_mt[4:], "%Y%m%d%H%M%S").strftime("%s"))
        loc_mt = int(os.path.getmtime( f ))
        return ftp_mt > loc_mt

