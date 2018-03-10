from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QUrl, QObject, pyqtSignal, QThread
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from ui import *
import logging


# Configurando el registro de la aplicacion a un fichero .log
logging.basicConfig (filename='Notificador-Foro-HLG.log', level=logging.INFO, format='[%(asctime)s] %(message)s')
# sonido
notification_sound = './sounds/sound_notification.wav'
new_posts_sound = './sounds/sound_new_post.mp3'


class TrayIcon (QSystemTrayIcon):
    def __init__(self):
        super (TrayIcon, self).__init__ ()
        self.menu = QMenu ()

        goForoAction = QAction (QIcon (icons[0]), "&Foro HLG",
                                self, triggered=goForo)
        quitAction = QAction (QIcon (icon_exit), "&Salir",
                              self, triggered=self._quit)
        acercaDeAction = QAction (QIcon (icon_info), "&Acerca de...",
                                  self, triggered=acercaDe)
        delprofileAction = QAction (QIcon (icon_remove), "&Eliminar mi perfil",
                                    self, triggered=delprofile)
        settingAction = QAction (QIcon (config_icon), "&Configuracion",
                                 self, triggered=self.run_config)
        showAction = QAction ('Mostrar', self, triggered=self.lit_show)

        self.menu.addAction (showAction)
        self.menu.addAction (delprofileAction)
        self.menu.addSeparator ()
        self.menu.addAction (goForoAction)
        self.menu.addSeparator ()
        self.menu.addAction (settingAction)
        self.menu.addAction (acercaDeAction)
        self.menu.addAction (quitAction)

        self.setContextMenu (self.menu)
        self.setIcon (QIcon (icons[0]))
        self.show ()

    def _quit(self):
        # main.quit()
        QApplication.instance ().quit ()

    def run_config(self):
        setting.load_data ()
        setting.show ()

    def lit_show(self):
        self.noti = Notificar ()
        test_html = """<div class="notifications">
                    <a href="https://192.168.16.113">
                    <p class="notifications_title"><strong>Texto de prueba</strong> de <span class="username">
                    Usuario404</span>: "Un saludo"</p></a><p class="notifications_time">
                    <span title="Sat Mar 10, 2018 10:53 am">56 seconds ago</span></p></div>"""
        self.noti.setInfo ('avatars/no_avatar.gif', test_html)
        self.noti.trigger_notification ()


class AR (QThread):
    signal = pyqtSignal (list, list)

    def __init__(self):
        super (AR, self).__init__ ()

        self.Class = ScrapTo ()
        self.signal.connect (self.Class.mainNotificator)

    def __del__(self):
        self.wait ()

    def run(self):
        while True:
            self.main_notif ()
            self.sleep (self.Class.time)

    def int_notification(self):
        try:
            return forum.get_notification ()
        except FileNotFoundError:
            Login.show()
            return []
        except:
            logging.info ('No se pudo establecer una conexion con el servidor')
            trayIcon.setToolTip ('No conectado')
            self.Class.Notifi = 0
            return 404

    def int_newPosts(self):
        try:
            return forum.get_new_posts ()
        except:

            return []

    def main_notif(self):
        if not Login.isVisible():
            self.settings = self.Class.file.from_file ()
            noti = self.int_notification ()
            if noti != 404:
                if self.settings['notify_new_messages']:
                    newp = self.int_newPosts ()
                    self.signal.emit (noti, newp)
                else:
                    self.signal.emit (noti, [])

class ScrapTo:
    def __init__(self):
        # Cargar la configuracion

        self.en = Notificar ()
        self.file = DataFile (config_file)
        self.settings = self.file.from_file ()
        self.time = int (self.settings['time_between_requests'])
        # Variables para notificar
        self.posts = 0
        self.Notifi = 0
        self.Icono = 0

        url_notif = QUrl.fromLocalFile (notification_sound)
        content_notif = QMediaContent (url_notif)
        self.player = QMediaPlayer ()
        self.player.setMedia (content_notif)
        self.setTrayIconTimer = QTimer (timeout=self.setTrayIcon)
        self.setTrayIconTimer.start (400)

    def getNotif(self, notification):
        if self.Notifi < len (notification) != 0:
            value = len(notification)
        else:
            value = 0

        self.Notifi = len (notification)
        return value

    def getNewPosts(self, posts_before):
        self.posts = len(posts_before)
        if len(posts_before) != 0:
            return len(posts_before)
        else:
            return 0

    def mainNotificator(self, notificationsA=[], new_postsA=[]):
        notifications = self.getNotif (notificationsA)
        new_posts = self.getNewPosts (new_postsA)

        if notifications or new_posts:
            self.player.play ()

            if notifications and new_posts:
                print ('yeahasd')
                self.en.setNotificationsContent (notificationsA[0])
                self.en.setTitulo (notific=notifications, msgs=new_posts)
                logging.info ('%s Notificaciones, %s Mensajes Nuevos' % (notifications, new_posts))
            elif notifications:
                self.en.setNotificationsContent(notificationsA[0])
                self.en.setTitulo (notifications)
                logging.info ('%s Notificaciones' % notifications)
            elif new_posts:
                logging.info ('%s Mensajes Nuevos' % new_posts)
                self.en.setNewMessageContent(new_postsA)
                self.en.setTitulo (msgs=new_posts)
            self.en.trigger_notification ()
        else:
            pass

        setTryIconTip (self.Notifi, self.posts)

        # end (if notifications or new posts)

    def setTrayIcon(self):
        if self.Notifi != 0 or self.posts != 0:
            if self.Icono:
                self.Icono = 0
                trayIcon.setIcon (QIcon (icons[1]))
            else:
                self.Icono = 1
                trayIcon.setIcon (QIcon (icons[0]))
        else:
            trayIcon.setIcon (QIcon (icons[0]))


def acercaDe():
    QMessageBox.information (QWidget (), "Acerca de...", "Version: 2.7b\n"
                                                         "Autor: aCC")


def apply_saved_data():
    data = use_saved_data ()
    if not data:
        Login.show ()
    else:
        logging.info ('Notificando')
        pass


def setTryIconTip(text=0, msgs=0):
    if text and msgs:
        trayIcon.setToolTip ('Tienes %s notificaciones y %s Mensajes Nuevos' % (text, msgs))
    elif text:
        trayIcon.setToolTip ("Tiene %s notificaciones." % text)
    elif msgs:
        trayIcon.setToolTip ("Hay mensajes nuevos")
    else:
        trayIcon.setToolTip ("No tiene notificaciones.")


if __name__ == '__main__':
    app = QApplication ([])
    app.setApplicationName ('NForoHLG 2.7b')
    app.setWindowIcon (QIcon (icons[0]))
    QApplication.setQuitOnLastWindowClosed (False)
    # Iniciando las clases para usarlas mas adelante

    Login = Login ()
    setting = Config ()
    try:
        setting.load_data ()
    except:
        setting.save_f ()

    trayIcon = TrayIcon ()

    if page_available (FORO_URL):
        apply_saved_data ()
    else:
        trayIcon.setToolTip ('No conectado')

    # Siempre se aplica ScrapTo
    ar = AR ()
    ar.start ()

    app.exec_ ()
