import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw
from video_frames import ffmpeg_path, rgba_frames


class AlphaCleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        folder = Path(cls.temp.name)
        source = Image.new('RGBA', (64, 64), (100, 40, 140, 0))
        draw = ImageDraw.Draw(source)
        draw.rectangle((18, 18, 42, 42), fill=(100, 40, 140, 255))
        draw.line((42, 20, 54, 20), fill=(100, 40, 140, 255), width=1)
        source.putpixel((57, 5), (100, 40, 140, 255))
        source.putpixel((17, 32), (100, 40, 140, 120))
        source.putpixel((3, 3), (100, 40, 140, 12))
        draw.rectangle((23, 51, 35, 53), fill=(100, 40, 140, 80))
        source.save(folder / 'fixture.png')
        cls.clip = folder / 'fixture.webm'
        subprocess.run([ffmpeg_path(), '-hide_banner', '-loglevel', 'error',
                        '-loop', '1', '-i', str(folder / 'fixture.png'),
                        '-frames:v', '2', '-c:v', 'libvpx-vp9', '-lossless', '1',
                        '-pix_fmt', 'yuva420p', '-auto-alt-ref', '0', str(cls.clip)],
                       check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def frames(self, enabled):
        with patch.dict(os.environ, {'BAILONG_ALPHA_CLEANUP': '1' if enabled else '0'}):
            return list(rgba_frames(self.clip, 64))

    def test_removes_distant_translucent_debris_but_keeps_soft_edge(self):
        raw = Image.frombytes('RGBA', (64, 64), self.frames(False)[0])
        clean = Image.frombytes('RGBA', (64, 64), self.frames(True)[0])
        self.assertGreater(raw.getpixel((29, 52))[3], 40)
        self.assertLessEqual(clean.getpixel((29, 52))[3], 1)
        self.assertLessEqual(clean.getpixel((3, 3))[3], 1)
        self.assertGreater(clean.getpixel((17, 32))[3], 60)

    def test_keeps_opaque_hair_and_detached_details(self):
        raw, clean = self.frames(False)[0], self.frames(True)[0]
        for offset in range(3, len(raw), 4):
            if raw[offset] >= 224:
                self.assertEqual(clean[offset], raw[offset])
        image = Image.frombytes('RGBA', (64, 64), clean)
        self.assertEqual(image.getpixel((53, 20))[3], 255)
        self.assertEqual(image.getpixel((57, 5))[3], 255)

    def test_keeps_rgb_and_animation_frame_count(self):
        original, cleaned = self.frames(False), self.frames(True)
        self.assertEqual(len(original), 2)
        self.assertEqual(len(cleaned), len(original))
        for raw, clean in zip(original, cleaned):
            self.assertEqual(len(clean), 64 * 64 * 4)
            for channel in (0, 1, 2):
                self.assertEqual(clean[channel::4], raw[channel::4])


if __name__ == '__main__':
    unittest.main()
