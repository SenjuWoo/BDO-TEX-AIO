#!/usr/bin/env python3
"""Self-checks for BodyMats' image path.

Run:  python test_body_mats.py     (no framework, plain asserts)
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image  # noqa: E402

import body_mats as bm  # noqa: E402
import dds  # noqa: E402


def _texture(size, alpha=True):
    w, h = size
    im = Image.new("RGBA", size)
    im.putdata([
        ((x * 7) % 256, (y * 5) % 256, (x ^ y) % 256,
         (0 if alpha and (x + y) % 5 == 0 else 255))
        for y in range(h) for x in range(w)
    ])
    return im


def test_blank_detection() -> None:
    assert bm.is_blank_rgb(Image.new("RGBA", (16, 16), (0, 0, 0, 0)))
    assert bm.is_blank_rgb(Image.new("RGBA", (16, 16), (0, 0, 0, 255)))
    assert not bm.is_blank_rgb(_texture((16, 16)))


def test_pack_without_texconv() -> None:
    """The addon must produce real DDS with no external tool installed."""
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        png = t / "a.png"
        _texture((128, 64)).save(png)
        for bc, fourcc in (("BC1_UNORM", "DXT1"), ("BC3_UNORM", "DXT5")):
            out = t / f"{bc}.dds"
            bm.pack_png_to_dds({"texconv": ""}, png, out, bc=bc)
            blob = out.read_bytes()
            h = dds.read_header(blob)
            assert h["fourcc"] == fourcc, h
            assert (h["width"], h["height"]) == (128, 64), h
            assert h["mip_count"] == len(dds.mip_dimensions(128, 64)), h
            assert not bm.is_blank_rgb(dds.to_image(blob))


def test_resize_preserves_aspect_and_alpha() -> None:
    """A non-square atlas must not be squashed into a square, and a cutout
    alpha must survive the trip (upscayl never sees the alpha channel)."""
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        src = t / "s.png"
        _texture((256, 128)).save(src)
        dest = t / "d.png"
        # no upscayl configured -> LANCZOS fallback path
        bm.upscayl_or_resize({"upscaylBin": "", "upscaylModels": ""}, src, dest, 512)
        with Image.open(dest) as out:
            out = out.convert("RGBA")
        assert out.size == (512, 256), f"aspect ratio broken: {out.size}"
        assert out.getextrema()[3][0] == 0, "cutout alpha lost"


def test_already_large_is_not_stretched() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        src = t / "s.png"
        _texture((1024, 1024), alpha=False).save(src)
        dest = t / "d.png"
        bm.upscayl_or_resize({"upscaylBin": "", "upscaylModels": ""}, src, dest, 512)
        with Image.open(dest) as out:
            # resize_long_edge is grow-only: a source at/above target is kept
            assert out.size == (1024, 1024), out.size


def test_blank_aio_root_is_not_the_current_folder() -> None:
    """The shipped example leaves bdoAioRoot blank; that must mean 'not set',
    never the folder the tool happens to run from."""
    import os
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        tex = t / "tools" / "genital_packs" / "texture"
        tex.mkdir(parents=True)
        (tex / "pbw_00_nude_0001.dds").write_bytes(b"DDS ")
        cfg = {"bdoAioRoot": "", "sourceGlobs": ["tools/genital_packs/texture/**/*.dds"]}
        old = os.getcwd()
        os.chdir(t)
        try:
            assert bm._aio_root(cfg) is None
            assert bm._aio_root({"bdoAioRoot": "   "}) is None
            assert bm.collect_from_aio_fallback(cfg) == []
            cfg["bdoAioRoot"] = str(t)
            got = [p.name for p in bm.collect_from_aio_fallback(cfg)]
            assert got == ["pbw_00_nude_0001.dds"], got
        finally:
            os.chdir(old)


def test_shipped_example_has_no_machine_path() -> None:
    import json
    example = Path(__file__).resolve().parent.parent / "config.example.json"
    cfg = json.loads(example.read_text(encoding="utf-8"))
    assert cfg["bdoAioRoot"] == "", cfg["bdoAioRoot"]
    for key, value in cfg.items():
        if isinstance(value, str):
            assert "\\Users\\" not in value and "/Users/" not in value, (key, value)


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    dds.demo()
    print(f"\n{len(tests)} BodyMats checks + dds self-check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
