import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

import unittest
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt
from pet import Bubble

app = QApplication.instance() or QApplication([])


class BubbleLayoutTests(unittest.TestCase):
    def setUp(self):
        self.bubble = Bubble()

    def tearDown(self):
        self.bubble.close()
        self.bubble.deleteLater()
        app.processEvents()

    def assert_labels_fit(self):
        app.processEvents()
        for label in self.bubble.findChildren(QLabel):
            with self.subTest(text=label.text()):
                self.assertGreaterEqual(label.height(), label.heightForWidth(label.width()))
                self.assertTrue(self.bubble.rect().contains(label.geometry()))

    def test_wrapped_messages_fit_when_replacing_text_and_changing_scale(self):
        for scale in (100, 50, 150, 100):
            self.bubble.set_scale_percent(scale)
            for text in ('你好', '金币、宝石，还有主人……都是我的宝贝！',
                         '这是一段较长的中文消息，用来检查自动换行以后每一行文字是否完整显示。',
                         '短句'):
                with self.subTest(scale=scale, text=text):
                    self.bubble.message(text)
                    self.assert_labels_fit()

    def test_task_title_and_quota_labels_fit_after_message(self):
        self.bubble.message('你好')
        self.bubble.task_result('主人，这一步正在检查较长的中文标题是否能够完整显示。',
                                '任务详情', lambda: None)
        self.assert_labels_fit()
        self.bubble.quota([{'name': '5小时', 'remaining': 70,
                            'resetsAt': 1800000000}])
        self.assert_labels_fit()

    def assert_body_fits(self):
        app.processEvents()
        view = self.bubble.result_view
        self.assertEqual(view.verticalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.assertEqual(view.horizontalScrollBarPolicy(), Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.assertGreaterEqual(view.viewport().height(), view.document().size().height())
        self.assertEqual(view.verticalScrollBar().maximum(), 0)
        self.assertTrue(self.bubble.rect().contains(view.geometry()))

    def test_task_body_grows_for_wrapped_text_without_scrollbars(self):
        self.bubble.task_result('主人，我忙到这一步啦…', '简短进展', lambda: None)
        app.processEvents()
        short_height = self.bubble.height()
        text = ('修复版已经重新显示在桌面上，双倍屏幕缩放下的文字检查也通过了。'
                '气泡布局检查已通过，其余检查还在完成中。') * 3
        for scale in (100, 50, 150):
            with self.subTest(scale=scale):
                self.bubble.task_result('主人，我忙到这一步啦…', text, lambda: None)
                self.bubble.set_scale_percent(scale)
                self.assert_body_fits()
                self.assertGreater(self.bubble.height(), short_height)

    def test_progress_updates_resize_body_both_up_and_down(self):
        self.bubble.task_result('正在处理', '短消息', lambda: None)
        app.processEvents()
        short_height = self.bubble.height()
        self.bubble.update_task_text('正在检查更多内容', '自动更新的进度文字，需要完整显示。' * 20)
        self.assert_body_fits()
        self.assertGreater(self.bubble.height(), short_height)
        self.bubble.update_task_text('完成', '短消息')
        self.assert_body_fits()
        self.assertEqual(self.bubble.height(), short_height)


if __name__ == '__main__':
    unittest.main()
