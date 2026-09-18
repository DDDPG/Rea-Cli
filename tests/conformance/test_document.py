import pytest
from reaper_parser import parse, emit, RPPParseError

SESSION = """<REAPER_PROJECT 0.1 7.48 1
  <TRACK {track}
    NAME "Original"
    VOLPAN 1 0 -1 -1 1
    <FXCHAIN
      BYPASS 0 0 0
      <JS first ""
        AAAAAA==
      >
      WAK 0 0
      BYPASS 0 0 0
      <JS second ""
      >
      WET 0.8
      WAK 0 0
    >
    <ITEM
      POSITION 0
      LENGTH 1
      IGUID {item}
      NAME "First"
      GUID {take1}
      <SOURCE WAVE
        FILE "first.wav"
      >
      TAKE SEL
      GUID {take2}
      <SOURCE WAVE
        FILE "second.wav"
      >
    >
    <FUTURE opaque
      DATA 1 2 3
      DATA 4 5
    >
  >
>
"""


def test_fx_missing_field_persists_in_owner_and_saved_document(tmp_path):
    doc = parse(SESSION)
    fx = doc.project.tracks[0].fx_chain.fxs[0]
    fx.wet = 0.25
    assert doc.project.tracks[0].fx_chain.fxs[0].wet == 0.25
    assert doc.project.tracks[0].fx_chain.fxs[1].wet == 0.8
    out = doc.save(tmp_path / "output.rpp")
    assert parse(out).project.tracks[0].fx_chain.fxs[0].wet == 0.25
    assert emit(doc).replace("      WET 0.25\n", "") == SESSION


def test_take_insert_targets_actual_range(tmp_path):
    doc = parse(SESSION)
    takes = doc.project.tracks[0].items[0].takes
    assert [t.selected for t in takes] == [False, True]
    takes[1].name = "Second"
    saved = parse(doc.text()).project.tracks[0].items[0].takes
    assert [t.name for t in saved] == ["First", "Second"]
    assert saved[1].source.file_path == "second.wav"


def test_rac_patch_and_object_views_share_one_document():
    compat = pytest.importorskip("rac.rpp")
    from rac.rpp import patch

    assert compat.parse is parse
    doc = parse(SESSION)
    view = doc.project.tracks[0]
    patch.set_track_name(doc, doc.tracks()[0], "Changed")
    assert view.name == "Changed"
    view.volume = 0.5
    assert doc.tracks()[0].find_line("VOLPAN").values[0] == "0.5"


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"])
def test_endings_bom_and_no_final_newline(ending):
    src = "\ufeff" + SESSION.rstrip("\n").replace("\n", ending)
    doc = parse(src)
    assert doc.text() == src
    doc.project.tracks[0].name = "Changed"
    assert doc.text() == src.replace('NAME "Original"', "NAME Changed")


def test_mixed_endings_unchanged_outside_patch():
    src = SESSION.replace('NAME "Original"\n', 'NAME "Original"\r\n')
    doc = parse(src)
    doc.project.tracks[0].name = "Changed"
    assert doc.text() == src.replace('NAME "Original"', "NAME Changed")


def test_invalid_utf8_and_opaque_bytes_preserved(tmp_path):
    src = SESSION.encode().replace(b"AAAAAA==", b"ABC\xff==")
    p = tmp_path / "input.rpp"
    p.write_bytes(src)
    doc = parse(p)
    doc.project.tracks[0].name = "Changed"
    doc.save(tmp_path / "out.rpp")
    assert (tmp_path / "out.rpp").read_bytes() == src.replace(
        b'NAME "Original"', b"NAME Changed"
    )


def test_save_refuses_overwrite(tmp_path):
    doc = parse(SESSION)
    p = doc.save(tmp_path / "out.rpp")
    with pytest.raises(FileExistsError):
        doc.save(p)
    doc.save(p, overwrite=True)


