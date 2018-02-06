button = """
QPushButton {
font: 75 11pt 'MS Shell Dlg 2';
border: 2px solid #8f8f91;
border-radius: 3px;
color: white;
background-color:  qlineargradient(spread:pad, x1:0, y1:0, x2:0.903, y2:0.954545, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(21, 68, 81, 255));
min-width: 80px;
margin: 2px}

QPushButton:pressed {
background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                            stop: 0 #dadbde, stop: 1 #f6f7fa);}

QPushButton:hover {
font: 75 11pt 'MS Shell Dlg 2';
border: 2px solid #8f8f91;
border-radius: 3px;
color: white;
background-color:  qlineargradient(spread:pad, x1:0, y1:0, x2:0.903, y2:0.954545, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(21, 68, 81, 255));
min-width: 80px;
margin: 0px
}
"""

lineedit = """
QLineEdit {
border: 2px solid #8f8f91;
border-radius: 5px;
background: white;
font: 11pt 'MS Shell Dlg 2';}

QLineEdit:hover {
border: 2px solid #7ccdff;
border-radius: 5px;
font: 11pt 'MS Shell Dlg 2';
}
"""

notification_widget_style_default = """
QWidget {
background: rgb(137, 188, 255);
border: 2px solid #8f8f91;
}

QLabel {
font: 9pt "Segoe UI";
background: transparent;
border: 0px;
}

QLabel#notiflabel {
font: 13pt "Adventure"; 
background: transparent; 
border: 0px;}"""

notification_widget_style_dark = """
QWidget {
background: rgb(53, 53, 53);
border: 2px solid #8f8f91;
}

QLabel {
font: 9pt "Segoe UI";
color: rgb(239, 239, 239);
background: transparent;
border: 0px;
}

QLabel#notiflabel {
font: 13pt "Adventure";
background: transparent; 
border: 0px;}"""

notification_widget_style_white = """
QWidget {
background: rgb(230, 230, 230);
border: 2px solid #8f8f91;
}

QLabel {
font: 9pt "Segoe UI";
background: transparent;
border: 0px;
}

QLabel#notiflabel {
font: 13pt "Adventure";
background: transparent; 
border: 0px;}"""

labelforum = """QLabel {font: 20pt "Adventure";
color:rgb(83, 149, 255);
background: transparent};

QLabel:hover {
font: 22pt "Eras Bold ITC";
color:rgb(83, 149, 255);
background: white;}"""

label = """
QLabel {
background: transparent;
border: 0px;}
"""

special = """
QLabel {
image: url(images/motif_logo.png);
width: 50px;
height: 50px;}
"""

closebutton = """
QPushButton {
image: url(images/arrow.png);
width: 16px;
height: 16px;
border: 0px;
}
QPushButton:hover {
image: url(images/arrow_hover.png);
background: none;
padding: 0px;
}"""

labeltext = "background: transparent; border: 0px; color: white"

back = """background: qlineargradient(spread:pad, x1:0, y1:0, x2:0.903, y2:0.954545,
 stop:0 rgba(255, 255, 255, 255), stop:1 rgba(55, 172, 203, 255));
 QLabel {
 background: transparent}"""



test = """
QWidget {
background: #282828;}

QLabel#labelforum {
font: 20pt "Comic Sans MS";
background: transparent;
border: 0px;
}

QLineEdit {
background: #434343;
border: 1px solid #c2c2c2;
border-radius: 4px;
height: 35px;
weight: 100px;
color: #757575;
font-size: 18px;
font-weight: 400px;
}

QLabel {
color: #757575;
background: none;
}

QPushButton {
background: #325698;
border: 0px;
border-radius: 4px;
width: 100%;
border: 0;
padding: 10px 10px;
color: #ffffff;
font: 10pt "Arial";
font-weight: bold;
}

QPushButton:hover {
background: #1d3259;
color: #ffffff;
}"""

