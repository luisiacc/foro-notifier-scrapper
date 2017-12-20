from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from bs4 import BeautifulSoup
from os import system, getcwd
from json import dump, load
import style
import requests

requests.packages.urllib3.disable_warnings()    # Deshabilitar advertencias

#icons
icons = ['images/forum.png', 'images/forum_msg.png']

# urls a usar
LOGIN_URL = 'https://192.168.16.113/ucp.php?mode=login'
NEWPOSTS_URL = 'https://192.168.16.113/search.php?search_id=newposts'
FORO_URL = 'https://192.168.16.113'
NOTIF_URL = 'https://192.168.16.113/ucp.php?i=ucp_notifications'
headers = {'User-Agent': 'Mozilla/5.0'}

# Iniciar Session()
session = requests.Session()
session.headers = headers
session.verify = False
#

class Login(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.CenterLayout = QVBoxLayout(self)
        self.setStyleSheet(style.back)
        self.setWindowIcon(QIcon(icons[0]))
        # Estableciendo fonts
        font = QFont()
        font.setFamily("Helvetica LT Std Cond Blk")
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)

        self.head = QLabel("<a href=http://192.168.16.113>FORUM HLG</a>")
        self.head.setOpenExternalLinks(True)
        self.head.setStyleSheet(style.labelforum)

        self.NombrePerfil = QLabel("Nombre:")
        self.NombrePerfil.setFont(font)
        self.NombrePerfil.setStyleSheet(style.label)

        self.EditNombre = QLineEdit(textChanged=self.save_data)
        self.EditNombre.setAlignment(Qt.AlignCenter)
        self.EditNombre.setStyleSheet(style.lineedit)

        self.PassPerfil = QLabel("Contraseña:")
        self.PassPerfil.setFont(font)
        self.PassPerfil.setStyleSheet(style.label)

        self.EditPass = QLineEdit(textChanged=self.save_data)
        self.EditPass.setAlignment(Qt.AlignCenter)
        self.EditPass.setStyleSheet(style.lineedit)
        self.EditPass.setEchoMode(QLineEdit.Password)

        self.LabelCAPTCHA = QLabel("Codigo de confirmacion:")
        self.LabelCAPTCHA.setFont(font)
        self.LabelCAPTCHA.hide()                            #
        self.LabelCAPTCHA.setStyleSheet(style.label)        # Esto por si se equivoca mucho el passw
                                                            # para mostrar el Captcha
        self.ImagenCAPTCHA = QLabel('<img src="" />')       #
        self.ImagenCAPTCHA.hide()

        self.EditCAPTCHA = QLineEdit()
        self.EditCAPTCHA.setAlignment(Qt.AlignCenter)
        self.EditCAPTCHA.captchaID = ''
        self.EditCAPTCHA.hide()

        self.Aceptar = QPushButton("Aceptar", clicked=self.loguearse)
        self.Aceptar.setStyleSheet(style.button)

        # Agregando elementos a la ventana
        self.CenterLayout.addWidget(self.head, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget(self.NombrePerfil, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget(self.EditNombre)
        self.CenterLayout.addWidget(self.PassPerfil, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget(self.EditPass)
        self.CenterLayout.addWidget(self.LabelCAPTCHA, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget(self.ImagenCAPTCHA, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget(self.EditCAPTCHA)
        self.CenterLayout.addWidget(self.Aceptar, alignment=Qt.AlignCenter)

    def save_data(self):
        userdata = {'user': self.EditNombre.text(), 'password': self.EditPass.text()}
        with open('./profile.cfg', 'w', encoding='cp1026')as h:
            dump(userdata, h)

    def loguearse(self):

        self.payloads = {
            'username': self.EditNombre.text(),
            'password': self.EditPass.text(),
            'login': 'Login',
            'sid': '',
            'confirm_code': self.EditCAPTCHA.text(),
            'confirm_id': self.EditCAPTCHA.captchaID,
            'redirect': 'index.php'
            }

        html = session.post(LOGIN_URL, data=self.payloads)

        if html.status_code == 200:
            html = BeautifulSoup(html.text, "html.parser")
            resp = html.find('div', {'class': 'error'})
            if resp:
                resp = str(resp).replace('href=".', 'href="' + FORO_URL)
                QMessageBox.information(self, "Error de identificacion", resp)
                # Descargando el Captcha
                resp = html.find('dd', {'class': 'captcha captcha-image'})
                if resp:
                    resp = html.find('img')
                    resp = resp.get("src")
                    if resp[0] == '.':
                        resp = resp[1:]
                    self.EditCAPTCHA.captchaID = resp[33:-7]
                    resp = session.get(FORO_URL + resp, stream=True)
                    with open("captcha.jpg", "wb") as file:
                        for chunk in resp.iter_content():
                            file.write(chunk)
                    self.ImagenCAPTCHA.setText('<img src="" />')
                    self.ImagenCAPTCHA.setText('<img src="./captcha.jpg" />')
                    self.LabelCAPTCHA.show()
                    self.ImagenCAPTCHA.show()
                    self.EditCAPTCHA.show()

            else:
                self.close()

    def setTryIconTip(self, text):
        if text > 0:
            app.trayIcon.setToolTip("Tiene %s notificaciones." % text)
        else:
            app.trayIcon.setToolTip("No tiene notificaciones.")


class ScrapTo:
    def __init__(self):
        self.Notifi = 0
        self.Icono = 0
        url = QUrl.fromLocalFile("sounds\sound.wav")
        content = QMediaContent(url)
        self.player = QMediaPlayer()
        self.player.setMedia(content)
        self.getPaginaTimer = QTimer(timeout=self.getNotif)
        self.getPaginaTimer.start(10000)
        self.getpostsTimer = QTimer(timeout=self.getNewPosts)
        self.getpostsTimer.start(10000)
        self.setTrayIconTimer = QTimer(timeout=self.setTrayIcon)
        self.setTrayIconTimer.start(500)

    def getNotif(self):
        if not Login.isVisible():
                html = session.get(FORO_URL)
                if html.status_code == 200:
                    html = BeautifulSoup(html.text, "html.parser")
                    resp = html.find('a', {'title': 'Identificarse'})
                    if resp:
                        Login.show()
                    else:
                        try:
                            notificaciones = int(html.title.string.split()[0][1])
                        except:
                            notificaciones = 0

                        if self.Notifi < int(notificaciones) != 0:
                            self.player.play()
                            en = Notificar()
                            en.setTitulo(notificaciones)

                        self.Notifi = int(notificaciones)
                        Login.setTryIconTip(self.Notifi)

                else:
                    app.trayIcon.setToolTip('No conectado')

    def getNewPosts(self):
        self.posts = []
        html = session.get(NEWPOSTS_URL)

        soup = BeautifulSoup(html.content, 'html.parser')

        topiclist = []
        usernames = []
        for i in soup.find_all('div', {'class': 'list-inner'}):
            topic = i.find('a', {'class': 'topictitle'})
            user = i.find('a', 'username-coloured')

            try:
                topiclist.append(topic.text)

                try:
                    usernames.append(user.text)

                except:
                    user = i.find('a', 'username')
                    usernames.append(user.text)

            except:
                pass

        for a, b in zip(topiclist, usernames):
            text = "'{topic}'iniciado por: {user}".format(topic=a, user=b)
            self.posts.append(text)

    def setTrayIcon(self):
        if self.Notifi != 0:
            if self.Icono:
                self.Icono = 0
                app.trayIcon.setIcon(QIcon(icons[1]))
            else:
                self.Icono = 1
                app.trayIcon.setIcon(QIcon(icons[0]))
        else:
            app.trayIcon.setIcon(QIcon(icons[0]))


class Notificar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.ToolTip)
        self.setGeometry(ancho - 295, alto - 120, 290, 75)
        self.cursor = QCursor()
        self.ocultar = QTimer(timeout=self.Ocultar)
        self.ocultar.time = 1.0

        self.CenterLayout = QHBoxLayout(self)
        self.CenterLayout.setContentsMargins(0, 0, 0, 0)
        self.CenterLayout.setSpacing(0)

        #add items
        self.CenterLayout.addWidget(self.SetWidget())
        #
        self.setStyleSheet('background: rgb(137, 188, 255)')
        self.ocultar.start(3000)
        self.show()

    def MainBody(self):
        Widget = QWidget()

        self.CenterLayout = QGridLayout()
        self.MainLayout = QHBoxLayout(Widget)

        self.Avatar = QLabel('<a href=http://192.168.16.113> </a>')
        self.Avatar.setOpenExternalLinks(True)
        self.Avatar.setPixmap(QPixmap('images\motif_logo.png'))
        self.Avatar.setAlignment(Qt.AlignCenter)
        self.Avatar.setMaximumSize(50, 50)
        self.Avatar.setStyleSheet(style.label)
        self.Avatar.setScaledContents(True)

        self.Titulo = QLabel('<b>Notificador <a href=http://192.168.16.113>FORUM HLG</a></b>')
        self.Titulo.setOpenExternalLinks(True)
        self.Titulo.setStyleSheet(style.notiflabel)
        self.Texto = QLabel('No hay notificaciones')
        self.Texto.setStyleSheet(style.label)

        self.cerrar = QPushButton(clicked=lambda: self.close())
        self.cerrar.setGeometry(20, 20, 20, 20)
        self.cerrar.setIcon(QIcon('images\salirtray.png'))
        self.cerrar.setMaximumSize(20, 20)
        self.cerrar.setStyleSheet('background: transparent')

        self.CenterLayout.addWidget(self.Titulo, 0, 0)
        self.CenterLayout.addWidget(self.cerrar, 0, 1)
        self.CenterLayout.addWidget(self.Texto, 1, 0)

        self.MainLayout.addWidget(self.Avatar)
        self.MainLayout.addLayout(self.CenterLayout)

        return Widget

    def SetWidget(self):
        ListWidget = QListWidget()

        myQCustomQWidget = self.MainBody()
        lostwidg = QListWidgetItem(ListWidget)
        lostwidg.setSizeHint(myQCustomQWidget.sizeHint())
        ListWidget.addItem(lostwidg)
        ListWidget.setItemWidget(lostwidg, myQCustomQWidget)

        return ListWidget

    def Ocultar(self):
        if self.windowOpacity() <= 0.01:
            self.hide()
            self.ocultar.time = 1.0
            self.setWindowOpacity(self.ocultar.time)
        elif self.cursor.pos().x() >= self.pos().x() and self.cursor.pos().y() >= self.pos().y():
            self.ocultar.time = 1.0
            self.setWindowOpacity(self.ocultar.time)
            self.ocultar.start(1000)
        else:
            self.ocultar.time -= 0.01
            self.setWindowOpacity(self.ocultar.time)
            self.ocultar.start(self.ocultar.time*100)


    def setTitulo(self, notific=0, msgs=0):
        if notific > 0:
            self.Texto.setText('Tienes %s notificaciones' % notific)
        elif msgs == 1:
            self.Texto.setText('Hay mensajes nuevos')


def acercaDe():
    QMessageBox.information(QWidget(), "Acerca de...", "Version: 2.1b\n"
                                                   "Autor: aCC")

def goForo():
    system("start http://192.168.16.113") #Windows OS

def InicioWindows():
    pass

def check_profile():
    try:
        #obteniendo los datos de usuario
        with open('./profile.cfg', encoding='cp1026') as h:
                mypro = load(h)
        return mypro

    except:
        return 0

def delprofile():
    msg = QMessageBox()
    msg.setText("¿ Estas seguro de borrar tu perfil ?")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    value = msg.exec_()
    if value == 1024:
        with open('./profile.cfg', 'w', encoding='cp1026') as m:
            pass
    else:
        pass

def page_available():
    # devuelve: 1- Pagina disponible, 0-No disponible
    availability = requests.get('http://192.168.16.113', verify=False)
    if availability.status_code == 200:
        return 1
    else:
        return 0

if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName('Notificador Foro HLG')
    app.setWindowIcon(QIcon(icons[0]))
    QApplication.setQuitOnLastWindowClosed(False)

    ancho = app.desktop().width()
    alto = app.desktop().height()

    app.trayIcon = QSystemTrayIcon()
    trayIconMenu = QMenu()

    goForoAction = QAction(QIcon('images\motif_logo.png'),"&Foro HLG", app, triggered=goForo)
    quitAction = QAction(QIcon('images\salirtray.png'),"&Salir", app, triggered=QApplication.instance().quit)
    acercaDeAction = QAction(QIcon('images\info.png'),"&Acerca de...", app, triggered=acercaDe)
    delprofileAction = QAction(QIcon('images\dremove.png'), "&Eliminar mi perfil", app, triggered=delprofile)

    trayIconMenu.addAction(delprofileAction)
    trayIconMenu.addSeparator()
    trayIconMenu.addAction(goForoAction)
    trayIconMenu.addAction(acercaDeAction)
    trayIconMenu.addAction(quitAction)

    app.trayIcon.setContextMenu(trayIconMenu)
    app.trayIcon.setIcon(QIcon(icons[0]))
    app.trayIcon.show()

    if page_available():

        if check_profile():
            Login = Login()
            data = check_profile()

            # Cuando se guarden las credenciales no hara falta manejar errores ya que
            # no hay error
            payloads = {
                'username': data['user'],
                'password': data['password'],
                'login': 'Login',
                'sid': '',
                'redirect': 'index.php'
                }

            html = session.post(LOGIN_URL, data=payloads)
            ScrapTo = ScrapTo()
        else:
            Login = Login()
            Login.show()
            Scrap = ScrapTo()

    else:
        app.trayIcon.setToolTip('No conectado')


    app.exec_()