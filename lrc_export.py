# lrc_export.py

from pathlib import Path


# --------------------------------------------------------
# Time Format
# --------------------------------------------------------

def time_to_lrc(seconds: float) -> str:
    """
    秒 -> LRC時間形式

    65.43
        ↓
    [01:05.43]
    """

    if seconds is None:
        seconds = 0.0

    minutes = int(seconds // 60)
    sec = seconds % 60

    return f"[{minutes:02d}:{sec:05.2f}]"


# --------------------------------------------------------
# Export Line LRC
# --------------------------------------------------------

def export_line_lrc(lines, output_file):

    with open(output_file, "w", encoding="utf-8") as f:

        for line in lines:

            timestamp = time_to_lrc(line["start"])

            lyric = line["lyric"]

            f.write(f"{timestamp}{lyric}\n")


# --------------------------------------------------------
# Export Word LRC
# --------------------------------------------------------

def export_word_lrc(lines, output_file):

    with open(output_file, "w", encoding="utf-8") as f:

        for line in lines:

            words = line.get("words", [])

            if not words:
                continue

            output = ""

            for word in words:

                start = word.get("start", 0)

                text = word.get("text", "")

                output += f"<{start:.2f}>{text}"

            f.write(output + "\n")


# --------------------------------------------------------
# Save
# --------------------------------------------------------

def save_lrc(
    audio_file,
    line_result,
    word_result,
    line_mode=True,
    word_mode=False,
):

    base = Path(audio_file).with_suffix("")

    if line_mode:

        output = str(base) + ".lrc"

        export_line_lrc(
            line_result,
            output
        )

        print("Saved:", output)

    if word_mode:

        output = str(base) + "_word.lrc"

        export_word_lrc(
            word_result,
            output
        )

        print("Saved:", output)