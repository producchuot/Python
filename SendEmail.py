from http.server import HTTPServer, BaseHTTPRequestHandler      
import cgi                  
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


file_dir = "D:\BTL"      #D:\
host = 'localhost'          
port = 8080                 


def create_email_message(from_address, to_address, subject, msg_body, files=None, html=None):
    msg = MIMEMultipart()      
    msg['From'] = from_address          
    msg['To'] = ",".join(to_address)    
    msg['Subject'] = subject
    msg.attach(MIMEText(msg_body, 'plain'))         
    if html is not None:
        msg.attach(MIMEText(html, 'html'))
    if files is not None:
        for file in files:
            try:
                attachment = open(file, 'rb')
                part = MIMEBase('application', 'octet-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                file_name_sended = file.split("\\")[-1]
                part.add_header('Content-Disposition', "attachment; filename= " + file_name_sended)
                msg.attach(part)
            except Exception as ex:
                print("could not attache file")
                print(ex)
    return msg


def handler_send_mail(self, form, lst_email, msg):
    try:
        with smtplib.SMTP('smtp.gmail.com', port=587) as smtp_server:
            smtp_server.ehlo()
            smtp_server.starttls()
            smtp_server.login(str(form['Email'].value), str(form['Password'].value))
            smtp_server.sendmail(str(form['Email'].value), lst_email, msg.as_string())
        print('send mail Success !!')
        self.path = '/sendss.html'
        file_to_open = open(self.path[1:]).read()
        self.send_response(200)
        self.wfile.write(bytes(file_to_open, 'utf-8'))
    except Exception as e:
        print(e)
        self.path = '/sendfs.html'
        file_to_open = open(self.path[1:]).read()
        self.send_response(200)
        self.wfile.write(bytes(file_to_open, 'utf-8'))
        er = "<h3 style=text-align:center;color:red;"">Error : %s</h3>" % str(e)
        self.wfile.write(bytes(er, "UTF-8"))
        print('send mail Fail !')


def send_multiple_files(fileitem, lst_file_name):
    fn = os.path.basename(fileitem.filename)
    if fileitem.filename:
        open(file_dir + fn, 'wb').write(fileitem.file.read())
        lst_file_name.append(file_dir + fn)
        print(" ONE - FILE " + fn + " upload success !\n")
    else:
        print("upload fail file "+fn+" !\n")


class Serv(BaseHTTPRequestHandler):

    def do_GET(self):           
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
            print("exception !!")
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

    def do_POST(self):      
        if self.path == '/index.html':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST',
                         'CONTENT_TYPE': self.headers['Content-Type']}
            )

            self.send_response(200)
            self.end_headers()

        lst_email = str(form['sendto'].value).split(",")      

        fileitem = form['filename']
        lst_file_name = []
        if str(fileitem) != "FieldStorage('filename', '', b'')":
            print("khac rong")
            if str(type(fileitem)) == "<class 'cgi.FieldStorage'>":
                print("1 value !")
                send_multiple_files(fileitem, lst_file_name)
            else:
                print("nhieu gia tri")
                for file in fileitem:
                    send_multiple_files(file, lst_file_name)
                for s in lst_file_name:
                    print("url : " + s)
        else:
            print("rong")

        msg = create_email_message(
            from_address=str(form['Email'].value),
            to_address=lst_email,
            subject=str(form['Subject'].value),
            msg_body=str(form['message'].value),
            files=lst_file_name
        )

        print(lst_email)
        handler_send_mail(self, form, lst_email, msg)
        return


httpd = HTTPServer((host, port), Serv)
httpd.serve_forever()
