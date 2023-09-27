from fabric import Connection


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