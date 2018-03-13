from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QSpinBox, QLabel, \
    QGroupBox, QLineEdit, QGridLayout, QComboBox, QProxyStyle, QApplication, QTextBrowser
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QIcon, QFont, QCursor, QPixmap, QFontDatabase
from engine import *
import rc
import style

# Variables de archivos a usar (imagenes, texto, sonido)
config_file = './Config.cnf'
config_icon = './images/config.png'
icon_forum_logo = './images/motif_logo.png'
login_icon = './images/exeicon.png'
icon_exit = './images/salirtray.png'
icon_info = './images/info.png'
icon_remove = './images/dremove.png'

# iconos para mostrar en la barra
icons = ['images/forum.png', 'images/forum_msg.png']
#

forum = ForumScrap()

class Config(QWidget):
    """panel de configuracion"""

    def __init__(self):
        super(Config, self).__init__()
        #
        self.en = Notificar ()
        #

        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon(config_icon))
        self.setWindowTitle('Configuración Notificador')

        self.save = QPushButton('Guardar', clicked=self.save_f)
        self.cancel = QPushButton('Salir', clicked=self.cancel_f)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.save)
        button_layout.addWidget(self.cancel)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.Notification_group())
        mainLayout.addWidget(self.connection_parameters())
        mainLayout.addWidget(self.pick_styles())
        mainLayout.addLayout(button_layout)
        # styles
        self.setStyleSheet('background: none;')
        self.setStyle(QProxyStyle('Fusion'))

        self.setLayout(mainLayout)


    def Notification_group(self):
        groupBox = QGroupBox('Notificar')

        notifications = QCheckBox('Notificaciones')
        notifications.setChecked(1)
        notifications.setDisabled(1)
        self.new_messages = QCheckBox('Nuevos Mensajes')
        self.new_messages.setToolTip('Selecciona para notificar TODOS los mensajes que se publican.\n'
                               'No recomendado para Moderadores')

        layout = QVBoxLayout()
        layout.addWidget(notifications)
        layout.addWidget(self.new_messages)

        groupBox.setLayout(layout)
        return groupBox

    def pick_styles(self):
        groupBox = QGroupBox('Interfaz')

        layout = QHBoxLayout()
        label = QLabel('Estilos: ')
        self.styles = QComboBox(currentIndexChanged=self.show_style)
        self.styles.setToolTip('Elige tu estilo')
        self.styles.addItems (i for i in ['Default', 'Dark', 'White'])
        self.styles.currentIndexChanged.connect(self.show_style)
        layout.addWidget(label)
        layout.addWidget(self.styles)
        groupBox.setLayout(layout)

        return groupBox

    def show_style(self):
        if self.isVisible():
            self.en.show_example()
            self.en.change_style(self.styles.currentIndex())
            self.en.trigger_notification(anim=False)

    def connection_parameters(self):
        groupBox = QGroupBox('Parametros de conexión')

        wait_label = QLabel('Verificar notificaciones cada: ')
        seconds_label = QLabel('segundos')
        self.wait_spinbox = QSpinBox()
        self.wait_spinbox.setValue(10)

        wait_layout = QHBoxLayout()
        wait_layout.addWidget(wait_label)
        wait_layout.addWidget(self.wait_spinbox)
        wait_layout.addWidget(seconds_label)

        groupBox.setLayout(wait_layout)
        return groupBox

    def cancel_f(self):
        self.close()

    def save_f(self):
        # Guarda los datos serializandolos con el modulo json
        QMessageBox.information(self, 'Guardar', 'Datos guardados, para que se apliquen los cambios\n'
                                                 'de tiempo deberá reiniciar la app.')

        data = {
            'notify_new_messages': self.new_messages.checkState(),
            'current_style': self.styles.currentIndex(),
            'time_between_requests': self.wait_spinbox.value()
            }
        with open(config_file, 'w', encoding='utf-8') as h:
            dump(data, h, indent=4)

        return 1

    def apply_load_data(self, new_msg=0, time=10, index=0):
        self.new_messages.setChecked(new_msg)
        self.styles.setCurrentIndex(index)
        self.wait_spinbox.setValue(time)

    def load_data(self):
        file = DataFile(config_file)
        check = file.from_file()
        if check:
            time = check['time_between_requests']
            new_messages_value = check['notify_new_messages']
            style_index = check['current_style']
            self.apply_load_data(new_messages_value, time, style_index)
        else:
            pass


