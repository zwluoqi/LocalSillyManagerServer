from flask import Flask, request, jsonify, make_response, Response, stream_with_context
import asyncio
import time
import threading
import queue
import logging
import subprocess


class CustomError(Exception):
  """自定义异常类，携带错误码和错误消息"""

  def __init__(self, error_code, message="An error occurred"):
    self.error_code = error_code
    self.message = message
    super().__init__(self.message)


# Refactor the creation of the Flask app into a function
def create_app(*args, **kwargs):

  app = Flask(__name__)
  # 设置日志的记录等级
  app.logger.setLevel(logging.DEBUG)

  @app.route("/")
  def root():
    return jsonify(message="Claude2WebProxy")
  
  @app.route("/script_trigger_url/<port>",
             methods=['GET'])
  def script_trigger_url(port):
    # 执行shell命令
    subprocess.run(["/root/silly/start_silly_port.sh",port], check=True)
    return "Script executed"
  
  return app


# Only for local development, not for production
if __name__ == "__main__":
  app = create_app(None, None)
  app.run(host="0.0.0.0", port=5000)

