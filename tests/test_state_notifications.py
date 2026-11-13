import unittest

from nikhi.adhara_sutra import ObservableState


class ObservableStateTests(unittest.TestCase):
    def test_subscribers_observe_top_level_changes_and_unsubscribe(self):
        state = ObservableState()
        events = []
        unsubscribe = state.subscribe(lambda *event: events.append(event))
        state["name"] = "one"
        state.update({"other": 2})
        del state["name"]
        state.pop("other")
        self.assertEqual(events, [("set", "name", "one"), ("set", "other", 2),
                                  ("delete", "name", "one"), ("delete", "other", 2)])
        unsubscribe()
        unsubscribe()
        state["name"] = "two"
        self.assertEqual(len(events), 4)

    def test_key_filter_nested_mutation_clear_and_listener_failure(self):
        state = ObservableState()
        nested = {"count": 1}
        state["nested"] = nested
        events = []
        unsubscribe = state.subscribe(lambda *event: events.append(event), key="nested")
        nested["count"] = 2
        state["other"] = 1
        self.assertEqual(events, [])
        state["nested"] = {"count": 2}
        self.assertEqual(events, [("set", "nested", {"count": 2})])

        def failing(*_event):
            raise RuntimeError("listener failed")

        unsubscribe_failing = state.subscribe(failing)
        state["after"] = True
        self.assertTrue(state["after"])
        unsubscribe_failing()

        state.clear()
        self.assertEqual(events[-1], ("delete", "nested", {"count": 2}))
        unsubscribe()

    def test_invalid_subscriptions_are_rejected(self):
        state = ObservableState()
        with self.assertRaises(TypeError):
            state.subscribe("not callable")
        with self.assertRaises(TypeError):
            state.subscribe(lambda *_: None, key=1)


if __name__ == "__main__":
    unittest.main()
