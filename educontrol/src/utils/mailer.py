from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
import smtplib
import jinja2
from src.settings import settings
from src.utils.logging.logger_factory import get_logger

logger = get_logger()


# ! internal use
def send_mail(
    smtp_server,
    smtp_port,
    smtp_user,
    smtp_password,
    send_to,
    subject,
    template_name,
    params,
    files=[],
):
    templatePath = settings.TEMPLATES_PATH
    try:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(templatePath))
    except Exception as e:
        logger.error(f"Error (jinja2.Environment) ---> {str(e)}")
        raise e

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            msg = MIMEMultipart("mixed")
            msg["From"] = smtp_user
            msg["To"] = COMMASPACE.join(send_to)
            msg["Date"] = formatdate(localtime=True)
            msg["Subject"] = subject

            template = env.get_template(template_name)
            html_content = template.render(params)
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            for file in files:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file["file"])
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition", f'attachment; filename="{file["name"]}"'
                )
                msg.attach(part)

            smtp.ehlo()
            smtp.starttls()
            smtp.login(smtp_user, smtp_password)
            smtp.sendmail(smtp_user, send_to, msg.as_string())
            smtp.quit()
    except Exception as e:
        logger.error(f"Error (smtplib.SMTP) ---> {str(e)}")
        raise e


# in external use at least once (gatewayDB.py)
def send_userNotification(
    notificationType: str, user: dict, files=[]
):  # (user: dict of SNAUser object + userName + userEmail)

    templateDict = {
        settings.SUSPENDED_NOTIFICATION: "suspended_user.html",
        settings.ACTIVATED_NOTIFICATION: "activated_user.html",
        settings.DEBT_NOTIFICATION: "debt_status_mssg.html",
        settings.REPORT_NOTIFICATION: "report.html",
    }
    template_str = templateDict[notificationType]

    subjectDict = {
        settings.SUSPENDED_NOTIFICATION: f"Notificación: Suspensión temporal de acceso a la plataforma de enseñanza virtual ({user['lmsName']}).",
        settings.ACTIVATED_NOTIFICATION: f"Notificación: Activación del acceso a la plataforma de enseñanza virtual ({user['lmsName']}).",
        settings.DEBT_NOTIFICATION: "Notificación: Estado de valores pendientes.",
        settings.REPORT_NOTIFICATION: "Notificación: Reporte diario de deudas.",
    }
    mssg_subject = subjectDict[notificationType]

    params = {}
    params["userName"] = user["userName"]
    if notificationType == "DEBT_NOTIFICATION":
        params["userDebt"] = user["userDebt"]
    elif notificationType == "REPORT_NOTIFICATION":
        params["fecha"] = datetime.now().strftime("%d/%m/%Y-%H:%M")

    send_mail(
        settings.SMTP_SERVER,
        settings.SMTP_PORT,
        settings.SMTP_USER,
        settings.SMTP_PASSWORD,
        [user["userEmail"]],
        mssg_subject,
        template_str,
        params,
        files,
    )
