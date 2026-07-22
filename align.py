import gc
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "2")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import av
import numpy as np
import torch

from lrc_export import save_lrc


APP_NAME = "CTCLRC"
SAMPLE_RATE = 16000
DEFAULT_LANGUAGE = "jpn"
CTC_ALIGNMENT_MODEL = "MahmoudAshraf/mms-300m-1130-forced-aligner"
LOCAL_CTC_MODEL_DIR = "models/mms-300m-1130-forced-aligner"
DEFAULT_LRC_LEAD_IN_SEC = 0.345
CPU_THREADS = 2


if torch.cuda.is_available():
    DEVICE = "cuda"
else:
    DEVICE = "cpu"
    torch.set_num_threads(CPU_THREADS)
    torch.set_num_interop_threads(1)


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
    APP_DIR = BASE_DIR


@dataclass(frozen=True)
class AlignmentBundle:
    model: Any
    tokenizer: Any
    dtype: Any
    model_path: str


def get_ctc_alignment_model_path() -> str:
    for base_dir in (APP_DIR, BASE_DIR):
        local_model = base_dir / LOCAL_CTC_MODEL_DIR
        if local_model.exists():
            return str(local_model)
    return CTC_ALIGNMENT_MODEL


def load_alignment_bundle() -> AlignmentBundle:
    try:
        from ctc_forced_aligner import load_alignment_model
    except ImportError as exc:
        raise RuntimeError(
            "ctc-forced-aligner is not installed. Install it with requirements.txt first."
        ) from exc

    dtype = torch.float16 if DEVICE == "cuda" else torch.float32
    model_path = get_ctc_alignment_model_path()
    print(f"Loading CTC model: {model_path}")
    print(f"Device: {DEVICE}")
    model, tokenizer = load_alignment_model(
        DEVICE,
        model_path,
        None,
        dtype,
    )
    return AlignmentBundle(model=model, tokenizer=tokenizer, dtype=dtype, model_path=model_path)


def load_lyrics(path: str) -> list[str]:
    lines, _ = load_lyrics_with_sections(path)
    return lines


def load_lyrics_with_sections(path: str, keep_sections: bool = True) -> tuple[list[str], list[int]]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return parse_lyrics_text(f.read(), keep_sections=keep_sections)


def load_lyrics_text(text: str, keep_sections: bool = True) -> tuple[list[str], list[int]]:
    return parse_lyrics_text(text, keep_sections=keep_sections)


def parse_lyrics_text(text: str, keep_sections: bool = True) -> tuple[list[str], list[int]]:
    lines: list[str] = []
    section_breaks: set[int] = set()
    pending_section_break = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if keep_sections and lines:
                pending_section_break = True
            continue

        if keep_sections and pending_section_break and lines:
            section_breaks.add(len(lines) - 1)
            pending_section_break = False

        lines.append(line)

    return lines, sorted(section_breaks) if keep_sections else []


def resolve_lyrics_source(
    audio_file: str | Path,
    lyric_file: str | Path | None = None,
    lyric_text: str | None = None,
    keep_sections: bool = True,
) -> tuple[list[str], list[int]]:
    if lyric_text is not None and lyric_text.strip():
        return load_lyrics_text(lyric_text, keep_sections=keep_sections)

    if lyric_file:
        lyric_path = Path(lyric_file)
        if lyric_path.exists():
            return load_lyrics_with_sections(str(lyric_path), keep_sections=keep_sections)

    audio_path = Path(audio_file)
    candidate = audio_path.with_suffix(".txt")
    if candidate.exists():
        return load_lyrics_with_sections(str(candidate), keep_sections=keep_sections)

    raise FileNotFoundError(
        "Lyrics were not provided. Supply a lyrics file, paste lyrics text, or place a .txt file next to the audio."
    )


def decode_audio(audio_path: str) -> np.ndarray:
    resampler = av.audio.resampler.AudioResampler(
        format="s16",
        layout="mono",
        rate=SAMPLE_RATE,
    )

    chunks = []
    with av.open(audio_path, mode="r", metadata_errors="ignore") as container:
        for frame in container.decode(audio=0):
            for resampled in resampler.resample(frame):
                chunks.append(resampled.to_ndarray().reshape(-1))

        for resampled in resampler.resample(None):
            chunks.append(resampled.to_ndarray().reshape(-1))

    if not chunks:
        raise ValueError(f"No audio stream found: {audio_path}")

    audio_i16 = np.concatenate(chunks).astype(np.int16, copy=False)
    return audio_i16.astype(np.float32) / 32768.0


