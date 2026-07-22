from pathlib import Path
from PySide6.QtCore import QSettings, Qt
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
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QFormLayout,
    QAbstractItemView,
    QSizePolicy,
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
        "audio": "Audio file",
        "lyrics_file": "Lyrics file",
        "lyrics_text": "Paste lyrics here",
        "browse": "Browse",
        "clear": "Clear",
        "language": "Lyrics language",
        "lead": "Lead-in seconds",
        "line": "Line LRC",
        "chars": "Character timing LRC",
        "sections": "Keep blank lines as sections",
        "generate": "Generate LRC",
        "progress": "Progress",
        "log": "Log",
        "settings": "Settings",
        "ui_language": "UI language",
        "ui_mode": "UI mode",
        "simple_mode": "Simple",
        "advanced_mode": "Advanced",
        "input_mode": "Input mode",
        "file_input": "Lyrics file",
        "paste_input": "Paste lyrics",
        "mode_simple": "Simple mode",
        "mode_advanced": "Advanced mode",
        "audio_list": "Audio files",
        "lyrics_list": "Lyrics files",
        "add_files": "Add files",
        "remove": "Remove selected",
        "clear_list": "Clear list",
        "pairing": "Pairing rule",
        "pair_by_name": "Match by file name",
        "pair_by_order": "Match by order",
        "output_dir": "Output directory",
        "preview": "Preview",
        "choose_output_dir": "Browse",
        "simple_hint": "Paste lyrics to skip the txt file. Blank lines can be preserved as section breaks.",
        "batch_hint": "Select multiple audio and lyrics files, then pair them by name or order.",
        "batch_lyrics": "Lyrics for selected audio",
        "batch_lyrics_hint": "Select an audio row, paste lyrics for that row, and the pasted text will override any file for that job.",
        "save_pasted": "Save pasted lyrics",
        "clear_pasted": "Clear pasted lyrics",
        "pasted_status": "Pasted lyrics",
        "lyrics_placeholder": "Paste lyrics here",
        "batch_lyrics_placeholder": "Paste lyrics for the selected audio item.",
    },
    "ja": {
        "audio": "音声ファイル",
        "lyrics_file": "歌詞ファイル",
        "lyrics_text": "歌詞を貼り付け",
        "browse": "参照",
        "clear": "クリア",
        "language": "歌詞の言語",
        "lead": "先出し秒数",
        "line": "行単位LRC",
        "chars": "文字単位LRC",
        "sections": "空行を分節として保持",
        "generate": "LRC生成",
        "progress": "進捗",
        "log": "ログ",
        "settings": "設定",
        "ui_language": "UI言語",
        "ui_mode": "UIモード",
        "simple_mode": "シンプル",
        "advanced_mode": "拡張",
        "input_mode": "入力方式",
        "file_input": "歌詞ファイル",
        "paste_input": "歌詞貼り付け",
        "mode_simple": "シンプルモード",
        "mode_advanced": "拡張モード",
        "audio_list": "音声ファイル",
        "lyrics_list": "歌詞ファイル",
        "add_files": "ファイル追加",
        "remove": "選択を削除",
        "clear_list": "全削除",
        "pairing": "対応付けルール",
        "pair_by_name": "ファイル名で一致",
        "pair_by_order": "順番で一致",
        "output_dir": "出力先フォルダ",
        "preview": "プレビュー",
        "choose_output_dir": "参照",
        "simple_hint": "歌詞を貼り付ければ txt は不要です。空行は分節として保持できます。",
        "batch_hint": "複数の音声と歌詞を選び、名前か順番で対応付けます。",
        "batch_lyrics": "選択中の音声の歌詞",
        "batch_lyrics_hint": "音声を1つ選んで、その行専用の歌詞を貼り付けます。貼り付けた内容はそのジョブではファイルより優先されます。",
        "save_pasted": "貼り付けを保存",
        "clear_pasted": "貼り付けを消去",
        "pasted_status": "貼り付け歌詞",
        "lyrics_placeholder": "ここに歌詞を貼り付け",
        "batch_lyrics_placeholder": "選択した音声用の歌詞を貼り付け",
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


class CurrentPageStackedWidget(QStackedWidget):
    def sizeHint(self):
        widget = self.currentWidget()
        if widget is not None:
            return widget.sizeHint()
        return super().sizeHint()

    def minimumSizeHint(self):
        widget = self.currentWidget()
        if widget is not None:
            return widget.minimumSizeHint()
        return super().minimumSizeHint()

class SettingsDialog(QDialog):
    def __init__(self, parent, ui_language: str, ui_mode: str):
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
        row = QHBoxLayout()
        row.addWidget(QLabel(parent.text("ui_mode")))
        self.ui_mode_combo = QComboBox()
        self.ui_mode_combo.addItem(parent.text("simple_mode"), "simple")
        self.ui_mode_combo.addItem(parent.text("advanced_mode"), "advanced")
        index = self.ui_mode_combo.findData(ui_mode)
        self.ui_mode_combo.setCurrentIndex(max(index, 0))
        row.addWidget(self.ui_mode_combo)
        layout.addLayout(row)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)
    def selected_ui_language(self) -> str:
        return self.ui_language_combo.currentData()
    def selected_ui_mode(self) -> str:
        return self.ui_mode_combo.currentData()
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("CTCLRC", "CTCLRC")
        self.ui_language = self.settings.value("ui_language", "en")
        self.ui_mode = self.settings.value("ui_mode", "simple")
        self.setAcceptDrops(True)
        self.setWindowTitle("CTCLRC")
        self.resize(920, 720)
        self.init_ui()
        self.load_settings()
        self.apply_ui_language()
        self.apply_mode()
    def init_ui(self):
        outer = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        self.settings_button = QToolButton()
        self.settings_button.setText("⚙")
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        top_layout.addWidget(self.settings_button)
        outer.addLayout(top_layout)
        common_box = QGroupBox()
        common_layout = QFormLayout(common_box)
        self.language_label = QLabel()
        self.language_combo = QComboBox()
        for label, code in LANGUAGE_ITEMS:
            self.language_combo.addItem(label, code)
        common_layout.addRow(self.language_label, self.language_combo)
        self.lead_label = QLabel()
        self.lead_in_spin = QDoubleSpinBox()
        self.lead_in_spin.setRange(0.0, 2.0)
        self.lead_in_spin.setSingleStep(0.005)
        self.lead_in_spin.setDecimals(3)
        self.lead_in_spin.setValue(DEFAULT_LEAD_IN)
        self.lead_in_spin.setSuffix(" s")
        common_layout.addRow(self.lead_label, self.lead_in_spin)
        self.line_checkbox = QCheckBox()
        self.line_checkbox.setChecked(True)
        common_layout.addRow(self.line_checkbox)
        self.word_checkbox = QCheckBox()
        common_layout.addRow(self.word_checkbox)
        self.section_checkbox = QCheckBox()
        self.section_checkbox.setChecked(True)
        common_layout.addRow(self.section_checkbox)
        outer.addWidget(common_box)
        self.stack = CurrentPageStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.simple_page = self._build_simple_page()
        self.advanced_page = self._build_advanced_page()
        self.stack.addWidget(self.simple_page)
        self.stack.addWidget(self.advanced_page)
        outer.addWidget(self.stack)
        self.progress_label = QLabel()
        outer.addWidget(self.progress_label)
        self.log_label = QLabel()
        outer.addWidget(self.log_label)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        outer.addWidget(self.log, 1)
        self.setLayout(outer)
    def _build_simple_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        audio_layout = QHBoxLayout()
        self.audio_label = QLabel()
        audio_layout.addWidget(self.audio_label)
        self.audio_edit = DropLineEdit()
        self.audio_button = QPushButton()
        self.audio_button.clicked.connect(self.select_audio)
        audio_layout.addWidget(self.audio_edit, 1)
        audio_layout.addWidget(self.audio_button)
        layout.addLayout(audio_layout)
        lyric_layout = QHBoxLayout()
        self.lyrics_label = QLabel()
        lyric_layout.addWidget(self.lyrics_label)
        self.lyrics_edit = DropLineEdit()
        self.lyrics_button = QPushButton()
        self.lyrics_button.clicked.connect(self.select_lyrics)
        lyric_layout.addWidget(self.lyrics_edit, 1)
        lyric_layout.addWidget(self.lyrics_button)
        layout.addLayout(lyric_layout)
        self.generate_button = QPushButton()
        self.generate_button.setMinimumHeight(42)
        layout.addWidget(self.generate_button)
        self.lyrics_text_label = QLabel()
        layout.addWidget(self.lyrics_text_label)
        self.lyrics_text_edit = QTextEdit()
        self.lyrics_text_edit.setPlaceholderText(self.text("lyrics_placeholder"))
        self.lyrics_text_edit.setMaximumHeight(140)
        layout.addWidget(self.lyrics_text_edit)
        self.simple_hint_label = QLabel()
        self.simple_hint_label.setWordWrap(True)
        layout.addWidget(self.simple_hint_label)
        return page
    def _build_list_section(self, title_key: str, add_slot, remove_slot, clear_slot):
        box = QGroupBox()
        box_layout = QVBoxLayout(box)
        title = QLabel()
        title.setObjectName(title_key)
        box_layout.addWidget(title)
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        box_layout.addWidget(list_widget, 1)
        buttons = QHBoxLayout()
        add_button = QPushButton()
        add_button.clicked.connect(add_slot)
        buttons.addWidget(add_button)
        remove_button = QPushButton()
        remove_button.clicked.connect(remove_slot)
        buttons.addWidget(remove_button)
        clear_button = QPushButton()
        clear_button.clicked.connect(clear_slot)
        buttons.addWidget(clear_button)
        buttons.addStretch()
        box_layout.addLayout(buttons)
        return box, title, list_widget, add_button, remove_button, clear_button
    def _build_advanced_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.audio_box, self.audio_list_title, self.audio_list, self.audio_add_button, self.audio_remove_button, self.audio_clear_button = self._build_list_section(
            "audio_list",
            self.add_audio_files,
            self.remove_selected_audio,
            self.clear_audio_files,
        )
        layout.addWidget(self.audio_box, 1)
        self.lyrics_box, self.lyrics_list_title, self.lyrics_list, self.lyrics_add_button, self.lyrics_remove_button, self.lyrics_clear_button = self._build_list_section(
            "lyrics_list",
            self.add_lyrics_files,
            self.remove_selected_lyrics,
            self.clear_lyrics_files,
        )
        layout.addWidget(self.lyrics_box, 1)
        pair_row = QHBoxLayout()
        self.pairing_label = QLabel()
        pair_row.addWidget(self.pairing_label)
        self.pairing_combo = QComboBox()
        self.pairing_combo.addItem("Match by file name", "name")
        self.pairing_combo.addItem("Match by order", "order")
        self.pairing_combo.currentIndexChanged.connect(self.update_batch_preview)
        pair_row.addWidget(self.pairing_combo, 1)
        layout.addLayout(pair_row)
        output_row = QHBoxLayout()
        self.output_dir_label = QLabel()
        output_row.addWidget(self.output_dir_label)
        self.output_dir_edit = DropLineEdit()
        self.output_dir_edit.textChanged.connect(self.update_batch_preview)
        output_row.addWidget(self.output_dir_edit, 1)
        self.output_dir_button = QPushButton()
        self.output_dir_button.clicked.connect(self.select_output_dir)
        output_row.addWidget(self.output_dir_button)
        layout.addLayout(output_row)
        self.batch_generate_button = QPushButton()
        self.batch_generate_button.setMinimumHeight(42)
        layout.addWidget(self.batch_generate_button)
        self.batch_lyrics_box = QGroupBox()
        batch_lyrics_layout = QVBoxLayout(self.batch_lyrics_box)
        self.batch_lyrics_label = QLabel()
        batch_lyrics_layout.addWidget(self.batch_lyrics_label)
        self.batch_lyrics_edit = QTextEdit()
        self.batch_lyrics_edit.setAcceptRichText(False)
        self.batch_lyrics_edit.setPlaceholderText("Paste lyrics for the selected audio item.")
        self.batch_lyrics_edit.setMaximumHeight(140)
        self.batch_lyrics_edit.textChanged.connect(self._sync_batch_lyrics_to_current_item)
        batch_lyrics_layout.addWidget(self.batch_lyrics_edit)
        batch_lyrics_buttons = QHBoxLayout()
        self.batch_lyrics_save_button = QPushButton()
        self.batch_lyrics_save_button.clicked.connect(self._sync_batch_lyrics_to_current_item)
        batch_lyrics_buttons.addWidget(self.batch_lyrics_save_button)
        self.batch_lyrics_clear_button = QPushButton()
        self.batch_lyrics_clear_button.clicked.connect(self.clear_selected_batch_lyrics)
        batch_lyrics_buttons.addWidget(self.batch_lyrics_clear_button)
        batch_lyrics_buttons.addStretch()
        batch_lyrics_layout.addLayout(batch_lyrics_buttons)
        self.batch_lyrics_hint_label = QLabel()
        self.batch_lyrics_hint_label.setWordWrap(True)
        batch_lyrics_layout.addWidget(self.batch_lyrics_hint_label)
        layout.addWidget(self.batch_lyrics_box)
        self.batch_hint_label = QLabel()
        self.batch_hint_label.setWordWrap(True)
        layout.addWidget(self.batch_hint_label)
        self.preview_label = QLabel()
        layout.addWidget(self.preview_label)
        self.batch_preview = QTextEdit()
        self.batch_preview.setReadOnly(True)
        layout.addWidget(self.batch_preview, 1)
        self.audio_list.itemSelectionChanged.connect(self.update_batch_preview)
        self.audio_list.currentItemChanged.connect(self._load_batch_lyrics_for_current_audio)
        self.audio_list.model().rowsInserted.connect(self.update_batch_preview)
        self.audio_list.model().rowsRemoved.connect(self.update_batch_preview)
        self.lyrics_list.itemSelectionChanged.connect(self.update_batch_preview)
        self.lyrics_list.model().rowsInserted.connect(self.update_batch_preview)
        self.lyrics_list.model().rowsRemoved.connect(self.update_batch_preview)
        return page
    def text(self, key: str) -> str:
        return UI_TEXT.get(self.ui_language, UI_TEXT["en"])[key]
    def apply_ui_language(self):
        texts = UI_TEXT.get(self.ui_language, UI_TEXT["en"])
        self.language_label.setText(texts["language"])
        self.lead_label.setText(texts["lead"])
        self.audio_label.setText(texts["audio"])
        self.lyrics_label.setText(texts["lyrics_file"])
        self.audio_button.setText(texts["browse"])
        self.lyrics_button.setText(texts["browse"])
        self.lyrics_text_label.setText(texts["paste_input"])
        self.simple_hint_label.setText(texts["simple_hint"])
        self.language_combo.setToolTip(texts["language"])
        self.section_checkbox.setText(texts["sections"])
        self.line_checkbox.setText(texts["line"])
        self.word_checkbox.setText(texts["chars"])
        self.generate_button.setText(texts["generate"])
        self.batch_generate_button.setText(texts["generate"])
        self.log_label.setText(texts["log"])
        self.progress_label.setText(f"{texts['progress']} : {getattr(self, 'current_progress', 0)}%")
        self.settings_button.setToolTip(texts["settings"])
        self.audio_list_title.setText(texts["audio_list"])
        self.lyrics_list_title.setText(texts["lyrics_list"])
        self.audio_add_button.setText(texts["add_files"])
        self.audio_remove_button.setText(texts["remove"])
        self.audio_clear_button.setText(texts["clear_list"])
        self.lyrics_add_button.setText(texts["add_files"])
        self.lyrics_remove_button.setText(texts["remove"])
        self.lyrics_clear_button.setText(texts["clear_list"])
        self.pairing_label.setText(texts["pairing"])
        self.output_dir_label.setText(texts["output_dir"])
        self.output_dir_button.setText(texts["choose_output_dir"])
        self.batch_lyrics_label.setText(texts["batch_lyrics"])
        self.batch_lyrics_save_button.setText(texts["save_pasted"])
        self.batch_lyrics_clear_button.setText(texts["clear_pasted"])
        self.batch_lyrics_hint_label.setText(texts["batch_lyrics_hint"])
        self.batch_lyrics_edit.setPlaceholderText(texts["batch_lyrics_placeholder"])
        self.preview_label.setText(texts["preview"])
        self.batch_hint_label.setText(texts["batch_hint"])
        self.lyrics_text_edit.setPlaceholderText(texts["lyrics_placeholder"])
        current_pair = self.pairing_combo.currentData() or "name"
        self.pairing_combo.blockSignals(True)
        self.pairing_combo.clear()
        self.pairing_combo.addItem(texts["pair_by_name"], "name")
        self.pairing_combo.addItem(texts["pair_by_order"], "order")
        idx = self.pairing_combo.findData(current_pair)
        if idx >= 0:
            self.pairing_combo.setCurrentIndex(idx)
        self.pairing_combo.blockSignals(False)
        self.set_progress(getattr(self, "current_progress", 0))
        self.update_batch_preview()
    def apply_mode(self):
        self.stack.setCurrentIndex(0 if self.ui_mode == "simple" else 1)
        self.stack.updateGeometry()
        self.updateGeometry()
        self.update_batch_preview()
    def load_settings(self):
        self.current_progress = 0
        self.lead_in_spin.setValue(self.settings.value("lead_in", DEFAULT_LEAD_IN, type=float))
        language_code = self.settings.value("lyrics_language", "jpn")
        index = self.language_combo.findData(language_code)
        self.language_combo.setCurrentIndex(max(index, 0))
        self.line_checkbox.setChecked(self.settings.value("line_mode", True, type=bool))
        self.word_checkbox.setChecked(self.settings.value("word_mode", False, type=bool))
        self.section_checkbox.setChecked(self.settings.value("keep_sections", True, type=bool))
        self.ui_language = self.settings.value("ui_language", self.ui_language)
        self.ui_mode = self.settings.value("ui_mode", self.ui_mode)
        self.audio_edit.setText(self.settings.value("audio_file", ""))
        self.lyrics_edit.setText(self.settings.value("lyrics_file", ""))
        self.lyrics_text_edit.setPlainText(self.settings.value("lyrics_text", ""))
        self.output_dir_edit.setText(self.settings.value("output_dir", ""))
    def save_settings(self):
        self.settings.setValue("ui_language", self.ui_language)
        self.settings.setValue("ui_mode", self.ui_mode)
        self.settings.setValue("lead_in", self.lead_in_spin.value())
        self.settings.setValue("lyrics_language", self.language_combo.currentData())
        self.settings.setValue("line_mode", self.line_checkbox.isChecked())
        self.settings.setValue("word_mode", self.word_checkbox.isChecked())
        self.settings.setValue("keep_sections", self.section_checkbox.isChecked())
        self.settings.setValue("audio_file", self.audio_edit.text())
        self.settings.setValue("lyrics_file", self.lyrics_edit.text())
        self.settings.setValue("lyrics_text", self.lyrics_text_edit.toPlainText())
        self.settings.setValue("output_dir", self.output_dir_edit.text())
    def open_settings(self):
        dialog = SettingsDialog(self, self.ui_language, self.ui_mode)
        if dialog.exec() == QDialog.Accepted:
            self.ui_language = dialog.selected_ui_language()
            self.ui_mode = dialog.selected_ui_mode()
            self.apply_ui_language()
            self.apply_mode()
            self.save_settings()
    def select_audio(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.text("audio"),
            "",
            "Audio (*.wav *.mp3 *.flac *.m4a *.aac *.ogg *.opus)",
        )
        if file:
            self.audio_edit.setText(file)
    def select_lyrics(self):
        file, _ = QFileDialog.getOpenFileName(
            self,
            self.text("lyrics_file"),
            "",
            "Text (*.txt)",
        )
        if file:
            self.lyrics_edit.setText(file)
    def add_audio_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.text("audio_list"),
            "",
            "Audio (*.wav *.mp3 *.flac *.m4a *.aac *.ogg *.opus)",
        )
        for file in files:
            self._add_list_item(self.audio_list, file)
        self.update_batch_preview()
    def add_lyrics_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.text("lyrics_list"),
            "",
            "Text (*.txt)",
        )
        for file in files:
            self._add_list_item(self.lyrics_list, file)
        self.update_batch_preview()
    def remove_selected_audio(self):
        self._remove_selected_items(self.audio_list)
        self.update_batch_preview()
    def remove_selected_lyrics(self):
        self._remove_selected_items(self.lyrics_list)
        self.update_batch_preview()
    def clear_audio_files(self):
        self.audio_list.clear()
        self.update_batch_preview()
    def clear_lyrics_files(self):
        self.lyrics_list.clear()
        self.update_batch_preview()
    def select_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            self.text("output_dir"),
            "",
        )
        if directory:
            self.output_dir_edit.setText(directory)
    def _add_list_item(self, list_widget: QListWidget, path: str):
        path = str(Path(path))
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == path:
                return
        item = QListWidgetItem(path)
        list_widget.addItem(item)
    def _remove_selected_items(self, list_widget: QListWidget):
        for item in list_widget.selectedItems():
            row = list_widget.row(item)
            list_widget.takeItem(row)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            suffix = path.lower().rsplit(".", 1)[-1]
            suffix = f".{suffix}" if suffix else ""
            if suffix in AUDIO_EXTENSIONS:
                if self.ui_mode == "advanced":
                    self._add_list_item(self.audio_list, path)
                else:
                    self.audio_edit.setText(path)
            elif suffix in TEXT_EXTENSIONS:
                if self.ui_mode == "advanced":
                    self._add_list_item(self.lyrics_list, path)
                else:
                    self.lyrics_edit.setText(path)
        self.update_batch_preview()
    def _collect_list_paths(self, list_widget: QListWidget) -> list[str]:
        return [list_widget.item(i).text() for i in range(list_widget.count())]
    def collect_simple_job(self):
        return {
            "audio": self.audio_edit.text().strip(),
            "lyrics_file": self.lyrics_edit.text().strip() or None,
            "lyrics_text": self.lyrics_text_edit.toPlainText().strip() or None,
            "output_path": None,
        }
    def _audio_item_lyrics_text(self, item) -> str | None:
        if item is None:
            return None
        data = item.data(Qt.UserRole)
        if data is None:
            return None
        text = str(data).strip()
        return text or None
    def collect_batch_jobs(self):
        audio_items = [self.audio_list.item(i) for i in range(self.audio_list.count())]
        lyric_paths = self._collect_list_paths(self.lyrics_list)
        pairing = self.pairing_combo.currentData() or "name"
        output_dir = self.output_dir_edit.text().strip() or None
        jobs = []
        if not audio_items:
            return jobs
        single_pair = len(audio_items) == 1 and len(lyric_paths) == 1
        lyric_by_stem = {}
        for lyric_path in lyric_paths:
            lyric_by_stem[Path(lyric_path).stem.lower()] = lyric_path
        for index, item in enumerate(audio_items):
            audio_path = item.text()
            lyrics_text = self._audio_item_lyrics_text(item)
            lyric_path = None
            if not lyrics_text:
                if pairing == "order":
                    lyric_path = lyric_paths[index] if index < len(lyric_paths) else None
                else:
                    lyric_path = lyric_by_stem.get(Path(audio_path).stem.lower())
                    if lyric_path is None and single_pair:
                        lyric_path = lyric_paths[0]
            jobs.append(self._make_job(audio_path, lyric_path, lyrics_text, output_dir))
        return jobs
    def _make_job(self, audio_path: str, lyric_path: str | None, lyrics_text: str | None, output_dir: str | None):
        output_path = None
        if output_dir:
            output_path = str(Path(output_dir) / Path(audio_path).stem)
        return {
            "audio": audio_path,
            "lyrics_file": lyric_path,
            "lyrics_text": lyrics_text,
            "output_path": output_path,
        }
    def _load_batch_lyrics_for_current_audio(self, current, previous=None):
        if getattr(self, "_batch_lyrics_syncing", False):
            return
        self._batch_lyrics_syncing = True
        try:
            text = ""
            if current is not None:
                text = self._audio_item_lyrics_text(current) or ""
            self.batch_lyrics_edit.blockSignals(True)
            self.batch_lyrics_edit.setPlainText(text)
            self.batch_lyrics_edit.blockSignals(False)
        finally:
            self._batch_lyrics_syncing = False
        self.update_batch_preview()
    def _sync_batch_lyrics_to_current_item(self, *args):
        if getattr(self, "_batch_lyrics_syncing", False):
            return
        item = self.audio_list.currentItem()
        if item is None:
            return
        text = self.batch_lyrics_edit.toPlainText().strip()
        item.setData(Qt.UserRole, text or None)
        item.setToolTip(text[:120].replace("\n", " "))
        self.update_batch_preview()
    def clear_selected_batch_lyrics(self, *args):
        item = self.audio_list.currentItem()
        self._batch_lyrics_syncing = True
        try:
            self.batch_lyrics_edit.blockSignals(True)
            self.batch_lyrics_edit.clear()
            self.batch_lyrics_edit.blockSignals(False)
            if item is not None:
                item.setData(Qt.UserRole, None)
                item.setToolTip("")
        finally:
            self._batch_lyrics_syncing = False
        self.update_batch_preview()
    def update_batch_preview(self):
        if not hasattr(self, "batch_preview"):
            return
        if self.ui_mode != "advanced":
            self.batch_preview.clear()
            return
        audio_paths = self._collect_list_paths(self.audio_list)
        lyric_paths = self._collect_list_paths(self.lyrics_list)
        pairing = self.pairing_combo.currentData() or "name"
        output_dir = self.output_dir_edit.text().strip()
        lines = []
        lines.append(f"Audio: {len(audio_paths)}")
        lines.append(f"Lyrics: {len(lyric_paths)}")
        lines.append(f"Pairing: {pairing}")
        if output_dir:
            lines.append(f"Output: {output_dir}")
        lines.append("")
        jobs = self.collect_batch_jobs()
        if not jobs:
            lines.append("No batch jobs.")
        else:
            for index, job in enumerate(jobs, start=1):
                if job["lyrics_text"]:
                    lyric_label = "<pasted text>"
                elif job["lyrics_file"]:
                    lyric_label = Path(job["lyrics_file"]).name
                else:
                    lyric_label = "<missing>"
                output_label = job["output_path"] or Path(job["audio"]).with_suffix("")
                lines.append(f"{index}. {Path(job['audio']).name} -> {lyric_label}")
                lines.append(f"   out: {output_label}")
                if job["lyrics_text"]:
                    lines.append("   source: pasted text")
                elif job["lyrics_file"] is None:
                    lines.append("   warning: lyrics not matched")
        self.batch_preview.setPlainText("\n".join(lines))
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
