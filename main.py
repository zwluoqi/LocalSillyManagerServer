from flask import Flask, request, jsonify, make_response, Response, stream_with_context,render_template_string
import asyncio
import time
import threading
import queue
import logging
import subprocess
import random
import requests

import urllib.request

# 使用ifconfig.me服务获取公网IP地址
url = 'http://ifconfig.me'
ip_address = ''
# 发送请求并读取响应
with urllib.request.urlopen(url) as response:
    ip_address = response.read().decode('utf-8')

print(ip_address)

def dump_session():
    try:
        subprocess.run(["/root/silly/dumpSession.sh"], check=True)
    except Exception as e:
        print( e )
    print( "dump_session executed" )

async def worker_once():
  while True:
    await asyncio.sleep(random.randint(1,60))
    dump_session()
    await asyncio.sleep(random.randint(60,120))

class CustomError(Exception):
  """自定义异常类，携带错误码和错误消息"""

  def __init__(self, error_code, message="An error occurred"):
    self.error_code = error_code
    self.message = message
    super().__init__(self.message)


# Refactor the creation of the Flask app into a function
def create_app(*args, **kwargs):
  threading.Thread(target=lambda: asyncio.run(worker_once())).start()

  app = Flask(__name__)
  # 设置日志的记录等级
  app.logger.setLevel(logging.DEBUG)

  def handle_502(port):
    try:
        subprocess.run(["/root/silly/start_silly_port.sh",port], check=True)
    except Exception as e:
        print( e )
    print( "Script executed" )
  
  @app.route("/",
             methods=['GET'])
  def root():
    service_name = request.headers.get('X-Service-Name')
    if service_name =='handle_502':
        port = request.headers.get('X-Service-Port')
        print(f"Restarting {service_name} on port {port}")
        try:
          payload = {
            "ip":ip_address,
            "port":port,
          }
          headers = {
              'Content-Type': 'application/json',
          }
          baseurl = 'https://sillydbserver.qingzhu-us.workers.dev'
          response = requests.post(baseurl+'/checksilly',data=payload,headers=headers)
          print('python',response.text)
          valid = response.json()['valid']
          if True:
            handle_502(port)
          else:
            return "服务已到期，请续费后使用"
        except Exception as e:
            print( e )
            handle_502(port)
    # return "正在重启服务，稍后刷新即可"
      # HTML 模板，包含 JavaScript 倒计时
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Processing...</title>
        <script type="text/javascript">
            var countdown = 20;
            var countdownTimer = setInterval(function() {
                if (countdown <= 0) {
                    clearInterval(countdownTimer);
                    window.location.reload();
                } else {
                    document.getElementById('countdown').innerHTML = countdown;
                    countdown--;
                }
            }, 1000);
        </script>
    </head>
    <body>
        <p>Please wait while we process your request. The page will refresh in <span id="countdown">20</span> seconds.</p>
    </body>
    </html>
    '''
    return render_template_string(html_template)
  return app




# Only for local development, not for production
if __name__ == "__main__":
  app = create_app(None, None)
  app.run(host="0.0.0.0", port=5000)

