from PyQt5.QtWidgets import QMessageBox, QWidget
from bs4 import BeautifulSoup
from requests import Session, packages, get
from os import getcwd
from json import load, dump
from webbrowser import open as openpage
import logging

packages.urllib3.disable_warnings()  # Deshabilitar advertencias

# urls a usar
LOGIN_URL = 'https://192.168.16.113/ucp.php?mode=login'
NEWPOSTS_URL = 'https://192.168.16.113/search.php?search_id=newposts'
FORO_URL = 'https://192.168.16.113'
NEW_URL = 'https://192.168.16.113/search.php?search_id=egosearch'
NOTIF_URL = 'https://192.168.16.113/ucp.php?i=ucp_notifications'
headers = {'User-Agent': 'Mozilla/5.0'}

# vars
my_profile_data = getcwd() + './profile.cfg'
file_posts = './latest_posts.txt'

# Iniciar Session()
session = Session()
session.headers = headers
session.verify = False
#

class ForumScrap:
    """
    Aqui se realizan todas las peticiones a la pagina web.
    Tambien:
    Esta clase se encarga de extraer los datos de la pagina, en este caso , cada vez
    que hay una notificacion, en el titulo aparece el numero de notificaciones,
    Ej: (1)Forum-HLG
    cada vez que haya un numero en el titulo, se notifica por sonido usando
    'QMediaPlayer', y mostrando una notificacion(definida en una clase posterior)
    Las peticiones se hacen cada 10 segundos, que esta definido en la linea:
    self.getPaginaTimer.start(10000)     # tiempo en milisegundos
    """

    def __init__(self):
        self.captcha_id = ''

    def login(self, username='', password='', captcha_code=''):

        self.payloads = {
            'username': username,
            'password': password,
            'login': 'Login',
            'sid': '',
            'confirm_code': captcha_code,
            'confirm_id': self.captcha_id,
            'redirect': 'index.php'
            }

        html = session.post(LOGIN_URL, data=self.payloads)
        if html.status_code == 200:
            html = BeautifulSoup(html.text, "html.parser")
            resp = html.find('div', {'class': 'error'})
            if resp:
                logging.info('Datos incorrectos introducidos')
                resp = str(resp).replace('href=".', 'href="' + FORO_URL)
                QMessageBox.information(QWidget(), "Error de identificacion", resp)
                # Descargando el Captcha
                resp = html.find('dd', {'class': 'captcha captcha-image'})
                if resp:
                    logging.info('Descargando el Captcha')
                    resp = html.find('img')
                    resp = resp.get("src")
                    if resp[0] == '.':
                        resp = resp[1:]
                    self.captcha_id = resp[33:-7]
                    resp = session.get(FORO_URL + resp, stream=True)
                    with open("captcha.jpg", "wb") as file:
                        for chunk in resp.iter_content():
                            file.write(chunk)
                    return 2
            else:
                return 1

    def get_notification(self):
        try:
            html = session.get(NOTIF_URL)
        except:
            raise Exception
        if html.status_code == 200:
            html = BeautifulSoup(html.text, "html.parser")
            resp = html.find('a', {'title': 'Identificarse'})
            if resp:
                resp = use_saved_data()
                if not resp:
                    raise FileNotFoundError
            else:
                try:
                    notificaciones = int(html.title.string.split()[0][1:-1])
                except:
                    notificaciones = 0

                if notificaciones:
                    info = self.get_html_notif(html, notificaciones)
                    return info
                else:
                    return []
        else:
            raise Exception

    def get_html_notif(self, soup: BeautifulSoup, number):
        li = []
        hy = 0
        for i in soup.find_all ('li', 'row'):
            if hy == number:
                break
            hy += 1
            img = i.find ('img')
            src = img.get ('data-src')
            if src is None:
                src = img.get ('src')
            srcf = 'https://192.168.16.113' + src[1:]
            avatar_name = self.get_name (src)

            if self.not_exists(avatar_name):
                self.download_img (srcf, avatar_name)

            clas_notif = i.find ('div', {'class': 'notifications'})
            te = clas_notif.find ('a')
            if te is not None:
                # n = str(te).replace('href="./', 'href="https://192.168.16.113/')
                # n = n.replace('amp;', '')
                # m = n[:3] + 'style="color:black; text-decoration:none" ' + n[3:]
                notification = str (clas_notif).replace ('href="./', 'href="https://192.168.16.113/')
            else:
                notification = str (clas_notif)

            li.append([notification, avatar_name])
        return li

    def get_name(self, url: str):
        if url.startswith ('./download'):
            place = url.find ('avatar')
            return 'avatars/'+url[place + 7:]
        else:
            return 'avatars/no_avatar.gif'

    def download_img(self, url, name):
        file = session.get (url, stream=True)
        with open (name, 'wb') as h:
            for i in file.iter_content ():
                h.write (i)

    def not_exists(self, file):
        try:
            m = open (file)
            m.close ()
            return False
        except FileNotFoundError:
            return True

    def get_new_posts(self):
        def respones():
            try:
                soup = session.get(NEWPOSTS_URL)
            except:
                raise Exception
            if soup.status_code == 200:
                    soup = BeautifulSoup(soup.text, 'html.parser')
                    respuestas = []
                    final = []
                    posts = []
                    # Parseando el html
                    for i in soup.find_all('li', {'class': 'row'}):
                        # topic - titulo de los posts
                        topic = i.find('a', {'class': 'topictitle'})
                        # answers - seccion que dice el numero de respuestas
                        answers = i.find('dd', {'class': 'posts'})

                        try:
                            respuestas.append(answers.text)
                            topic = str(topic).replace('href="./', 'href="https://192.168.16.113/')
                            posts.append(str(topic))

                        except:
                            pass
                    # Quitar los tabuladores \t y saltos de linea \n
                    respuestas = [x.replace('\n\t\t\t\t\t\t', '') for x in respuestas]
                    # Convirtiendo los resultados de la lista 'respuestas' al numero de
                    # respuestas. Ej: convertir la cadena 'Respuestas: 3" al entero 3.
                    for m in respuestas:
                        t = m.find('Vistas')
                        m = int(m[t-2:t])
                        final.append(m)
                    return zip(posts, final)

            else:
                raise Exception

        # Iniciar la clase para trabajar con el archivo file_posts
        file = DataFile(file_posts)
        # Chequeo el archivo
        get_data = list(file.from_file())
        # Obtengo los posts actuales de la pagina
        zipped_list = respones()
        # Chequeando si el fichero esta vacio
        news = []
        if not get_data:
            # Si esta vacio escribe los post actuales
            file.to_file(list(zipped_list))
        else:
            for post, answ in zipped_list:
                # Aqui uso una lista [post, answ] pues json no reconoce
                # las tuplas, sino que las convierte a lista
                chain = [post, answ]
                try:
                    # index si no encuentra el valor lanza excepcion
                    place = get_data.index(chain)
                except:
                    news.append(post)
                    get_data.append(chain)
                    file.to_file(get_data)

        if len(file) > 50:
            file.del_elements(10)
        else:
            pass

        return news

