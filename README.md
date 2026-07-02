# CTCLRC
<br>[日本語](https://github.com/Kdroidwin/CTCLRC/blob/main/README-ja.md) </br>
<br> </br>
CTCLRC is a Windows desktop app that creates LRC lyric timing files from:

- an audio file
- a complete correct lyrics `.txt` file

It uses CTC forced alignment. The lyrics text is treated as the correct answer, and the app estimates timestamps for each lyric line.

## For End Users

Use the packaged Windows app:

1. Run `CTCLRC.exe`.
2. Select an audio file.
3. Select a lyrics `.txt` file.
4. Keep language as `Japanese (jpn)` for Japanese songs.
5. Click `Generate LRC`.

The `.lrc` file is saved next to the audio file.

## Important For Distribution

Builds should use the one-file PyInstaller spec:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm CTCLRC.spec
```

The output is:

```text
dist\CTCLRC.exe
```

This is a single executable. Users can move `CTCLRC.exe` to another folder and run it.

## Alignment Model

The app uses:

- `ctc-forced-aligner`
- `MahmoudAshraf/mms-300m-1130-forced-aligner`

If the model is not bundled, the app will download it from Hugging Face on first use and then reuse the local cache.

For a fully offline EXE, put the downloaded model here before building:

```text
models/mms-300m-1130-forced-aligner/
```

`CTCLRC.spec` automatically bundles `models/` when that folder exists.

The app also checks for this folder next to the EXE:

```text
models/mms-300m-1130-forced-aligner/
```

## Build On Windows

Install dependencies:

```powershell
cd C:\Users\owner\Downloads\WhisperLRC
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If you have the local ctc-forced-aligner zip:

```powershell
.\.venv\Scripts\python.exe -m pip install C:\Users\owner\Downloads\ctc-forced-aligner-main.zip
```

Build:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm CTCLRC.spec
```

Output:

```text
dist\CTCLRC.exe
```

## Optional Offline Model Download

```powershell
huggingface-cli download MahmoudAshraf/mms-300m-1130-forced-aligner --local-dir models\mms-300m-1130-forced-aligner
```

## Source Release

Do not include `.venv`, `build`, `dist`, generated `.lrc`, model files, or copyrighted audio files in the source release.

Use:

```powershell
.\make_source_zip.ps1
```

This creates:

```text
CTCLRC-source.zip
```
