class Lottery:
    def __init__(self):
        self.firstname = 111

    def load_config(self, type):
        import json

        file_object  = open('cred.json', 'r')
        ret = json.loads(file_object.read())[type]
        file_object.close()

        return ret

    def change_date_format(self, original_format, modified_format, date):
        import datetime
        return datetime.datetime.strptime(date, original_format).strftime(modified_format)

    def dict_to_html(self, lottery_data):
        # import pandas as pd
        import HTML
        
        header = [ '' ]
        count = [ 'counts' ]
        for pair in lottery_data:
            header.append(pair[0])
            count.append(pair[1])
        
        table_data = [ header, count ]
        htmlcode = HTML.table(
            table_data,
            # header_row=header,
            # col_width=[],
            # col_align=[ 'left', 'center', 'right', 'char' ],
            col_styles=[ 'font-size: large' for i in range(len(count)) ]
        )
        
        # df = pd.DataFrame(data=lottery_dict)
        # df = df.fillna(' ').T
        
        return htmlcode
    
    def send_email(self, email_content):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        config = self.load_config('email')

        gmail_user = config['gmail_user']
        gmail_password = config['gmail_password']

        sent_from = gmail_user
        sent_to = config['sent_to']
        # subject = 'BingoBingo Daily Statistics'
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'BingoBingo Daily Statistics'
        msg['From'] = gmail_user
        msg['To'] = ', '.join(sent_to)
        
        # email_text = 'Subject: {}\n\n{}'.format(subject, email_content)
        
        # text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"
#         html = """\
# <html>
#   <head></head>
#   <body>
#     <p>Hi!<br>
#        How are you?<br>
#        Here is the <a href="http://www.python.org">link</a> you wanted.
#     </p>
#   </body>
# </html>
# """
        # part1 = MIMEText(text, 'plain')
        part2 = MIMEText(email_content, 'html')
        # msg.attach(part1)
        msg.attach(part2)
        
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(sent_from, sent_to, msg.as_string())
            server.close()

            print('Email sent')
        except:
            import traceback
            traceback.print_exc()

    def sql_action(self, sql, bind_values=()):
        import pymysql.cursors
        import re
        
        action = re.sub(' .*$', '', sql).lower()
        
        # print(sql)
        # print(bind_values)

        config = self.load_config('database')
        trial_max = 5
        while trial_max > 0:
            try:
                conn = pymysql.connect(host=config['host'], port=config['port'], user=config['user'], passwd=config['passwd'], db=config['db'], charset="utf8")
                cur = conn.cursor()

                if action == 'insert':
                    cur.executemany(sql, bind_values)
                elif action == 'select':
                    cur.execute(sql, bind_values)
                    results = cur.fetchall()

                cur.close()
                conn.commit()
                conn.close()
                break
            except:
                import traceback
                traceback.print_exc()
                cur.close()
                conn.close()

                trial_max -= 1
        
        if 'results' in locals():
            return results
        elif trial_max > 0:
            return 1
        else:
            return 0