class DataFile:
    def __init__(self, file):
        self.file = file

    def from_file(self, encode='utf-8'):
        try:
            # obteniendo los datos del archivo
            logging.info('Analizando el archivo "%s" ' % self.file)
            with open(self.file, encoding=encode) as h:
                # Si esta vacio lanza error JSONDecodeError
                mypro = load(h)
                return mypro
        except:
            logging.info('El archivo "%s" esta vacio ' % self.file)
            return []

    def to_file(self, li):
        # Serializar datos en el archivo especificado
        with open(self.file, 'w') as h:
            dump(li, h)

    def del_elements(self, lines_to_delete=5):
        # Elimina de un archivo los 1ros elementos del arch especificado
        try:
            with open(self.file) as h:
                all_lines = load(h)
            # Elimina la cantidad de elementos de la lista especificados
            del all_lines[:lines_to_delete]
            # Sobrescribe el fichero con los elementos ya borradas
            with open(self.file, 'w') as h:
                dump(all_lines, h)
            return all_lines

        except:
            return 0

    def __len__(self):
        return len(self.from_file())

def page_available(url):
    """devuelve: 1-Pagina disponible, 0-No disponible"""
    try:
        availability = get(url, verify=False)
        if availability.status_code == 200:
            logging.info('Pagina disponible')
            return 1
        else:
            logging.info('Pagina no disponible')
            return 0
    except:
        logging.info('Pagina no encontrada')
        return 0

def use_saved_data():
    file = DataFile(my_profile_data)
    data = file.from_file(encode='cp1026')
    if data:
        logging.info('Obteniendo los datos del archivo "profile.cfg" ')

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
            logging.info('Datos guardados incorrectos')
            return 0
        else:
            logging.info('Notificando')
            return 1
    else:
        logging.info('Ejecutando Login')
        return 0

def goForo():
    openpage(FORO_URL)

def delprofile():
    """Mas claro ni el agua, para borrar el perfil, borrando los datos
    salvados en el archivo 'profile.cfg' """
    msg = QMessageBox()
    msg.setText("¿ Estas seguro de borrar tu perfil ?")
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    value = msg.exec_()
    if value == 1024:
        logging.info('Borrando perfil')
        with open(my_profile_data, 'w', encoding='cp1026') as m:
            pass
    else:
        pass
