import requests
from bs4 import BeautifulSoup as bs
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv

USERNAME = 'XXXX@XXXXX.com'
PASSWORD = 'XXXXXX'


class WebrootPartnerCart(object):
    def __init__(self):
        self.base_url = 'https://partnercart.webroot.com'
        self.session = requests.session()

    def login(self, username, password):
        self.username = username
        self.password = password
        url = self.base_url + '/login'
        s = self.session
        data = s.get(url).text
        token = [i for i in data.split('name="security[token]"')][1].split('" />')[0][8:]
        url = 'https://partnercart.webroot.com/sessions'
        s.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        params = {}
        params['username'] = self.username
        params['password'] = self.password
        params['security[token]'] = token
        resp = s.post(url, data=params)
        return resp

    def get_recent_orders(self):
        url = 'https://partnercart.webroot.com/'
        s = self.session
        data = s.get(url).text
        soup = bs(data, "html.parser")
        recent_table = soup.find(id='recent-orders')
        table_values = recent_table.find_all('a')
        urls = [self.base_url + i['href'] for i in table_values if 'orders' in i['href']]
        return urls

    def get_keycode_from_order_url(self, order_url):
        s = self.session
        data = s.get(order_url).text
        soup = bs(data, "html.parser")
        order_table = soup.find(id='order-summary')
        order_values = order_table.find_all('a')
        keycodes = list(set([i.text for i in order_values]))
        return keycodes


    def send_email(self, keycodes, newkeycodes):
        if not newkeycodes:
            newkeycodes = "No New Keycodes"
        fromaddr = "xxx@xxxxxx.com"
        toaddr = ["xxx@xxxxxx.com", "xx@xxx.com"]
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = "  ,".join(toaddr)
        msg['Subject'] = "Webroot Keycodes"
        body = 'New Webroot Keycodes: \n' + str(newkeycodes) + '\n\n Recent Webroot Keycodes: \n' + str(keycodes)
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('outbound.address.com', 25)
        server.ehlo()
        server.starttls()
        server.ehlo()
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        print('email sent')



def main():
    w = WebrootPartnerCart()
    w.login(USERNAME, PASSWORD)
    urls = w.get_recent_orders()
    keycodes = []
    print("Today's Keycodes:")
    for order_url in urls:
        keycode = w.get_keycode_from_order_url(order_url)
        if len(keycode) > 1:
            keycodes.append('Multiple keycodes found in a single order:', order_url)
            print('Multiple keycodes found in a single order', keycode)
        else:
            keycodes.append(keycode[0])
            print(keycode[0])
    print(keycodes)
    print("Yesterday's Keycodes:")
    yestkeycodes = []
    with open('keycodes.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter="\n")
        for row in reader:
            yestkeycodes.append(row[0])
    print(yestkeycodes)
    print("New Keycodes:")
    newkeycodes = (list((set(keycodes)) - (set(yestkeycodes))))
    for each in newkeycodes:
        print(each)
    if not newkeycodes:
        print("No New Keycodes")
    w.send_email(keycodes, newkeycodes)
    with open('keycodes.csv', mode='w', encoding='utf-8') as f:
        for row in keycodes:
            f.write(row + '\n')
    print('keycodes.csv updated.')


if __name__ == '__main__':
    main()
