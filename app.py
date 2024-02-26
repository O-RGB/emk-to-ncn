import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QLineEdit, QVBoxLayout, QFileDialog, QMessageBox, QCheckBox

from lib.EMKDecoder import EMKDecoder

class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.button_top = QPushButton('Select EMK File')
        self.button_bottom = QPushButton('Convert to NCN')
        self.button_bottom.setEnabled(False) 

        self.input_text = QLineEdit()
        self.input_text.setDisabled(True)  
        self.checkbox = QCheckBox('UTF-8')  
        self.checkbox.setDisabled(True) 
        self.checkbox.setChecked(True)

        self.button_top.clicked.connect(self.show_dialog)
        self.button_bottom.clicked.connect(self.convert_to_ncn)

        hbox_top = QHBoxLayout()
        hbox_top.addWidget(self.button_top)
        hbox_top.addWidget(self.input_text)

        hbox_bottom = QHBoxLayout()
        hbox_bottom.addWidget(self.button_bottom)
        hbox_bottom.addWidget(self.checkbox)  

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_top)
        vbox.addLayout(hbox_bottom)

        self.setLayout(vbox)

        self.setWindowTitle('EMK TO NCN')
        self.setGeometry(100, 100, 400, 100)

        self.show()

    def show_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open .emk file', '', 'EMK Files (*.emk);;All Files (*)', options=options)
        if file_name:
            self.input_text.setText(file_name)
            self.button_bottom.setEnabled(True)  
            self.checkbox.setEnabled(True) 

    def convert_to_ncn(self):
        emk_file = self.input_text.text()
        options = QFileDialog.Options()
        folder = QFileDialog.getExistingDirectory(self, 'Select folder to save NCN file', options=options)

        if folder:
            EMK = EMKDecoder(emk_file, folder)
            if self.checkbox.isChecked():
                EMK.setEncodeText()

            magic = EMK.getMagicError()
            if not magic:
                QMessageBox.critical(self, 'Conversion Failed', f'Conversion failed.')
                return None

            result = EMK.decodeEmk()
            if result:
                QMessageBox.information(self, 'Conversion Complete', f'Conversion complete.')
            else:
                QMessageBox.critical(self, 'Conversion Failed', f'Conversion failed.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    custom_widget = CustomWidget()
    sys.exit(app.exec_())
