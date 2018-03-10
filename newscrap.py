from bs4 import BeautifulSoup
from requests import Session, packages, get
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

def label(st):
    m = QTextBrowser()
    m.setHtml('<style> div{color: red} p:hover{color: red}</style>'+st)
    m.setOpenExternalLinks(True)
    return m

def pixmap(st):
    label = QLabel()
    label.setPixmap(QPixmap(st))
    label.setScaledContents (True)
    label.setMaximumSize (80, 80)
    return label

def get_name(url: str):
    if url.startswith('./download'):
        place = url.find('avatar')
        return 'avatars/'+url[place+7:]
    else:
        return 'avatars/no_avatar.gif'

def not_exists(file):
    try:
        m = open(file)
        m.close()
        return False
    except FileNotFoundError:
        return True

def remove_text_decoration(string: str):
    place = string.find('<a')
    style = ' style="text-decoration:none; color:black"'
    return string[:place +2] + style + string[place+2:]


app = QApplication([])
widget = QWidget()
widget.setGeometry(QRect(500, 500, 1000, 500))
lay = QVBoxLayout(widget)


NOTIF_URL = 'https://192.168.16.113/ucp.php?i=ucp_notifications'
LOGIN_URL = 'https://192.168.16.113/ucp.php?mode=login'
NEWPOSTS_URL = 'https://192.168.16.113/search.php?search_id=newposts'

packages.urllib3.disable_warnings()

session = Session()
session.verify = False
session.headers = {'User-Agent': 'Mozilla/5.0'}

payloads = {
            'username': 'LuisKrlos',
            'password': 'luisi4cc',
            'login': 'Login',
            'sid': '',
            'redirect': 'index.php'
            }
html = session.post(LOGIN_URL, data=payloads)
notif = session.get(NOTIF_URL)
sopa = BeautifulSoup(notif.text, 'html5lib')

def download_img(url, name: str):
    print('download', name)
    global session
    file = session.get(url, stream=True)
    with open('avatars/'+name, 'wb') as h:
        for i in file.iter_content():
            h.write(i)


for i in sopa.find_all('li', 'row'):
    img = i.find('img')
    src = img.get('data-src')
    if src is None:
        src = img.get ('src')
    srcf = 'https://192.168.16.113' + src[1:]
    direction = get_name(src)
    if not_exists(direction):
        download_img(srcf, direction)

    clas_notif = i.find('div', {'class': 'notifications'})
    te = clas_notif.find('a')
    if te is not None:
        #n = str(te).replace('href="./', 'href="https://192.168.16.113/')
        #n = n.replace('amp;', '')
        #m = n[:3] + 'style="color:black; text-decoration:none" ' + n[3:]
        m = str (clas_notif).replace ('href="./', 'href="https://192.168.16.113/')
    else:
        m = str(clas_notif)
    print(m)

    hori = QHBoxLayout()
    hori.addWidget(pixmap(direction))
    hori.addWidget(label(m))
    lay.addLayout(hori)

def topics():
    for i in sopa.find_all('li', 'row'):
        data = i.find('div', {'class': 'list-inner'})
        name = data.find('a', 'topictitle')
        name = str (name).replace ('href="./', 'href="https://192.168.16.113/')
        print(name)
        lay.addWidget(label(str(name)))





widget.show()
app.exec_()
