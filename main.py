#!/usr/bin/env python3.4
import socket
from functools import wraps
from concurrent import futures
import time
from ftplib import FTP
import re

def ftp_connector(ip):
    ftp = FTP(ip)
    ftp.login()
    return ftp.retrlines('LIST')

def clocker(wr_func):
    time_srt = "time.strftime('[%H:%M:%S]')"
    pattern = re.compile(r'\d+.\d+.\d+')
    @wraps(wr_func)
    def wrapping(*args,**kwargs):
        if wr_func.__name__ == scaner.__name__:
            print('{time_now} :: {func_name} started at network {net}'.format(time_now=eval(time_srt),
                                                                func_name=wr_func.__name__,
                                                                net=pattern.findall(args[0][0])[0]+'.0'))
        else:
            print('{time_now} :: {func_name} started'.format(time_now=eval(time_srt),
                func_name=wr_func.__name__))
        start = time.time()
        setattr(clocker, 'start', start)
        data = wr_func(*args,**kwargs)
        end = time.time() - start
        print('{time_now} :: {func_name} ended with result {result} at {sec:.2f} secs.'.format(time_now=eval(time_srt),
                func_name=wr_func.__name__,
                result = data,
                sec = end))
        return data
    return wrapping

@clocker
def connection_test(host):
    port = 21
    sock = socket.socket()
    sock.settimeout(1)
    try:
        sock.connect((host,port))
    except socket.timeout:
        return None
    except OSError:
        pass
    if sock:
        return host
    else:
        return None



@clocker
def scaner(ip_list):
    with futures.ThreadPoolExecutor(100) as runner:
        to_do = []
        for ip in (ip_list):
            future = runner.submit(connection_test, ip)
            to_do.append(future)
        results = []
        for future in futures.as_completed(to_do):
            if future.result():
                result = future.result()
                print("""
                Online ftp on {res}
                at {time_s:.2f} sec of working {func_name} func.
                """.format(res=result, time_s=time.time()-clocker.start, func_name=scaner.__name__))
                print(ftp_connector(result))
                results.append(result)
    return results

if __name__ == '__main__':
    IPs = ['213.180.204.' + str(x) for x in range(1, 256)]
    print(scaner(IPs))