def test_repeat_unknown_fields_stay_accessible():
    doc = parse(SESSION)
    node = doc.tracks()[0].find_chunk("FUTURE")
    assert [r.values for r in node.find_lines("DATA")] == [["1", "2", "3"], ["4", "5"]]
    assert doc.text() == SESSION


def test_typed_writes_do_not_invent_contracts():
    with pytest.raises(ValueError, match="verified write contract"):
        parse(SESSION).project.set_field("GROUPOVERRIDE", 1, 2)


def test_confirmed_field_metadata_and_raw_unknown():
    doc = parse(
        "<REAPER_PROJECT 0.1 7.48 1\nRENDER_RANGE 2 1.25 2.5 0 1000\nNEW_FLAG abc\n>\n"
    )
    fields = list(doc.project.fields())
    start = next(f for f in fields if f.token == "RENDER_RANGE" and f.index == 2)
    assert start.value == 1.25 and start.semantic_status == "confirmed"
    assert next(f for f in fields if f.token == "NEW_FLAG").value == "abc"


def test_backtick_tokens_and_notes_payload():
    doc = parse(
        '<REAPER_PROJECT 0.1 7.48 1\nTITLE `a "title"`\n<NOTES\n|text "unclosed\n>\n>\n'
    )
    assert doc.root.find_line("TITLE").values == ['a "title"']
    assert doc.text().count("unclosed") == 1


def test_range_deletion_does_not_remove_adjacent_fx():
    doc = parse(SESSION)
    doc.project.tracks[0].fx_chain.fxs[0].remove()
    remaining = parse(doc.text()).project.tracks[0].fx_chain.fxs
    assert len(remaining) == 1 and remaining[0].plugin.attrs[0] == "second"


def test_nested_source_midi_and_envelopes():
    src = "<REAPER_PROJECT 0.1 7.48 1\n<TRACK\n<VOLENV2\nPT 0 .5 0\n>\n<ITEM\n<SOURCE SECTION\n<SOURCE MIDI\nHASDATA 1 960 QN\ne 0 90 3c 7f\nE 960 80 3c 00\n>\n>\n>\n>\n>\n"
    track = parse(src).project.tracks[0]
    assert len(track.envelopes[0].points) == 1
    assert len(track.items[0].takes[0].source.sources[0].events) == 2


@pytest.mark.parametrize(
    "src", ["<REAPER_PROJECT_BAD 1\n>\n", "<REAPER_PROJECT 1\n<TRACK\n"]
)
def test_invalid_structure_errors(src):
    with pytest.raises(RPPParseError):
        parse(src)


@pytest.mark.parametrize(
    "value",
    [
        "C:" + chr(92) + "audio" + chr(92),
        'say "hello"',
        "both ' and \" here",
        "back`tick",
    ],
)
def test_native_quote_delimiters_and_trailing_backslash(value):
    from reaper_parser.parser import quote_value, tokenize

    assert tokenize("FILE " + quote_value(value) + ' "next"') == ["FILE", value, "next"]
    doc = parse(SESSION)
    doc.project.tracks[0].name = value
    assert parse(doc.text()).project.tracks[0].name == value


def test_fx_range_removal_preserves_chain_trailing_unknown_state():
    src = SESSION.replace(
        "      WET 0.8\n      WAK 0 0",
        "      WET 0.8\n      WAK 0 0\n      FUTURE_CHAIN_SETTING 7",
    )
    doc = parse(src)
    doc.project.tracks[0].fx_chain.fxs[-1].remove()
    assert "FUTURE_CHAIN_SETTING 7" in doc.text()
    assert len(parse(doc.text()).project.tracks[0].fx_chain.fxs) == 1


def test_take_removal_does_not_delete_item_geometry():
    doc = parse(SESSION)
    with pytest.raises(ValueError, match="host operation"):
        doc.project.tracks[0].items[0].takes[0].remove()
    assert doc.text() == SESSION
