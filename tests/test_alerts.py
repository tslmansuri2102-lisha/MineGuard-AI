import unittest

from backend.alerts import AlertService


class TestAlertService(unittest.TestCase):

    def setUp(self):
        self.service = AlertService()

    def make_prediction(self, risk_level="LOW", risk_score=20.0):
        return {
            "mine_id": "MINE-001",
            "zone_id": "ZONE-003",
            "sensor_id": "SENSOR-003",
            "timestamp": "2026-08-17T12:00:00Z",
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommended_action": "Monitor the affected zone.",
            "factors": [
                {
                    "feature": "displacement_rate",
                    "impact": "HIGH",
                }
            ],
        }

    def test_low_risk_does_not_create_alert(self):
        result = self.service.evaluate_and_dispatch(
            self.make_prediction("LOW", 20.0)
        )

        self.assertIsNone(result)
        self.assertEqual(self.service.get_history(), [])

    def test_moderate_risk_does_not_create_alert(self):
        result = self.service.evaluate_and_dispatch(
            self.make_prediction("MODERATE", 45.0)
        )

        self.assertIsNone(result)
        self.assertEqual(self.service.get_history(), [])

    def test_high_risk_creates_alert(self):
        result = self.service.evaluate_and_dispatch(
            self.make_prediction("HIGH", 75.0)
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.risk_level, "HIGH")
        self.assertEqual(result.risk_score, 75.0)
        self.assertEqual(result.alert_id, "ALERT-000001")

    def test_critical_risk_creates_alert(self):
        result = self.service.evaluate_and_dispatch(
            self.make_prediction("CRITICAL", 95.0)
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.risk_level, "CRITICAL")
        self.assertEqual(result.alert_id, "ALERT-000001")

    def test_alert_history_is_stored(self):
        self.service.evaluate_and_dispatch(
            self.make_prediction("HIGH", 80.0)
        )
        self.service.evaluate_and_dispatch(
            self.make_prediction("CRITICAL", 98.0)
        )

        history = self.service.get_history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["risk_level"], "CRITICAL")
        self.assertEqual(history[1]["risk_level"], "HIGH")

    def test_subscriber_receives_alert(self):
        received = []

        def subscriber(alert):
            received.append(alert)

        self.service.register_subscriber(subscriber)

        self.service.evaluate_and_dispatch(
            self.make_prediction("HIGH", 80.0)
        )

        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].risk_level, "HIGH")

    def test_alert_counter_increments(self):
        first = self.service.evaluate_and_dispatch(
            self.make_prediction("HIGH", 70.0)
        )
        second = self.service.evaluate_and_dispatch(
            self.make_prediction("CRITICAL", 95.0)
        )

        self.assertEqual(first.alert_id, "ALERT-000001")
        self.assertEqual(second.alert_id, "ALERT-000002")


if __name__ == "__main__":
    unittest.main()