import unittest
from main import functioncleantext
SEARCH_INPUTS = [
    "software companies in Lahore",
    "IT companies in Karachi",
    "web development agencies Islamabad",
    "restaurants in Lahore",
    "hospitals in Lahore",
    "digital marketing agency Lahore",
    "mobile app development company Lahore",
    "software house near Johar Town Lahore",
    "Techverx Lahore",
    "xyzabc123 nonexistent",
]
SAMPLE = (
    "A Co\n4.5(10)\nSoftware company · X\nClosed · Opens 9 AM · 123\nWebsite\nDirections\n"
    "B Co\n5.0(14)\nSoftware company · Y\nOpen 24 hours · 456\nWebsite\nDirections\n"
    "5 km"
)


class TestCleanText(unittest.TestCase):
    def test_live_inputs(self):
        from main import functionlocationgoogle
        for q in SEARCH_INPUTS:
            with self.subTest(query=q):
                functionlocationgoogle(q)
    def test_closed_removed(self):
        self.assertNotIn("A Co", functioncleantext(SAMPLE))

    def test_open_kept(self):
        self.assertIn("B Co", functioncleantext(SAMPLE))

    def test_scale_removed(self):
        self.assertNotIn("5 km", functioncleantext(SAMPLE))

    def test_ui_garbage_removed(self):
        self.assertNotIn("Website", functioncleantext(SAMPLE))

    def test_empty_input(self):
        self.assertEqual(functioncleantext(""), "")


if __name__ == "__main__":
    unittest.main()