class Login(QWidget):
    """ Esta clase se utilizara para el logueo a la pagina, si se muesta la interfaz
    de logueo, a medida que se vaya escribiendo se va guardando los datos que introdujo
    el usuario en el archivo 'profile.cfg' , los datos se guardan codificados en 'cp1026'
    para que algun pillo se siente en tu pc y no te los lea asi de jamon, al dar click
    en el boton 'Aceptar' se loguea con los datos que escribiste"""

    def __init__(self):
        super().__init__()
        self.setWindowIcon (QIcon (login_icon))

        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.CenterLayout = QVBoxLayout(self)
        self.setGeometry (500, 500, 250, 250)

        # Estableciendo fonts
        font = QFont()
        font.setFamily("Helvetica LT Std Cond Blk")
        font.setPointSize(9)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)

        self.head = QLabel("<a style='color: #757575' href=http://foro.hlg.cu>FORUM HLG</a>")
        self.head.setObjectName('labelforum')
        self.head.setOpenExternalLinks(True)

        self.NombrePerfil = QLabel("Nombre:")
        self.NombrePerfil.setFont(font)

        self.EditNombre = QLineEdit(editingFinished=self.save_data)
        self.EditNombre.setAlignment(Qt.AlignCenter)

        self.PassPerfil = QLabel("Contraseña:")
        self.PassPerfil.setFont(font)

        self.EditPass = QLineEdit(editingFinished=self.save_data)
        self.EditPass.setAlignment(Qt.AlignCenter)
        self.EditPass.setEchoMode(QLineEdit.Password)

        self.LabelCAPTCHA = QLabel("Codigo de confirmacion:")
        self.LabelCAPTCHA.setFont(font)
        self.LabelCAPTCHA.hide()  # Esto por si se equivoca mucho el passw
        # para mostrar el Captcha
        self.ImagenCAPTCHA = QLabel('<img src="" />')  #
        self.ImagenCAPTCHA.hide()

        self.EditCAPTCHA = QLineEdit()
        self.EditCAPTCHA.setAlignment(Qt.AlignCenter)
        self.EditCAPTCHA.hide()

        self.Aceptar = QPushButton("Aceptar", clicked=self.loguearse)

        # Agregando elementos a la ventana
        self.CenterLayout.addWidget (self.head, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget (self.NombrePerfil, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget (self.EditNombre)
        self.CenterLayout.addWidget (self.PassPerfil, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget (self.EditPass)
        self.CenterLayout.addWidget (self.LabelCAPTCHA, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget (self.ImagenCAPTCHA, alignment=Qt.AlignCenter)
        self.CenterLayout.addWidget (self.EditCAPTCHA)
        self.CenterLayout.addSpacing (7)
        self.CenterLayout.addWidget (self.Aceptar)
        self.setStyleSheet(style.test)

    def save_data(self):
        """Guarda los datos que se escriben en los campos de edicion y los codifica
        a 'cp1026' """
        logging.info('Funcion save_data() aplicada, datos guardados')
        userdata = {'user': self.EditNombre.text(), 'password': self.EditPass.text()}
        with open(my_profile_data, 'w', encoding='cp1026')as h:
            dump(userdata, h)

    def loguearse(self):
        logging.info('Logueandose en la pagina')

        user = self.EditNombre.text()
        passw = self.EditPass.text()
        captcha_code = self.EditCAPTCHA.text()
        login = forum.login(user, passw, captcha_code)
        if login == 2:
            self.ImagenCAPTCHA.setText('<img src="" />')
            self.ImagenCAPTCHA.setText('<img src="./captcha.jpg" />')
            self.LabelCAPTCHA.show()
            self.ImagenCAPTCHA.show()
            self.EditCAPTCHA.show()

        elif login == 1:
            logging.info('Logueado correctamente')
            self.close()


class Notificar(QWidget):
    """Interfaz de la notificacion
    params: ancho -> ancho de la pantalla
            alto -> altura de la pantalla
    """

    def __init__(self):
        super().__init__()
        # color de la letra en la notificacion
        self.defaultColor = '#d3c7c7'
        self.defaultBackground = '#3a3838'

        self.setStyleSheet("background: #3a3838; border: 1px solid #a59191")
        datafont = QFontDatabase()
        datafont.addApplicationFont(':Adventur.ttf')



        self.restancho = 375
        self.ancho = QApplication.desktop().width() - self.restancho
        self.restalto = 160
        self.alto = QApplication.desktop().height() - self.restalto


        self.sizeWidth = 370
        self.sizeHeight = 115

        self.setWindowFlags(Qt.ToolTip)
        self.setGeometry(self.ancho, self.alto, self.sizeWidth, self.sizeHeight)
        self.cursor = QCursor()
        self.ocultar = QTimer(timeout=self.Ocultar)
        self.ocultar.time = 1.0

        self.CenterLayout = QHBoxLayout(self)
        self.CenterLayout.setContentsMargins(0, 0, 0, 0)
        self.CenterLayout.setSpacing(0)

        # add items
        self.CenterLayout.addWidget(self.MainBody2())
        #

        # applying saved data
        file = DataFile(config_file)
        data = file.from_file()
        self.change_style(data['current_style'], reboot=False)

    def trigger_notification(self, anim=True):
        if anim:
            self.an = QPropertyAnimation (self, b'geometry')
            self.an.setStartValue (QRect (self.ancho + self.restancho, self.alto, self.sizeWidth, self.sizeHeight))
            self.an.setEndValue (QRect (self.ancho, self.alto, self.sizeWidth, self.sizeHeight))
            self.an.setDuration (250)
            self.show ()
            self.an.start ()
        else:
            self.setGeometry (self.ancho, self.alto, self.sizeWidth, self.sizeHeight)
            self.show()

        self.ocultar.time = 1.0
        self.setWindowOpacity (self.ocultar.time)
        self.ocultar.start (3000)

    def close_anim(self):
        self.vn = QPropertyAnimation (self, b'geometry')
        self.vn.setStartValue (QRect (self.ancho, self.alto, self.sizeWidth, self.sizeHeight))
        self.vn.setEndValue (QRect (self.ancho + self.restancho, self.alto, self.sizeWidth, self.sizeHeight))
        self.vn.setDuration (150)
        self.vn.finished.connect(lambda : self.close())
        self.vn.start ()


    def MainBody2(self):
        self.widget = QWidget()
        layout = QHBoxLayout()
        mainlayout = QVBoxLayout(self.widget)
        self.cerrar = QPushButton (clicked=self.close_anim)
        self.cerrar.setStyleSheet (style.closebutton)
        self.title_label = QLabel ('Tienes 0 notificaciones')
        self.title_label.setStyleSheet('border: none')
        self.avatar = QLabel('Avatar')
        self.bla = QTextBrowser()
        self.bla.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bla.setOpenExternalLinks(True)
        self.bla.setStyleSheet("""border: 0px; background: transparent; 
                               font: 8pt 'Segoe UI'""")
        self.avatar.setScaledContents(True)
        self.avatar.setMaximumSize(60, 70)
        layout.addWidget(self.avatar, alignment=Qt.AlignTop)
        layout.addWidget (self.bla)

        lay = QHBoxLayout ()
        lay.addWidget (self.title_label)
        lay.addStretch(15)
        lay.addWidget (self.cerrar, Qt.AlignRight)

        mainlayout.addLayout(lay)
        mainlayout.addLayout(layout)
        return self.widget

    def show_example(self):
        test_html = """<div class="notifications">
                    <a href="https://foro.hlg.cu">
                    <p class="notifications_title"><strong>Texto de prueba</strong> de <span class="username">
                    Usuario404</span>: "Un saludo"</p></a><p class="notifications_time">
                    <span title="Sat Mar 10, 2018 10:53 am">56 seconds ago</span></p></div>"""
        self.setInfo ('avatars/no_avatar.gif', test_html)

    def setInfo(self, avatar, info):
        #self.body.setText(info)
        style = '<style> div{color:%s}a{color:%s}</style>' % (self.defaultColor, self.defaultColor)
        self.bla.setHtml(style+info )
        self.avatar.setPixmap(QPixmap(avatar))

    def setNotificationsContent(self, n=[]):
        self.setInfo(n[1], n[0])

    def setNewMessageContent(self, m=[]):
        default = 'avatars/no_avatar.gif'
        self.setInfo (default, m[0])

    def change_style(self, index, reboot=True):
        white_font = '#d3c7c7'
        black_font = '#292828'
        black_background = '#3a3838'
        blue_background = '#2d76d4'
        white_background = '#d7dbe0'

        complements = [(blue_background, black_font), (black_background, white_font),
                       (white_background, black_font)]
        self.setStyleSheet ("background: %s; border: 1px solid #a59191" % complements[index][0])
        self.defaultColor = complements[index][1]

        if reboot:
            self.ocultar.time = 1.0
            self.setWindowOpacity (self.ocultar.time)
            self.ocultar.start (5000)
        else:
            pass

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
        if notific and msgs:
            self.title_label.setText('Tienes %s notificaciones y %s Mensajes Nuevos' % (notific, msgs))
        elif notific :
            self.title_label.setText ('Tienes %s notificaciones' % notific)
        elif msgs:
            self.title_label.setText ('Tienes %s Mensajes Nuevos' % msgs)




if __name__ == '__main__':
    app = QApplication([])
    m = Notificar()
    m.trigger_notification()
    app.exec_()

