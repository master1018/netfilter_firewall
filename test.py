from fabric import Connection

conn = Connection(
    host='192.168.247.139',
    user='yhr',
    port=22,
    connect_kwargs={
        "password": 'qwert12345'
    },
)

result = conn.run('/home/yhr/RJFireWall/uapp rule default accept')
# 打印输出结果
print(result.stdout)