import json
import sys

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fpdf import FPDF

from admin_panel.models import Emails, MailQueues, MailAttachments
from meeting.models import MeetingHD
from reports.models import ReportForms, ReportLegend, LegendSubs, DepartmentReportMailQue
from taskmanager.models import Tasks


@csrf_exempt
def interface(request):
    response = {
        'status_code': 0,
        'message': ""
    }

    success_response = {
        'status_code': 200,
        'message': "Procedure Completed Successfully"
    }

    # get method
    method = request.method

    try:

        body = json.loads(request.body)
        module = body.get('module')
        data = body.get('data')
        doc = data.get('doc')
        key = data.get('key')
        output = data.get('output')
        header = {}
        transactions = []

        if doc == 'TSK' and output == 'PDF':
            import re
            clean = re.compile('<.*?>')
            head = Tasks.objects.get(uni=key)
            pdf = FPDF('P', 'mm', 'A4')
            pdf.add_page()

            pdf.set_font('Arial', 'B', 16)
            pdf.cell(200, 5, head.title, 0, 1)
            pdf.ln(5)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, f"{re.sub(clean, '', head.description)}", 0, 'L')

            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(200, 5, 'TRANSACTIONS', 0, 1)
            pdf.ln(2)

            t_count = 1
            for tran in head.transaction():
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(200, 5, f'{t_count}. {tran.title}', 0, 1)
                pdf.set_font('Arial', '', 10)
                pdf.cell(200, 5, f"By {tran.owner.username} On {tran.created_date} {tran.created_time}", 0, 1)
                pdf.ln(1)
                pdf.multi_cell(0, 5, f"{re.sub(clean, '', tran.description)}", 0, 'L')
                pdf.ln(2)
                t_count += 1

            fil_name = f"static/general/tmp/test.pdf"
            pdf.output(fil_name, 'F')

            success_response['message'] = fil_name
            response = success_response

        elif doc == 'SAVE_FORM':
            ReportForms(key=key, code=output, description=key).save()

            success_response['message'] = "Form Saved"
            response = success_response

        elif doc == 'SAVE_REPORT_LEGEND':
            ReportLegend(name=key, description=output).save()

            success_response['message'] = "Legend Saved"
            response = success_response

        elif doc == 'SAVE_REPORT_LEGEND_SUB':
            description = data.get('description')
            action = data.get('action')
            legend = data.get('legend')
            name = data.get('name')

            lg = ReportLegend.objects.get(pk=legend)

            LegendSubs(legend=lg, description=description, action=action, name=name).save()

            success_response['message'] = "Legend Saved"
            response = success_response

        elif doc == 'send_dept_mail':

            pending_mail_list = DepartmentReportMailQue.objects.filter(status=0)
            resp = []
            deptt = []
            if pending_mail_list.count() > 0:
                for mails in pending_mail_list:
                    head_email = mails.department.email_of_head
                    files = mails.files
                    clean_files = files.rstrip(',')
                    files_array = clean_files.split(',')

                    import smtplib
                    from email.mime.multipart import MIMEMultipart
                    from email.mime.text import MIMEText
                    from email.mime.application import MIMEApplication
                    # Email configuration
                    smtp_server = "smtp.gmail.com"
                    smtp_port = 587
                    sender_email = "donotreply@protonghana.com"
                    sender_password = "arbogirmfctrnnpt"  # Use an app password for security
                    subject = f"{mails.department.name} PRODUCTIVITY REPORT "
                    html_content = "Productivity report base on task manager. This report will includes all tasks"

                    # Create a MIME multipart message
                    msg = MIMEMultipart()
                    msg["From"] = sender_email
                    msg["To"] = head_email
                    msg["Subject"] = subject

                    # Attach the HTML content to the message
                    msg.attach(MIMEText(html_content, "html"))
                    files_array = clean_files.split(',')
                    ff = []
                    for att_file in files_array:
                        # Attach the file
                        ff.append(att_file)
                        attachment_filename = f"static/general/task-reports/{att_file}"
                        attachment_path = attachment_filename
                        try:
                            with open(attachment_path, 'rb') as attachment:
                                part = MIMEApplication(attachment.read())
                                part.add_header('Content-Disposition', 'attachment', filename=att_file.strip())
                                msg.attach(part)
                                print(attachment_filename)
                        except FileNotFoundError:
                            print(f"File not found: {attachment_filename}")
                        except Exception as e:
                            print(f"Error attaching file {attachment_filename}: {str(e)}")

                            # Connect to the Gmail SMTP server and send the email
                    try:
                        server = smtplib.SMTP(smtp_server, smtp_port)
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, head_email, msg.as_string())
                        deptt.append({'department':mails.department.name,'files':ff})
                        mails.status = 1
                        mails.save()

                    except Exception as e:
                        # response['status_code'] = 505
                        # response['message'] = str(e)
                        deptt.append({'department':mails.department.name,'files':e})
                        message = f"COULD NOT SEND EMAIL {str(e)}"
                        print("Error sending email:", e)
                    finally:
                        server.quit()

                success_response['message'] = deptt
                response = success_response
            else:
                success_response['message'] = "No Emails To Send For Department"
                response = success_response

        elif doc == 'mail_sync':
            pending_mails = Emails.objects.filter(status=0)
            c = 0
            for email in pending_mails:
                recipient = email.sent_to
                subject = email.subject
                sent_from = email.sent_from
                body = email.body
                this_email = Emails.objects.filter(pk=email.pk)
                email_type = email.email_type
                email_ref = email.ref
                attacs = email.attachments
                cc = email.send_cc()

                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from email.mime.application import MIMEApplication

                # Email configuration
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                sender_email = "donotreply@protonghana.com"
                sender_password = "arbogirmfctrnnpt"  # Use an app password for security
                html_content = body

                # Create a MIME multipart message
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = recipient
                msg["Subject"] = subject
                msg['Cc'] = email.cc

                # Attach the HTML content to the message
                msg.attach(MIMEText(html_content, "html"))
                files_array = attacs.split(',')
                ff = []

                for att_file in files_array:
                    # Attach the file
                    ff.append(att_file)
                    attachment_filename = f"static/general/crm-logs-reports/{att_file}"
                    attachment_path = attachment_filename
                    try:
                        with open(attachment_path, 'rb') as attachment:
                            part = MIMEApplication(attachment.read())
                            part.add_header('Content-Disposition', 'attachment', filename=att_file.strip())
                            msg.attach(part)
                            print(att_file)
                    except FileNotFoundError:
                        print(f"File not found: {attachment_filename}")
                    except Exception as e:
                        print(f"Error attaching file {attachment_filename}: {str(e)}")

                        # Connect to the Gmail SMTP server and send the email
                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, recipient, msg.as_string())

                    email.status = 1
                    email.save()

                except Exception as e:
                    # response['status_code'] = 505
                    # response['message'] = str(e)

                    message = f"COULD NOT SEND EMAIL {str(e)}"
                    print("Error sending email:", e)
                finally:
                    server.quit()

                c += 1
            success_response['message'] = f"{c} EMAILS SENT"
            response = success_response

        elif doc == 'mail_sync_v2':
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.application import MIMEApplication

            mails = MailQueues.objects.filter(is_sent=False)

            for mail in mails:
                sender = mail.sender
                recipient = mail.recipient
                subject = mail.subject
                body = mail.body
                cc = mail.cc

                smtp_server = sender.host
                smtp_port = sender.port
                sender_email = sender.address
                sender_password = sender.password
                html_content = body

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient
                msg['Subject'] = subject
                msg['Cc'] = cc

                to_address = [recipient] + cc.split(',') if cc else [recipient]

                # attachments
                msg.attach(MIMEText(html_content, 'html'))
                attachments = MailAttachments.objects.filter(mail=mail)
                print(attachments.count)
                for attachment in attachments:
                    attachment_filename = attachment.attachment.path
                    file_name = attachment_filename.split('/')[-1]
                    try:
                        with open(attachment_filename, 'rb') as attached:
                            part = MIMEApplication(attached)
                            part.add_header('Content-Disposition', 'attachment',filename=file_name)
                            msg.attach(part)
                    except FileNotFoundError:
                        print(f"File not found: {attachment_filename}")
                    except Exception as e:
                        print(f"Error attaching file {attachment_filename}: {str(e)}")

                # send email

                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, to_address, msg.as_string())

                    mail.is_sent = 1
                    mail.sent_response = "Email Sent"
                    mail.save()
                    server.quit()
                    response['message'] = "Email Sent"
                except Exception as e:
                    # response['status_code'] = 505
                    # response['message'] = str(e)
                    mail.sent_response = f"Could Not Send {e}"
                    mail.save()

                    message = f"COULD NOT SEND EMAIL {str(e)}"
                    response['message'] = message
                success_response['message'] = f"{mails.count()} Sent"
                response = success_response


    except Exception as e:
        error_type, error_instance, traceback = sys.exc_info()
        tb_path = traceback.tb_frame.f_code.co_filename
        line_number = traceback.tb_lineno
        response["status_code"] = 500
        response[
            "message"] = f"An error of type {error_type} occurred on line {line_number} in file {tb_path}. Details: {e}"

    return JsonResponse(response)
