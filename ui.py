from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QCheckBox,
)


class DropLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.setText(urls[0].toLocalFile())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CTCLRC")
        self.resize(720, 520)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        audio_layout = QHBoxLayout()
        audio_layout.addWidget(QLabel("Audio"))
        self.audio_edit = DropLineEdit()
        self.audio_button = QPushButton("Browse")
        self.audio_button.clicked.connect(self.select_audio)
        audio_layout.addWidget(self.audio_edit)
        audio_layout.addWidget(self.audio_button)
        layout.addLayout(audio_layout)

        lyric_layout = QHBoxLayout()
        lyric_layout.addWidget(QLabel("Lyrics"))
        self.lyrics_edit = DropLineEdit()
        self.lyrics_button = QPushButton("Browse")
        self.lyrics_button.clicked.connect(self.select_lyrics)
        lyric_layout.addWidget(self.lyrics_edit)
        lyric_layout.addWidget(self.lyrics_button)
        layout.addLayout(lyric_layout)

        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("Language"))
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "Japanese (jpn)",
            "English (eng)",
            "Korean (kor)",
            "Chinese Mandarin (cmn)",
            "Spanish (spa)",
        ])
        self.language_combo.setCurrentText("Japanese (jpn)")
        language_layout.addWidget(self.language_combo)
        layout.addLayout(language_layout)

        self.line_checkbox = QCheckBox("Line LRC")
        self.line_checkbox.setChecked(True)
        self.word_checkbox = QCheckBox("Character timing LRC")
        layout.addWidget(self.line_checkbox)
        layout.addWidget(self.word_checkbox)

        self.start_button = QPushButton("Generate LRC")
        self.start_button.setMinimumHeight(40)
        layout.addWidget(self.start_button)

        self.progress_label = QLabel("Progress : 0 %")
        layout.addWidget(self.progress_label)

        layout.addWidget(QLabel("Log"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.setLayout(layout)

    def select_audio(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Audio File",
            "",
            "Audio (*.wav *.mp3 *.flac *.m4a *.aac *.ogg *.opus)",
        )
        if file:
            self.audio_edit.setText(file)

    def select_lyrics(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Lyrics File",
            "",
            "Text (*.txt)",
        )
        if file:
            self.lyrics_edit.setText(file)

    def append_log(self, text):
        self.log.append(text)

    def clear_log(self):
        self.log.clear()

    def set_progress(self, value):
        self.progress_label.setText(f"Progress : {value}%")
