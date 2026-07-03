import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from ui import MainWindow
from align import generate_lrc


def language_code(label: str) -> str:
    if "(" in label and ")" in label:
        return label.rsplit("(", 1)[1].split(")", 1)[0].strip()
    return "jpn"


class App:
    def __init__(self):
        self.window = MainWindow()
        self.window.start_button.clicked.connect(self.start_generate)

    def start_generate(self):
        audio = self.window.audio_edit.text().strip()
        lyrics = self.window.lyrics_edit.text().strip()

        if not Path(audio).exists():
            QMessageBox.warning(self.window, "Error", "Audio file was not found.")
            return

        if not Path(lyrics).exists():
            QMessageBox.warning(self.window, "Error", "Lyrics file was not found.")
            return

        language = language_code(self.window.language_combo.currentText())
        lead_in = float(self.window.lead_in_spin.value())

        self.window.clear_log()
        self.window.append_log("===== CTCLRC =====")
        self.window.append_log(f"Audio : {audio}")
        self.window.append_log(f"Lyrics: {lyrics}")
        self.window.append_log(f"Lang  : {language}")
        self.window.append_log(f"Lead  : {lead_in:.2f}s")
        self.window.append_log("")

        try:
            self.window.set_progress(10)

            generate_lrc(
                audio,
                lyrics,
                language=language,
                lead_in=lead_in,
                line_mode=self.window.line_checkbox.isChecked(),
                word_mode=self.window.word_checkbox.isChecked(),
            )

            self.window.set_progress(100)
            self.window.append_log("LRC generated.")
            QMessageBox.information(self.window, "Finished", "LRC file was generated.")

        except Exception:
            tb = traceback.format_exc()
            print(tb)
            QMessageBox.critical(self.window, "Error", tb)


def main():
    app = QApplication(sys.argv)
    controller = App()
    controller.window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
