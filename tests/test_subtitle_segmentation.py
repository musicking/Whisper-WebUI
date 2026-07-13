from modules.utils.subtitle_manager import split_segments_for_subtitles
from modules.whisper.data_classes import Segment, SubtitleParams, TranscriptionPipelineParams, Word


def make_word(start: float, end: float, text: str) -> Word:
    return Word(start=start, end=end, word=text, probability=1.0)


def test_splits_chinese_subtitles_on_punctuation_and_pause():
    phrases = [
        "\u5927\u5bb6\u597d\uff0c",
        "\u4eca\u5929\u662f\u5468\u4e00\uff0c",
        "\u4e03\u6708\u5341\u4e09\u65e5\uff0c",
        "\u5e02\u573a\u5373\u5c06\u8fdb\u5165\u65b0\u4e00\u8f6e\u8d22\u62a5\u5b63",
    ]
    segment = Segment(
        start=0.24,
        end=5.919,
        text="".join(phrases),
        words=[
            make_word(0.24, 0.64, phrases[0]),
            make_word(0.96, 2.08, phrases[1]),
            make_word(2.16, 3.20, phrases[2]),
            make_word(3.359, 5.919, phrases[3]),
        ],
    )

    result = split_segments_for_subtitles(segments=[segment], params=SubtitleParams())

    assert [item.text for item in result] == [phrase.rstrip("\uff0c") for phrase in phrases]
    assert [(item.start, item.end) for item in result] == [
        (0.24, 0.64),
        (0.96, 2.08),
        (2.16, 3.20),
        (3.359, 5.919),
    ]


def test_splits_by_width_when_punctuation_is_missing():
    segment = Segment(
        start=0,
        end=2,
        text="abcdefghijkl",
        words=[
            make_word(0, 1, "abcdef"),
            make_word(1, 2, "ghijkl"),
        ],
    )
    params = SubtitleParams(
        max_line_width=8,
        max_line_count=1,
        pause_threshold=None,
        max_segment_duration=None,
        split_on_punctuation=False,
    )

    result = split_segments_for_subtitles([segment], params)

    assert [item.text for item in result] == ["abcdef", "ghijkl"]


def test_keeps_decimal_percentage_together_across_timed_words():
    prefix = "\u9053\u743c\u5de5\u4e1a\u6307\u6570\u4e0a\u6da80."
    following = "\u6807\u666e500\u4e0a\u6da80."
    segment = Segment(
        start=8.58,
        end=13.34,
        text=prefix + "3%," + following + "4%,",
        words=[
            make_word(8.58, 10.28, prefix),
            make_word(10.66, 11.02, "3%,"),
            make_word(11.02, 12.60, following),
            make_word(12.96, 13.34, "4%,"),
        ],
    )

    result = split_segments_for_subtitles([segment], SubtitleParams())

    assert [item.text for item in result] == [prefix + "3%", following + "4%"]
    assert [(item.start, item.end) for item in result] == [
        (8.58, 11.02),
        (11.02, 13.34),
    ]


def test_keeps_grouped_number_together_before_splitting():
    segment = Segment(
        start=0,
        end=2,
        text="Revenue 1,000, next",
        words=[
            make_word(0, 0.8, "Revenue 1,"),
            make_word(1.2, 1.5, "000,"),
            make_word(1.5, 2, " next"),
        ],
    )

    result = split_segments_for_subtitles([segment], SubtitleParams())

    assert [item.text for item in result] == ["Revenue 1,000", "next"]


def test_pipeline_parameter_list_round_trip_includes_subtitles():
    params = TranscriptionPipelineParams(
        subtitle=SubtitleParams(max_line_width=18, pause_threshold=0.4)
    )

    restored = TranscriptionPipelineParams.from_list(params.to_list())

    assert restored == params
