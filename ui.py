from PySide6.QtCore import QSettings
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
    QDoubleSpinBox,
    QDialog,
    QDialogButtonBox,
    QToolButton,
)


DEFAULT_LEAD_IN = 0.345

AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
    ".opus",
}

TEXT_EXTENSIONS = {".txt"}

LANGUAGE_ITEMS = [
    ("Japanese (jpn)", "jpn"),
    ("English (eng)", "eng"),
    ("Korean (kor)", "kor"),
    ("Chinese Mandarin (cmn)", "cmn"),
    ("Spanish (spa)", "spa"),
]

UI_TEXT = {
    "en": {
        "audio": "Audio",
        "lyrics": "Lyrics",
        "browse": "Browse",
        "language": "Lyrics language",
        "lead": "Lead-in seconds",
        "line": "Line LRC",
        "chars": "Character timing LRC",
        "generate": "Generate LRC",
        "progress": "Progress",
        "log": "Log",
        "settings": "Settings",
        "ui_language": "UI language",
    },
    "ja": {
        "audio": "音声",
        "lyrics": "歌詞",
        "browse": "参照",
        "language": "歌詞の言語",
        "lead": "先出し秒数",
        "line": "行単位LRC",
        "chars": "文字単位LRC",
        "generate": "LRC生成",
        "progress": "進捗",
        "log": "ログ",
        "settings": "設定",
        "ui_language": "UI言語",
    },
}


def code_from_label(label: str) -> str:
    if "(" in label and ")" in label:
        return label.rsplit("(", 1)[1].split(")", 1)[0].strip()
    return "jpn"


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


class SettingsDialog(QDialog):
    def __init__(self, parent, ui_language: str):
        super().__init__(parent)
        self.setWindowTitle(parent.text("settings"))

        layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel(parent.text("ui_language")))

        self.ui_language_combo = QComboBox()
        self.ui_language_combo.addItem("English", "en")
        self.ui_language_combo.addItem("日本語", "ja")
        index = self.ui_language_combo.findData(ui_language)
        self.ui_language_combo.setCurrentIndex(max(index, 0))
        row.addWidget(self.ui_language_combo)
        layout.addLayout(row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def selected_ui_language(self) -> str:
        return self.ui_language_combo.currentData()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("CTCLRC", "CTCLRC")
        self.ui_language = self.settings.value("ui_language", "en")
        self.setAcceptDrops(True)
        self.setWindowTitle("CTCLRC")
        self.resize(760, 540)
        self.init_ui()
        self.load_settings()
        self.apply_ui_language()

    def init_ui(self):
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.settings_button = QToolButton()
        self.settings_button.setText("⚙")
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        top_layout.addWidget(self.settings_button)
        layout.addLayout(top_layout)

        audio_layout = QHBoxLayout()
        self.audio_label = QLabel()
        audio_layout.addWidget(self.audio_label)
        self.audio_edit = DropLineEdit()
        self.audio_button = QPushButton()
        self.audio_button.clicked.connect(self.select_audio)
        audio_layout.addWidget(self.audio_edit)
        audio_layout.addWidget(self.audio_button)
        layout.addLayout(audio_layout)

        lyric_layout = QHBoxLayout()
        self.lyrics_label = QLabel()
        lyric_layout.addWidget(self.lyrics_label)
        self.lyrics_edit = DropLineEdit()
        self.lyrics_button = QPushButton()
        self.lyrics_button.clicked.connect(self.select_lyrics)
        lyric_layout.addWidget(self.lyrics_edit)
        lyric_layout.addWidget(self.lyrics_button)
        layout.addLayout(lyric_layout)

        language_layout = QHBoxLayout()
        self.language_label = QLabel()
        language_layout.addWidget(self.language_label)
        self.language_combo = QComboBox()
        for label, code in LANGUAGE_ITEMS:
            self.language_combo.addItem(label, code)
        language_layout.addWidget(self.language_combo)
        layout.addLayout(language_layout)

        lead_layout = QHBoxLayout()
        self.lead_label = QLabel()
        lead_layout.addWidget(self.lead_label)
        self.lead_in_spin = QDoubleSpinBox()
        self.lead_in_spin.setRange(0.0, 2.0)
        self.lead_in_spin.setSingleStep(0.005)
        self.lead_in_spin.setDecimals(3)
        self.lead_in_spin.setValue(DEFAULT_LEAD_IN)
        self.lead_in_spin.setSuffix(" s")
        lead_layout.addWidget(self.lead_in_spin)
        layout.addLayout(lead_layout)

        self.line_checkbox = QCheckBox()
        self.line_checkbox.setChecked(True)
        self.word_checkbox = QCheckBox()
        layout.addWidget(self.line_checkbox)
        layout.addWidget(self.word_checkbox)

        self.start_button = QPushButton()
        self.start_button.setMinimumHeight(40)
        layout.addWidget(self.start_button)

        self.progress_label = QLabel()
        layout.addWidget(self.progress_label)

        self.log_label = QLabel()
        layout.addWidget(self.log_label)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.setLayout(layout)

    def text(self, key: str) -> str:
        return UI_TEXT.get(self.ui_language, UI_TEXT["en"])[key]

    def apply_ui_language(self):
        self.audio_label.setText(self.text("audio"))
        self.lyrics_label.setText(self.text("lyrics"))
        self.audio_button.setText(self.text("browse"))
        self.lyrics_button.setText(self.text("browse"))
        self.language_label.setText(self.text("language"))
        self.lead_label.setText(self.text("lead"))
        self.line_checkbox.setText(self.text("line"))
        self.word_checkbox.setText(self.text("chars"))
        self.start_button.setText(self.text("generate"))
        self.log_label.setText(self.text("log"))
        self.settings_button.setToolTip(self.text("settings"))
        self.set_progress(self.current_progress)

    def load_settings(self):
        self.current_progress = 0
        lead_in = self.settings.value("lead_in", DEFAULT_LEAD_IN, type=float)
        self.lead_in_spin.setValue(lead_in)

        language_code = self.settings.value("lyrics_language", "jpn")
        index = self.language_combo.findData(language_code)
        self.language_combo.setCurrentIndex(max(index, 0))

        line_mode = self.settings.value("line_mode", True, type=bool)
        word_mode = self.settings.value("word_mode", False, type=bool)
        self.line_checkbox.setChecked(line_mode)
        self.word_checkbox.setChecked(word_mode)

    def save_settings(self):
        self.settings.setValue("ui_language", self.ui_language)
        self.settings.setValue("lead_in", self.lead_in_spin.value())
        self.settings.setValue("lyrics_language", self.language_combo.currentData())
        self.settings.setValue("line_mode", self.line_checkbox.isChecked())
        self.settings.setValue("word_mode", self.word_checkbox.isChecked())

    def open_settings(self):
        dialog = SettingsDialog(self, self.ui_language)
        if dialog.exec() == QDialog.Accepted:
            self.ui_language = dialog.selected_ui_language()
            self.apply_ui_language()
            self.save_settings()

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            suffix = path.lower().rsplit(".", 1)[-1]
            suffix = f".{suffix}" if suffix else ""
            if suffix in AUDIO_EXTENSIONS:
                self.audio_edit.setText(path)
            elif suffix in TEXT_EXTENSIONS:
                self.lyrics_edit.setText(path)

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def append_log(self, text):
        self.log.append(text)

    def clear_log(self):
        self.log.clear()

    def set_progress(self, value):
        self.current_progress = int(value)
        self.progress_label.setText(f"{self.text('progress')} : {self.current_progress}%")
