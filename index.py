# coding=utf-8
#!/usr/bin/env python
import io
import os
import re
import sys
import json
import subprocess
import requests
import ipaddress
import hmac
from hashlib import sha1
from flask import Flask, request, abort

"""
Conditionally import ProxyFix from werkzeug if the USE_PROXYFIX environment
variable is set to true.  If you intend to import this as a module in your own
code, use os.environ to set the environment variable before importing this as a
module.

.. code:: python

    os.environ['USE_PROXYFIX'] = 'true'
    import flask-github-webhook-handler.index as handler

"""
if os.environ.get('USE_PROXYFIX', None) == 'true':
    from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.debug = os.environ.get('DEBUG') == 'true'

# The repos.json file should be readable by the user running the Flask app,
# and the absolute path should be given by this environment variable.

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return 'OK123123123'
    elif request.method == 'POST':
        request_ip = ipaddress.ip_address(u'{0}'.format(request.remote_addr))

        print (request.headers.get('X-Gitlab-Event'))

        if request.headers.get('X-Gitlab-Event') == "ping":
            return json.dumps({'msg': 'Hi!'})
        if request.headers.get('X-Gitlab-Event') == "Push Hook":
            return json.dumps({'msg': 'Hi!'})
        elif request.headers.get('X-Gitlab-Event') == "Merge Request Hook":
            payload = json.loads(request.data)
            # 获取每个部分的内容
            # print("hello")
            project_name = payload["repository"]["name"]
            mr_title = payload["object_attributes"]["title"]
            assignee = payload["assignee"]["name"]
            requester = payload["user"]["name"]
            target_branch = payload["object_attributes"]["target_branch"]
            source_branch = payload["object_attributes"]["source_branch"]
            create_time = payload["object_attributes"]["created_at"]
            update_time = payload["object_attributes"]["updated_at"]
            request_state = payload["object_attributes"]["state"]
            request_url = payload["object_attributes"]["url"]

            if target_branch != "master":
                print("Not Master Event")
                return json.dumps({'msg': "Branch Filtered"})

            if request_state == "merged":
                params = {
                    "msgtype" : "markdown",
                    "agentid" : 1,
                    "markdown" : {
                        "content" : u"项目 `"+project_name+u"` 已有新 `Merge` 合并 \n"
                        u"> 标题: `" + mr_title +u"`\n"
                        u"> 状态: `" + request_state + u"`\n"
                        u"> 执行人: `" + requester +u"`\n"
                        u"> 目标分支: `" + target_branch +u"`\n"
                        u"> 源分支: " + source_branch +u"\n"
                        u"> 创建时间: " + create_time +u"\n"
                        u"> 更新时间: " + update_time +u"\n"
                        u"> [点击查看详情]("+request_url+u")\n"
                    },
                    "safe":0
                }
            elif create_time == update_time:
                params = {
                "msgtype" : "markdown",
                "agentid" : 1,
                "markdown" : {
                    "content" : u"项目 `"+project_name+u"` 收到 `Merge` 请求 \n"
                    u"> 标题: `" + mr_title +u"`\n"
                    u"> 状态: `" + request_state + u"`\n"
                    u"> 指定执行人: `" + assignee +u"`\n"
                    u"> MR申请人: " + requester +u"\n"
                    u"> 目标分支: `" + target_branch +u"`\n"
                    u"> 源分支: " + source_branch +u"\n"
                    u"> 创建时间: " + create_time +u"\n"
                    u"> 更新时间: " + update_time +u"\n"
                    u"> [点击查看详情]("+request_url+u")\n"
                },
                "safe":0
            }
            else:
                print("Merge Update Event")
                return json.dumps({'msg': "Time Filtered"})
            # Robot 测试群
            # response = requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=cd35d8df-8820-4b23-2adf-96c04049ebb5", data=json.dumps(params))
            # 正式项目群
            response = requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=476e1e00-be43-44f8-25f3-48d33178f3c5", data=json.dumps(params))
            print(response)
        else:
            return json.dumps({'msg': "wrong event type"})
        return 'OK'

# Check if python version is less than 2.7.7
if sys.version_info < (2, 7, 7):
    # http://blog.turret.io/hmac-in-go-python-ruby-php-and-nodejs/
    def compare_digest(a, b):
        """
        ** From Django source **

        Run a constant time comparison against two strings

        Returns true if a and b are equal.

        a and b must both be the same length, or False is
        returned immediately
        """
        if len(a) != len(b):
            return False

        result = 0
        for ch_a, ch_b in zip(a, b):
            result |= ord(ch_a) ^ ord(ch_b)
        return result == 0
else:
    compare_digest = hmac.compare_digest

if __name__ == "__main__":
    try:
        port_number = int(sys.argv[1])
    except:
        port_number = 80
    if os.environ.get('USE_PROXYFIX', None) == 'true':
        app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', port=port_number)
