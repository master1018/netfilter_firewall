from fabric import Connection
import json
import os
import paramiko  # 用于调用scp命令
from scp import SCPClient
 
 
def upload_img(host, port, user, passwd, remote_path, local_path):
 
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(host, port, user, passwd)
    scpclient = SCPClient(ssh_client.get_transport(),socket_timeout=15.0)

    try:
        scpclient.put(local_path, remote_path)
    except FileNotFoundError as e:
        print(e)
        print("系统找不到指定文件" + local_path)
    else:
        print("文件上传成功")
    ssh_client.close()


def connect_firewall(host, user, port, passwd):
    return Connection(
        host=host,
        user=user,
        port=port,
        connect_kwargs={
            "password": passwd
        },
    )

def check_connect(host, user, port, passwd):
    conn = connect_firewall(host, user, port, passwd)
    res = conn.run("whoami")
    if user in res.stdout:
        return 1
    else:
        return 0

def set_default_mode(mode, host, port, user, passwd):
    conn = connect_firewall(host, user, port, passwd)
    res = conn.run("/home/yhr/RJFireWall/uapp rule default " + mode)
    return res.stdout

def quert_rule_list(host, port, user, passwd):
    conn = connect_firewall(host, user, port, passwd)
    res = conn.run("/home/yhr/RJFireWall/uapp rule ls")
    return res.stdout

def remote_run_shell(host, port, user, passwd, shell_path):
    conn = connect_firewall(host, user, port, passwd)
    res = conn.run(shell_path)
    return res.stdout

    
def add_rule_list(host, port, user, passwd):
    rule_list = []
    with open("tmp") as f:
        rule_list = json.load(f)
    for rule in rule_list:
        # write rule in cache
        f = open("cache_input", "w")
        print(1, file=f)
        print(rule['index'], file=f)
        print(rule['src ip'], file=f)
        if rule['src port'] != 'any':
            print(rule['src port'] + '-' + rule['src port'], file=f)
        else:
            print('any', file=f)
        print(rule['dst ip'], file=f)
        if rule['dst port'] != 'any':
            print(rule['dst port'] + '-' + rule['dst port'], file=f)
        else:
            print('any', file=f)
        print(rule['protocol'], file=f)
        if rule['action'] == 'accept':
            print(1, file=f)
        else:
            print(0, file=f)
        print(rule['log'], file=f)
        f.close()
        upload_img(host, port, user, passwd, "/home/yhr/RJFireWall/", "cache_input")
        remote_run_shell(host, port, user, passwd, "/home/yhr/RJFireWall/run.sh")

def del_rule_list(host, port, user, passwd, index):
    conn = connect_firewall(host, user, port, passwd)
    res = conn.run("/home/yhr/RJFireWall/uapp rule del " + str(index))
    return res.stdout

def query_log(host, port, user, passwd):
    conn = connect_firewall(host, user, port, passwd)
    res = conn.run("/home/yhr/RJFireWall/uapp ls log")
    return res.stdout

def query_nat_list(host, port, user, passwd):
    conn = connect_firewall(host, user, port, passwd)
    res = conn.run("/home/yhr/RJFireWall/uapp ls nat")
    return res.stdout

def add_nat_list(host, port, user, passwd):
    nat_list = []
    with open("tmp") as f:
        nat_list = json.load(f)
    for nat in nat_list:
        # write rule in cache
        f = open("cache_input", "w")
        print(nat['src ip'], file=f)
        print(nat['nat ip'], file=f)
        if "any" not in nat['nat port']:
            print(nat['nat port'] + "-" + nat['nat port'] , file=f)
        else:
            print('any', file=f)
        f.close()
        upload_img(host, port, user, passwd, "/home/yhr/RJFireWall/", "cache_input")
        remote_run_shell(host, port, user, passwd, "/home/yhr/RJFireWall/run2.sh")

def del_nat_list(host, port, user, passwd, index):
    conn = connect_firewall(host, user, port, passwd)
    print(index)
    res = conn.run("/home/yhr/RJFireWall/uapp nat del " + str(index))
    return res.stdout

def query_connect_record(host, port, user, passwd):
    conn = connect_firewall(host, user, port, passwd)
    res = conn.run("/home/yhr/RJFireWall/uapp ls connect")
    return res.stdout