import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtCore import QObject, QThread, Signal, Slot, QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from ui import MainWindow
from align import generate_lrc, load_alignment_bundle


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path


@dataclass
class GenerateJob:
    audio: str
    lyrics_file: str | None = None
    lyrics_text: str | None = None
    output_path: str | None = None


class GenerateWorker(QObject):
    progress = Signal(int)
    message = Signal(str)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, jobs, language, lead_in, line_mode, word_mode, keep_sections):
        super().__init__()
        self.jobs = jobs
        self.language = language
        self.lead_in = lead_in
        self.line_mode = line_mode
        self.word_mode = word_mode
        self.keep_sections = keep_sections

    @Slot()
    def run(self):
        try:
            if not self.jobs:
                raise ValueError("No jobs to process.")

            bundle = load_alignment_bundle()
            total = len(self.jobs)

            for index, job in enumerate(self.jobs):
                audio = job.audio
                self.message.emit(f"[{index + 1}/{total}] {Path(audio).name}")

                def emit_progress(local_pct):
                    overall = int(((index + max(0, min(100, int(local_pct))) / 100.0) / total) * 100)
                    self.progress.emit(max(0, min(100, overall)))

                generate_lrc(
                    audio,
                    job.lyrics_file,
                    job.lyrics_text,
                    model=bundle,
                    language=self.language,
                    lead_in=self.lead_in,
                    line_mode=self.line_mode,
                    word_mode=self.word_mode,
                    output_path=job.output_path,
                    progress_callback=emit_progress,
                    keep_sections=self.keep_sections,
                )

            self.progress.emit(100)
            self.finished.emit()
        except Exception:
            self.failed.emit(traceback.format_exc())


class App(QObject):
    def __init__(self):
        super().__init__()
        self.window = MainWindow()
        self.window.generate_button.clicked.connect(self.start_generate)
        if hasattr(self.window, "batch_generate_button"):
            self.window.batch_generate_button.clicked.connect(self.start_generate)
        self.thread = None
        self.worker = None

    def _language_code(self) -> str:
        return self.window.language_combo.currentData() or "jpn"

    def _set_generate_enabled(self, enabled: bool):
        self.window.generate_button.setEnabled(enabled)
        if hasattr(self.window, "batch_generate_button"):
            self.window.batch_generate_button.setEnabled(enabled)

    def _build_jobs(self):
        if self.window.ui_mode == "advanced":
            jobs = []
            for job in self.window.collect_batch_jobs():
                jobs.append(
                    GenerateJob(
                        audio=job["audio"],
                        lyrics_file=job["lyrics_file"],
                        lyrics_text=job["lyrics_text"],
                        output_path=job["output_path"],
                    )
                )
            return jobs

        job = self.window.collect_simple_job()
        return [
            GenerateJob(
                audio=job["audio"],
                lyrics_file=job["lyrics_file"],
                lyrics_text=job["lyrics_text"],
                output_path=job["output_path"],
            )
        ]

    def _validate_jobs(self, jobs):
        for job in jobs:
            if not job.audio or not Path(job.audio).exists():
                raise FileNotFoundError(f"Audio file was not found: {job.audio}")
            if job.lyrics_file and not Path(job.lyrics_file).exists():
                raise FileNotFoundError(f"Lyrics file was not found: {job.lyrics_file}")
            if job.output_path:
                out_dir = Path(job.output_path).parent
                out_dir.mkdir(parents=True, exist_ok=True)

    def start_generate(self):
        try:
            jobs = self._build_jobs()
            self._validate_jobs(jobs)
        except Exception as exc:
            QMessageBox.warning(self.window, "Error", str(exc))
            return

        language = self._language_code()
        lead_in = float(self.window.lead_in_spin.value())
        line_mode = self.window.line_checkbox.isChecked()
        word_mode = self.window.word_checkbox.isChecked()
        keep_sections = self.window.section_checkbox.isChecked()
        self.window.save_settings()

        self.window.clear_log()
        self.window.append_log("===== CTCLRC =====")
        self.window.append_log(f"Mode  : {self.window.ui_mode}")
        self.window.append_log(f"Jobs  : {len(jobs)}")
        self.window.append_log(f"Lang  : {language}")
        self.window.append_log(f"Lead  : {lead_in:.3f}s")
        self.window.append_log(f"Line  : {line_mode}")
        self.window.append_log(f"Chars : {word_mode}")
        self.window.append_log(f"Sec   : {keep_sections}")
        self.window.append_log("")

        for index, job in enumerate(jobs, start=1):
            self.window.append_log(f"{index}. {job.audio}")
            if job.lyrics_text:
                self.window.append_log("   lyrics: <pasted text>")
            else:
                self.window.append_log(f"   lyrics: {job.lyrics_file or '<auto .txt>'}")
            if job.output_path:
                self.window.append_log(f"   out   : {job.output_path}")
        self.window.append_log("")

        self._set_generate_enabled(False)
        self.window.set_progress(1)

        self.thread = QThread()
        self.worker = GenerateWorker(
            jobs,
            language,
            lead_in,
            line_mode,
            word_mode,
            keep_sections,
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.window.set_progress)
        self.worker.message.connect(self.window.append_log)
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
        self._set_generate_enabled(True)
        self.window.append_log("LRC generated.")
        QTimer.singleShot(0, lambda: QMessageBox.information(self.window, "Finished", "LRC file was generated."))

    @Slot(str)
    def generate_failed(self, traceback_text):
        print(traceback_text)
        self._set_generate_enabled(True)
        QTimer.singleShot(0, lambda: QMessageBox.critical(self.window, "Error", traceback_text))

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