def normalize_text(text: str) -> str:
    remove_chars = {
        " ",
        "\t",
        "\u3000",
        "\n",
        "\r",
        ",",
        ".",
        "!",
        "?",
        "！",
        "？",
        "、",
        "。",
        "・",
        "…",
        "「",
        "」",
        "『",
        "』",
        "(",
        ")",
        "（",
        "）",
        "[",
        "]",
        "【",
        "】",
        '"',
        "'",
        ":",
        ";",
        "：",
        "；",
    }
    return "".join(ch for ch in text.strip() if ch not in remove_chars)


def average_ctc_score(items: list[dict]) -> float:
    scores = [float(item.get("score", 0.0)) for item in items]
    if not scores:
        return 0.0
    return round(max(0.0, sum(scores) / len(scores)), 1)


def distribute_chars(chars: list[str], start: float, end: float) -> list[dict]:
    if not chars:
        return []

    if end <= start:
        end = start + 0.05 * len(chars)

    span = end - start
    return [
        {
            "text": char,
            "start": start + span * index / len(chars),
            "end": start + span * (index + 1) / len(chars),
        }
        for index, char in enumerate(chars)
    ]


def enforce_monotonic_times(line_result: list[dict], word_result: list[dict]) -> None:
    previous = 0.0

    for line, words in zip(line_result, word_result):
        start = max(float(line["start"]), previous)
        end = max(float(line["end"]), start + 0.05)

        line["start"] = start
        line["end"] = end
        words["start"] = start
        words["end"] = end
        previous = start + 0.02


def apply_lrc_lead_in(line_result: list[dict], word_result: list[dict], seconds: float) -> None:
    if seconds <= 0:
        return

    for line, words in zip(line_result, word_result):
        line["start"] = max(0.0, float(line["start"]) - seconds)
        line["end"] = max(line["start"] + 0.05, float(line["end"]) - seconds)
        words["start"] = line["start"]
        words["end"] = line["end"]

        for word in words.get("words", []):
            word["start"] = max(0.0, float(word.get("start", 0.0)) - seconds)
            word["end"] = max(
                word["start"] + 0.01,
                float(word.get("end", word["start"])) - seconds,
            )


def ctc_align_lyrics(
    audio: np.ndarray,
    lyrics: list[str],
    language: str,
    lead_in: float,
    bundle: AlignmentBundle | None = None,
) -> tuple[list[dict], list[dict]]:
    try:
        from ctc_forced_aligner import (
            generate_emissions,
            get_alignments,
            get_spans,
            postprocess_results,
            preprocess_text,
        )
    except ImportError as exc:
        raise RuntimeError(
            "ctc-forced-aligner is not installed. Install it with requirements.txt first."
        ) from exc

    owned_bundle = bundle is None
    if bundle is None:
        bundle = load_alignment_bundle()

    prepared_lines = [normalize_text(line) for line in lyrics]
    full_text = "".join(prepared_lines)
    if not full_text:
        raise ValueError("Lyrics contain no alignable text.")

    print(f"Language: {language}")

    try:
        audio_waveform = torch.as_tensor(audio, dtype=bundle.dtype, device=DEVICE)
        emissions, stride = generate_emissions(
            bundle.model,
            audio_waveform,
            window_length=20,
            context_length=2,
            batch_size=1,
        )

        tokens_starred, text_starred = preprocess_text(
            full_text,
            romanize=True,
            language=language,
            split_size="char",
            star_frequency="edges",
        )

        segments, scores, blank_token = get_alignments(
            emissions,
            tokens_starred,
            bundle.tokenizer,
        )
        spans = get_spans(tokens_starred, segments, blank_token)
        char_results = postprocess_results(
            text_starred,
            spans,
            stride,
            scores,
            merge_threshold=0.0,
        )
    finally:
        if owned_bundle:
            del bundle
            gc.collect()
            if DEVICE == "cuda":
                torch.cuda.empty_cache()

    line_result = []
    word_result = []
    cursor = 0

    for lyric, prepared in zip(lyrics, prepared_lines):
        count = len(prepared)
        chars = char_results[cursor:cursor + count]
        cursor += count

        timed_chars = [
            item for item in chars
            if item.get("start") is not None and item.get("end") is not None
        ]

        if timed_chars:
            start = float(timed_chars[0]["start"])
            end = float(timed_chars[-1]["end"])
            score = average_ctc_score(timed_chars)
        else:
            start = 0.0 if not line_result else line_result[-1]["end"]
            end = start + 0.05 * max(count, 1)
            score = 0.0

        words = [
            {
                "text": prepared[index],
                "start": float(item.get("start", start)),
                "end": float(item.get("end", end)),
            }
            for index, item in enumerate(chars[:count])
            if index < len(prepared)
        ]

        if not words:
            words = distribute_chars(list(prepared), start, end)

        line_result.append(
            {
                "lyric": lyric,
                "recognized": "",
                "start": start,
                "end": max(end, start + 0.05),
                "score": score,
            }
        )
        word_result.append(
            {
                "lyric": lyric,
                "start": start,
                "end": max(end, start + 0.05),
                "words": words,
            }
        )

    enforce_monotonic_times(line_result, word_result)
    apply_lrc_lead_in(line_result, word_result, lead_in)
    return line_result, word_result


