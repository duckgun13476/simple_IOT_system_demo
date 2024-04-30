import base64
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dashboard.variables.variable import Var

smtp_server_set = Var.smtp_server
smtp_port_set = Var.smtp_port
smtp_sender_mail_set = Var.smtp_sender_email
smtp_secret_set = Var.smtp_password


def send_email(subject, body, send_email, title="智能仪表终端"):
    # 邮件内容
    # title="智能仪表终端"
    utf8_bytes = title.encode('utf-8')
    base64_encoded = base64.b64encode(utf8_bytes).decode('utf-8')
    final_nickname = f'=?utf-8?b?{base64_encoded}?='
    # 构建邮件
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = final_nickname + ' <1907284584@qq.com>'
    msg['To'] = send_email

    # 发送邮件
    smtp_server = smtp_server_set
    smtp_port = smtp_port_set
    sender_email = smtp_sender_mail_set
    password = smtp_secret_set  # 在QQ邮箱设置里拿到的码

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, [msg['To']], msg.as_string())
        print('邮件发送成功')
    except smtplib.SMTPException as e:
        print('邮件发送失败:', str(e))


if __name__ == "__main__":
    subject = '[来自智能检测终端V1.1]'
    body = '这是一封测试邮件'
    send_email(subject, body, send_email='2980168906@qq.com')
