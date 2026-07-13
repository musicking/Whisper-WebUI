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

    assert [item.text for item in result] == phrases
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


def test_pipeline_parameter_list_round_trip_includes_subtitles():
    params = TranscriptionPipelineParams(
        subtitle=SubtitleParams(max_line_width=18, pause_threshold=0.4)
    )

    restored = TranscriptionPipelineParams.from_list(params.to_list())

    assert restored == params
