from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout,\
    QGridLayout, QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QUrl, QTimer, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap, QFont, QCursor
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from bs4 import BeautifulSoup
from os import system, getcwd
from json import dump, load
import logging
import style
from requests import Session, packages, get

packages.urllib3.disable_warnings()  # Deshabilitar advertencias

# iconos para mostrar en la barra
icons = ['images/forum.png', 'images/forum_msg.png']

# urls a usar
LOGIN_URL = 'https://192.168.16.113/ucp.php?mode=login'
NEWPOSTS_URL = 'https://192.168.16.113/search.php?search_id=newposts'
FORO_URL = 'https://192.168.16.113'
NOTIF_URL = 'https://192.168.16.113/ucp.php?i=ucp_notifications'
headers = {'User-Agent': 'Mozilla/5.0'}

# Iniciar Session()
session = Session()
session.headers = headers
session.verify = False
#

# Variables de archivos a usar (imagenes, texto, sonido)
my_profile_data = getcwd() + '\profile.cfg'
icon_forum_logo = getcwd() + '\images\motif_logo.png'
icon_exit = getcwd() + '\images\salirtray.png'
icon_info = getcwd() + '\images\info.png'
icon_remove = getcwd() + '\images\dremove.png'
notification_sound = getcwd() + '\sounds\sound.wav'


class Login(QWidget):
    """ Esta clase se utilizara para el logueo a la pagina, si se muesta la interfaz
    de logueo, a medida que se vaya escribiendo se va guardando los datos que introdujo
    el usuario en el archivo 'profile.cfg' , los datos se guardan codificados en 'cp1026'
    para que algun pillo se siente en tu pc y no te los lea asi de jamon, al dar click
    en el boton 'Aceptar' se loguea con los datos que escribiste"""

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
        self.LabelCAPTCHA.hide()  #
        self.LabelCAPTCHA.setStyleSheet(style.label)    # Esto por si se equivoca mucho el passw
                                                        # para mostrar el Captcha
        self.ImagenCAPTCHA = QLabel('<img src="" />')   #
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
        """Guarda los datos que se escriben en los campos de edicion y los codifica
        a 'cp1026' """
        userdata = {'user': self.EditNombre.text(), 'password': self.EditPass.text()}
        with open(my_profile_data, 'w', encoding='cp1026')as h:
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

    def setTryIconTip(self, text=0, msgs=0):
        if text:
            app.trayIcon.setToolTip("Tiene %s notificaciones." % text)
        elif msgs:
            app.trayIcon.setToolTip("Hay mensajes nuevos")
        else:
            app.trayIcon.setToolTip("No tiene notificaciones.")


class ScrapTo:
    """Esta clase se encarga de extraer los datos de la pagina, en este caso , cada vez
    que hay una notificacion, en el titulo aparece el numero de notificaciones,
    Ej: (1)Forum-HLG
    cada vez que haya un numero en el titulo, se notifica por sonido usando 'QMediaPlayer', y mostrando
    una notificacion(definida en una clase posterior)
    Las peticiones se hacen cada 10 segundos, que esta definido en la linea:
    self.getPaginaTimer.start(10000)     # tiempo en milisegundos
    """

    def __init__(self):
        self.Notifi = 0
        self.Icono = 0
        url = QUrl.fromLocalFile(notification_sound)
        content = QMediaContent(url)
        self.player = QMediaPlayer()
        self.player.setMedia(content)
        self.getPaginaTimer = QTimer(timeout=self.getNotif)
        self.getPaginaTimer.start(10000)
        # self.getpostsTimer = QTimer(timeout=self.getNewPosts)
        # self.getpostsTimer.start(10000)
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
        # Aun en desarrollo
        posts_before = []
        posts_after = []
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
            posts_before.append(text)

        if len(posts_after) < len(posts_before) != 0:
            self.player.play()
            en = Notificar()
            en.setTitulo(notificaciones=0, msgs=1)

        posts_after = [x for x in posts_before]

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
    """Interfaz de la notificacion"""

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

        # add items
        self.CenterLayout.addWidget(self.MainBody())
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
        self.Avatar.setPixmap(QPixmap(icon_forum_logo))
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
        self.cerrar.setIcon(QIcon(icon_exit))
        self.cerrar.setMaximumSize(20, 20)
        self.cerrar.setStyleSheet(style.label)

        self.CenterLayout.addWidget(self.Titulo, 0, 0)
        self.CenterLayout.addWidget(self.cerrar, 0, 1)
        self.CenterLayout.addWidget(self.Texto, 1, 0)

        self.MainLayout.addWidget(self.Avatar)
        self.MainLayout.addLayout(self.CenterLayout)
        Widget.setStyleSheet(style.notifcation)

        return Widget

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
            self.ocultar.start(self.ocultar.time * 100)

    def setTitulo(self, notific=0, msgs=0):
        if notific > 0:
            self.Texto.setText('Tienes %s notificaciones' % notific)
        elif msgs == 1:
            self.Texto.setText('Hay mensajes nuevos')


def acercaDe():
    QMessageBox.information(QWidget(), "Acerca de...", "Version: 2.1b\n"
                                                       "Autor: aCC")

def goForo():
    system("start %s" % FORO_URL)  # Windows OS


def InicioWindows():
    pass


def check_profile():
    try:
        # obteniendo los datos de usuario
        with open(my_profile_data, encoding='cp1026') as h:
            mypro = load(h)  # Si esta vacio lanza error JSONDecodeError
        return mypro

    except:
        return 0


def delprofile():
    """Mas claro ni el agua, para borrar el perfil, borrando los datos
    salvados en el archivo 'profile.cfg' """
    msg = QMessageBox()
    msg.setText("¿ Estas seguro de borrar tu perfil ?")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    value = msg.exec_()
    if value == 1024:
        with open(my_profile_data, 'w', encoding='cp1026') as m:
            pass
    else:
        pass


def page_available(url):
    """devuelve: 1-Pagina disponible, 0-No disponible"""
    try:
        availability = get(url, verify=False)
        if availability.status_code == 200:
            return 1
        else:
            return 0
    except:
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

    goForoAction = QAction(QIcon(icon_forum_logo), "&Foro HLG", app, triggered=goForo)
    quitAction = QAction(QIcon(icon_exit), "&Salir", app, triggered=QApplication.instance().quit)
    acercaDeAction = QAction(QIcon(icon_info), "&Acerca de...", app, triggered=acercaDe)
    delprofileAction = QAction(QIcon(icon_remove), "&Eliminar mi perfil", app, triggered=delprofile)

    trayIconMenu.addAction(delprofileAction)
    trayIconMenu.addSeparator()
    trayIconMenu.addAction(goForoAction)
    trayIconMenu.addAction(acercaDeAction)
    trayIconMenu.addAction(quitAction)

    app.trayIcon.setContextMenu(trayIconMenu)
    app.trayIcon.setIcon(QIcon(icons[0]))
    app.trayIcon.show()

    if page_available(FORO_URL):

        if check_profile():
            Login = Login()
            data = check_profile()

            payloads = {
                'username': data['user'],
                'password': data['password'],
                'login': 'Login',
                'sid': '',
                'redirect': 'index.php'
            }

            petic = session.post(LOGIN_URL, data=payloads)
            # Chequeando si los datos guardados son correctos
            html = BeautifulSoup(petic.text, 'html.parser')
            resp = html.find('div', {'class': 'error'})
            if resp:
                Login.show()
            ScrapTo = ScrapTo()
        else:
            Login = Login()
            Login.show()
            Scrap = ScrapTo()

    else:
        app.trayIcon.setToolTip('No conectado')

    app.exec_()
