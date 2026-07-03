# CTCLRC

CTCLRC は、以下の 2 つのファイルから **LRC 歌詞タイミングファイル** を生成する Windows デスクトップアプリです。

* 音声ファイル
* 完全かつ正確な歌詞が記載された `.txt` ファイル

本アプリは **CTC Forced Alignment** を利用して、歌詞テキストを正解データとして扱い、各歌詞行のタイムスタンプを推定します。

---

# エンドユーザー向け

パッケージ化された Windows アプリを使用します。

1. `CTCLRC.exe` を起動します。
2. 音声ファイルを選択します。
3. 歌詞の `.txt` ファイルを選択します。
4. 日本語の楽曲の場合は、言語を **Japanese (jpn)** のままにします。
5. **Generate LRC** をクリックします。

生成された `.lrc` ファイルは、音声ファイルと同じフォルダーへ保存されます。

---

## 動作環境

### 最低動作環境
CPUのみで動作可能です。本当に最低動作レベルです。かなり厳しいです。

| 項目 | 最低要件 |
|------|---------|
| OS | Windows 10（64bit） |
| CPU | Intel Core i5（第8世代）または AMD Ryzen 5 2600 相当以上 |
| メモリ | 8 GB RAM |
| ストレージ | SSD 空き容量 2 GB以上 |
| GPU | 不要 |

### 推奨動作環境
より高速なアライメント処理を行う場合。

| 項目 | 推奨 |
|------|------|
| OS | Windows 10 / 11（64bit） |
| CPU | Intel Core i5-12400 / AMD Ryzen 5 5600 以上 |
| メモリ | 16 GB RAM |
| ストレージ | NVMe SSD |
| GPU | CUDA対応 NVIDIA GPU（VRAM 6 GB以上、GTX 1660・RTX 3050以上推奨） |

### 備考

- CPUのみでも問題なく動作します。
- CUDA対応GPUを利用するとアライメント処理が大幅に高速化されます。
- 初回起動時は、モデルを同梱していない場合のみ、約1～2GBのアライメントモデルを自動ダウンロードします。
- 音声ファイルが長いほど処理時間も長くなります。


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

ユーザーは `CTCLRC.exe` を任意のフォルダーへ移動し、そのまま実行できます。

---

# アラインメントモデル

本アプリでは以下を使用します。

* `ctc-forced-aligner`
* `MahmoudAshraf/mms-300m-1130-forced-aligner`

モデルが同梱されていない場合、初回実行時に Hugging Face から自動的にダウンロードされます。

ダウンロード済みモデルはローカルキャッシュに保存され、以降は再利用されます。

完全オフラインで動作する EXE を作成する場合は、ビルド前にダウンロード済みモデルを以下へ配置してください。

```text
models/mms-300m-1130-forced-aligner/
```

`CTCLRC.spec` は、この `models/` ディレクトリが存在する場合、自動的にアプリへ同梱します。

また、アプリ起動時には EXE と同じ場所に存在する以下のディレクトリも検索対象となります。

```text
models/mms-300m-1130-forced-aligner/
```

---

# Windows でのビルド

## 依存ライブラリのインストール

プロジェクトルートディレクトリで実行してください。

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

ローカルに `ctc-forced-aligner` の ZIP ファイルがある場合：

```powershell
.\.venv\Scripts\python.exe -m pip install path\to\ctc-forced-aligner-main.zip
```

## ビルド

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

ソースコード配布時には、以下を含めないでください。

* `.venv`
* `build`
* `dist`
* 生成された `.lrc` ファイル
* モデルファイル
* 著作権で保護された音声ファイル

以下を実行します。

```powershell
.\make_source_zip.ps1
```

すると、以下の ZIP ファイルが作成されます。

```text
CTCLRC-source.zip
```
