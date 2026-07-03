# CTCLRC

[日本語版 README](README-ja.md)

CTCLRC is a Windows desktop application that generates **LRC lyric timing files** from the following two inputs:

* An audio file
* A complete and accurate lyrics `.txt` file

The application uses **CTC Forced Alignment**.

The lyrics text is treated as the ground truth, and the application estimates timestamps for each lyric line.

---

## For End Users

Use the packaged Windows application:

1. Run `CTCLRC.exe`.
2. Select an audio file.
3. Select a lyrics `.txt` file.
4. For Japanese songs, leave the language set to **Japanese (jpn)**.
5. Click **Generate LRC**.

The generated `.lrc` file is saved in the same folder as the audio file.

---

## System Requirements

### Minimum Requirements
These specifications are sufficient to run the application using CPU inference.

| Component | Minimum |
|----------|---------|
| OS | Windows 10 (64-bit) |
| CPU | Intel Core i5 (8th Gen) / AMD Ryzen 5 2600 or equivalent |
| Memory | 8 GB RAM |
| Storage | 2 GB available SSD space |
| GPU | Not required |

### Recommended Requirements
For faster alignment and smoother operation.

| Component | Recommended |
|----------|-------------|
| OS | Windows 10/11 (64-bit) |
| CPU | Intel Core i5-12400 / AMD Ryzen 5 5600 or better |
| Memory | 16 GB RAM |
| Storage | NVMe SSD |
| GPU | NVIDIA GPU with CUDA support (6 GB+ VRAM, e.g. GTX 1660 or RTX 3050+) |

### Notes

- CPU-only inference is fully supported.
- When a CUDA-compatible NVIDIA GPU is available, alignment is significantly faster.
- The first launch downloads the alignment model (approximately 1–2 GB depending on the model format) unless it is bundled with the application.
- Longer audio files require proportionally more processing time.

---


## Important Distribution Notes

Builds should use the **single-file (One-File)** PyInstaller specification:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm CTCLRC.spec
```

Output:

```text
dist\CTCLRC.exe
```

The generated executable is a single standalone file.

Users can move `CTCLRC.exe` to any folder and run it directly.

---

## Alignment Model

The application uses the following components:

* `ctc-forced-aligner`
* `MahmoudAshraf/mms-300m-1130-forced-aligner`

If the model is not bundled, the application automatically downloads it from Hugging Face during the first run and reuses the local cache afterward.

To create a fully offline executable, place the downloaded model in the following location before building:

```text
models/mms-300m-1130-forced-aligner/
```

If the `models/` directory exists, `CTCLRC.spec` automatically bundles it into the application.

The application also checks for the following directory next to the executable at runtime:

```text
models/mms-300m-1130-forced-aligner/
```

---

## Building on Windows

### Install Dependencies

Run the following command from the project root directory:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If you have a local copy of the `ctc-forced-aligner` ZIP package:

```powershell
.\.venv\Scripts\python.exe -m pip install path\to\ctc-forced-aligner-main.zip
```

### Build

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm CTCLRC.spec
```

Output:

```text
dist\CTCLRC.exe
```

---

## Optional Offline Model Download

```powershell
huggingface-cli download MahmoudAshraf/mms-300m-1130-forced-aligner --local-dir models\mms-300m-1130-forced-aligner
```

---

## Source Distribution

When distributing the source code, do not include the following:

* `.venv`
* `build`
* `dist`
* Generated `.lrc` files
* Model files
* Copyrighted audio files

Run:

```powershell
.\make_source_zip.ps1
```

This creates:

```text
CTCLRC-source.zip
```
