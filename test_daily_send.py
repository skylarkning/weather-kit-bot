import unittest
from datetime import datetime, date
from check_daily_send import in_delivery_window, already_sent


class DeliveryTests(unittest.TestCase):
    def test_utc_windows_and_dst(self):
        cases = [('2026-10-04T11:00:00+00:00', True),
                 ('2026-10-04T12:40:00+00:00', True),
                 ('2026-12-04T11:40:00+00:00', False),
                 ('2026-12-04T12:00:00+00:00', True),
                 ('2026-10-04T14:00:00+00:00', False)]
        for stamp, expected in cases:
            self.assertEqual(in_delivery_window(datetime.fromisoformat(stamp)), expected)

    def test_daily_dedup_and_current_run(self):
        runs = [{'id':1, 'created_at':'2026-10-04T11:00:00Z'}]
        jobs = lambda _: [{'steps':[{'name':'Generate and send weather card','conclusion':'success'}]}]
        self.assertTrue(already_sent(runs,date(2026,10,4),2,jobs))
        self.assertFalse(already_sent(runs,date(2026,10,4),1,jobs))
        self.assertFalse(already_sent(runs,date(2026,10,5),2,jobs))

    def test_failed_send_does_not_block_retry(self):
        runs = [{'id':1, 'created_at':'2026-10-04T11:00:00Z'}]
        jobs = lambda _: [{'steps':[{'name':'Generate and send weather card','conclusion':'failure'}]}]
        self.assertFalse(already_sent(runs,date(2026,10,4),2,jobs))
