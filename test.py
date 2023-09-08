from fabric import Connection

conn = Connection(
    host='192.168.247.139',
    user='yhr',
    port=22,
    connect_kwargs={
        "password": 'qwert12345'
    },
)

result = conn.run('uname -s')
# 打印输出结果
print(result.stdout)