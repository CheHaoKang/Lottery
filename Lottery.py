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
    
    def send_email(self, email_content):
        import smtplib

        config = self.load_config('email')

        gmail_user = config['gmail_user']
        gmail_password = config['gmail_password']

        sent_from = gmail_user
        sent_to = config['sent_to']
        subject = 'BingoBingo Daily Statistics'

        email_text = 'Subject: {}\n\n{}'.format(subject, email_content)

        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(sent_from, sent_to, email_text)
            server.close()

            print('Email sent')
        except:
            import traceback
            traceback.print_exc()

    def sql_action(self, sql, bind_values=()):
        import pymysql.cursors
        import re
        
        action = re.sub(' .*$', '', sql).lower()

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
