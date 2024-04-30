import urllib.request
import re
from sugar import *
from datetime import datetime

year = datetime.now().year


@timer
def get_html(url):
    # 发送HTTP请求获取页面内容
    response = urllib.request.urlopen(url)
    html_content_1 = response.read().decode('utf-8')
    return html_content_1


def handle_weather(html_content_2):
    date = r' 7天天气预报（(.*?)发布）(.*?)<table class="hour-table" id="hourTable_0" style="">'
    matches = re.findall(date, html_content_2, re.DOTALL)

    date1 = (r'星期(.*?)\n         <br>(.*?)\n        </div> \n        <div class="day-item dayicon">\n         (.*?)\n '
             r'       </div> \n        <div class="day-item">\n         (.*?)\n        </div> \n        <div '
             r'class="day-item">\n         (.*?)\n        </div> \n        <div class="day-item">\n         (.*?)\n  '
             r'      </div> \n        <div class="day-item bardiv">\n         (.*?)\n          <div class="high">\n  '
             r'         (.*?)\n          </div>\n          <div class="low">\n           (.*?)\n          </div>\n   '
             r'      </div>\n        </div> \n        <div class="day-item nighticon">\n         (.*?)\n        '
             r'</div> \n        <div class="day-item">\n         (.*?)\n        </div> \n        <div '
             r'class="day-item">\n         (.*?)\n        </div> \n        <div class="day-item">\n         (.*?)\n  '
             r'      </div> \n       </div> \n')
    matches1 = re.findall(date1, str(matches[0][1]), re.DOTALL)
    return matches1


def process_weather_data(matches1):
    weather_info = "天气如下：\n"  # 初始化一个空字符串用于累加天气信息

    for match in matches1:
        day = match[0]
        date_1 = match[1]
        weather_1 = match[3]
        wind = match[4]
        wave = match[5]
        high_temp = match[7]
        low_temp = match[8]
        unknown = match[11]
        wave_speed = match[12]

        # 将每天的天气信息添加到字符串中，每天的信息后加上换行符
        weather_info += f"日期：{year}/{date_1}  星期{day}  {weather_1} {wind}{wave}     温度：{low_temp}~{high_temp} {unknown}{wave_speed}\n"

    return weather_info  # 返回累加后的天气信息字符串


def get__weather():
    url = 'https://weather.cma.cn/web/weather/59948.html'
    html_content = get_html(url)
    weather_out = handle_weather(html_content)
    weather_print = process_weather_data(weather_out)
    return weather_print


if __name__ == '__main__':
    weather = get__weather()
    print(weather)
