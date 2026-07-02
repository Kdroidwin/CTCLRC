# CTCLRC

CTCLRC は、以下の2つのファイルから **LRC 歌詞タイミングファイル** を生成する Windows デスクトップアプリです。

- 音声ファイル
- 完全で正しい歌詞が記載された `.txt` ファイル

本アプリは **CTC Forced Alignment** を使用します。

歌詞テキストを正解データとして扱い、各歌詞行のタイムスタンプを推定します。

---

# エンドユーザー向け

パッケージ化された Windows アプリを使用します。

1. `CTCLRC.exe` を起動します。
2. 音声ファイルを選択します。
3. 歌詞の `.txt` ファイルを選択します。
4. 日本語の楽曲の場合は、言語を **Japanese (jpn)** のままにします。
5. **Generate LRC** をクリックします。

生成された `.lrc` ファイルは、音声ファイルと同じフォルダーに保存されます。

---

# 配布時の重要事項

ビルドには、**単一実行ファイル（One-File）** 用の PyInstaller スペックを使用します。

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm CTCLRC.spec
```

出力先：

```text
dist\CTCLRC.exe
```

生成されるのは単一の実行ファイルです。

ユーザーは `CTCLRC.exe` を任意のフォルダーへ移動して、そのまま実行できます。

---

# アラインメントモデル

本アプリでは以下を使用します。

- `ctc-forced-aligner`
- `MahmoudAshraf/mms-300m-1130-forced-aligner`

モデルが同梱されていない場合は、初回実行時に Hugging Face から自動的にダウンロードされ、その後はローカルキャッシュが再利用されます。

完全オフラインで動作する EXE を作成する場合は、ビルド前にダウンロード済みモデルを次の場所へ配置してください。

```text
models/mms-300m-1130-forced-aligner/
```

`CTCLRC.spec` は、この `models/` フォルダーが存在する場合、自動的にアプリへ同梱します。

また、アプリは EXE と同じ場所にある以下のフォルダーも確認します。

```text
models/mms-300m-1130-forced-aligner/
```

---

# Windows でのビルド

依存ライブラリをインストールします。

```powershell
cd C:\Users\owner\Downloads\WhisperLRC
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

ローカルに `ctc-forced-aligner` の ZIP ファイルがある場合：

```powershell
.\.venv\Scripts\python.exe -m pip install C:\Users\owner\Downloads\ctc-forced-aligner-main.zip
```

ビルド：

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm CTCLRC.spec
```

出力：

```text
dist\CTCLRC.exe
```

---

# （任意）オフライン用モデルのダウンロード

```powershell
huggingface-cli download MahmoudAshraf/mms-300m-1130-forced-aligner --local-dir models\mms-300m-1130-forced-aligner
```

---

# ソースコード配布

ソースコード配布には、以下を含めないでください。

- `.venv`
- `build`
- `dist`
- 生成された `.lrc` ファイル
- モデルファイル
- 著作権で保護された音声ファイル

以下を実行します。

```powershell
.\make_source_zip.ps1
```

すると、以下の ZIP ファイルが作成されます。

```text
CTCLRC-source.zip
```
