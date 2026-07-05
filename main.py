import sys
import traceback
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication, QMessageBox

from ui import MainWindow
from align import generate_lrc


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


def language_code(label: str) -> str:
    if "(" in label and ")" in label:
        return label.rsplit("(", 1)[1].split(")", 1)[0].strip()
    return "jpn"


class GenerateWorker(QObject):
    progress = Signal(int)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, audio, lyrics, language, lead_in, line_mode, word_mode):
        super().__init__()
        self.audio = audio
        self.lyrics = lyrics
        self.language = language
        self.lead_in = lead_in
        self.line_mode = line_mode
        self.word_mode = word_mode

    @Slot()
    def run(self):
        try:
            generate_lrc(
                self.audio,
                self.lyrics,
                language=self.language,
                lead_in=self.lead_in,
                line_mode=self.line_mode,
                word_mode=self.word_mode,
                progress_callback=self.progress.emit,
            )
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())


class App:
    def __init__(self):
        self.window = MainWindow()
        self.window.start_button.clicked.connect(self.start_generate)
        self.thread = None
        self.worker = None

    def start_generate(self):
        audio = self.window.audio_edit.text().strip()
        lyrics = self.window.lyrics_edit.text().strip()

        if not Path(audio).exists():
            QMessageBox.warning(self.window, "Error", "Audio file was not found.")
            return

        if not Path(lyrics).exists():
            QMessageBox.warning(self.window, "Error", "Lyrics file was not found.")
            return

        language = self.window.language_combo.currentData() or language_code(
            self.window.language_combo.currentText()
        )
        lead_in = float(self.window.lead_in_spin.value())
        self.window.save_settings()

        self.window.clear_log()
        self.window.append_log("===== CTCLRC =====")
        self.window.append_log(f"Audio : {audio}")
        self.window.append_log(f"Lyrics: {lyrics}")
        self.window.append_log(f"Lang  : {language}")
        self.window.append_log(f"Lead  : {lead_in:.2f}s")
        self.window.append_log("")

        self.window.start_button.setEnabled(False)
        self.window.set_progress(1)

        self.thread = QThread()
        self.worker = GenerateWorker(
            audio,
            lyrics,
            language,
            lead_in,
            self.window.line_checkbox.isChecked(),
            self.window.word_checkbox.isChecked(),
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.window.set_progress)
        self.worker.finished.connect(self.generate_finished)
        self.worker.failed.connect(self.generate_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.clear_worker_refs)
        self.thread.start()

    @Slot()
    def generate_finished(self):
        self.window.set_progress(100)
        self.window.start_button.setEnabled(True)
        self.window.append_log("LRC generated.")
        QMessageBox.information(self.window, "Finished", "LRC file was generated.")

    @Slot(str)
    def generate_failed(self, traceback_text):
        print(traceback_text)
        self.window.start_button.setEnabled(True)
        QMessageBox.critical(self.window, "Error", traceback_text)

    @Slot()
    def clear_worker_refs(self):
        self.thread = None
        self.worker = None


def main():
    app = QApplication(sys.argv)
    icon_path = resource_path("assets/ctclrc.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    controller = App()
    if icon_path.exists():
        controller.window.setWindowIcon(QIcon(str(icon_path)))
    controller.window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
