import colorlog
import logging

# 创建一个日志处理器
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# 定义颜色格式器
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white'
    },
    secondary_log_colors={},
    style='%'
)

handler.setFormatter(formatter)

# 获取根日志器并添加处理器
log = colorlog.getLogger()
if not log.handlers:
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
if __name__ == "__main__":
    # 测试不同级别的日志
    log.debug("这是一条 DEBUG 级别的日志")
    log.info("这是一条 INFO 级别的日志")
    log.warning("这是一条 WARNING 级别的日志")
    log.error("这是一条 ERROR 级别的日志")
    log.critical("这是一条 CRITICAL 级别的日志")