def annotate_section_breaks(lines: list[dict], break_after_indices: list[int] | None) -> None:
    if not break_after_indices:
        return
    breaks = set(break_after_indices)
    for index, item in enumerate(lines):
        if index in breaks:
            item["section_break_after"] = True


def print_line_alignment(lines: list[dict]) -> None:
    print()
    print("=" * 60)
    print("Line Alignment")
    print("=" * 60)

    for item in lines:
        print(f"[{item['start']:.2f}] {item['lyric']}")
        if item.get("section_break_after"):
            print()


def print_word_alignment(lines: list[dict]) -> None:
    print()
    print("=" * 60)
    print("Word Alignment")
    print("=" * 60)

    for line in lines:
        print()
        print(line["lyric"])
        for word in line["words"]:
            print(f"    {word['start']:.2f}  {word['text']}")


def generate_lrc(
    audio_file,
    lyric_file=None,
    lyric_text=None,
    model=None,
    language=DEFAULT_LANGUAGE,
    lead_in=DEFAULT_LRC_LEAD_IN_SEC,
    line_mode=True,
    word_mode=False,
    output_path=None,
    progress_callback=None,
    keep_sections=True,
):
    print("=" * 60)
    print(APP_NAME)
    print("=" * 60)

    audio_file = Path(audio_file)
    if not audio_file.exists():
        raise FileNotFoundError(audio_file)

    if progress_callback:
        progress_callback(5)

    print("Load lyrics...")
    lyrics, section_breaks = resolve_lyrics_source(audio_file, lyric_file, lyric_text, keep_sections=keep_sections)
    if not lyrics:
        raise ValueError("Lyrics are empty.")
    print(f"{len(lyrics)} lyric lines")
    if progress_callback:
        progress_callback(15)

    print("Load audio...")
    audio = decode_audio(str(audio_file))
    if progress_callback:
        progress_callback(30)

    print("CTC forced alignment...")
    bundle = model if isinstance(model, AlignmentBundle) else None
    line_result, word_result = ctc_align_lyrics(audio, lyrics, language, lead_in, bundle=bundle)
    annotate_section_breaks(line_result, section_breaks)
    annotate_section_breaks(word_result, section_breaks)
    print(f"LRC lead-in: -{lead_in:.2f}s")
    if progress_callback:
        progress_callback(90)

    print_line_alignment(line_result)
    if word_mode:
        print_word_alignment(word_result)

    save_lrc(
        str(audio_file),
        line_result,
        word_result,
        line_mode=line_mode,
        word_mode=word_mode,
        output_path=output_path,
    )
    if progress_callback:
        progress_callback(100)

    print()
    print("Done.")

    return {
        "lines": line_result,
        "words": word_result,
    }


if __name__ == "__main__":
    generate_lrc(
        "song.flac",
        "lyrics.txt",
        language=DEFAULT_LANGUAGE,
        line_mode=True,
        word_mode=False,
    )
