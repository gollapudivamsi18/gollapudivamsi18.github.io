import os
import unittest

import plan_waves

HERE = os.path.dirname(__file__)
INV = os.path.join(HERE, "..", "inventory")


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.servers, self.deps = plan_waves.load(
            os.path.join(INV, "servers.csv"), os.path.join(INV, "dependencies.csv"))

    def test_inputs_are_valid(self):
        self.assertEqual(plan_waves.validate(self.servers, self.deps), [])

    def test_every_server_in_exactly_one_wave(self):
        waves = plan_waves.plan(self.servers, self.deps)
        placed = [s for _, members in waves for s in members]
        self.assertEqual(sorted(placed), sorted(self.servers))

    def test_dependent_servers_move_together(self):
        waves = plan_waves.plan(self.servers, self.deps)
        wave_of = {s: i for i, (_, m) in enumerate(waves) for s in m}
        shared = {n for n, s in self.servers.items() if s["role"] in plan_waves.SHARED_ROLES}
        for d in self.deps:
            if d["source"] in shared or d["target"] in shared:
                continue
            self.assertEqual(wave_of[d["source"]], wave_of[d["target"]], d)

    def test_shared_services_first(self):
        waves = plan_waves.plan(self.servers, self.deps)
        self.assertIn("DEMO-DC01", waves[0][1])

    def test_unknown_server_detected(self):
        bad = self.deps + [{"source": "GHOST", "target": "DEMO-SQL01", "port": "1", "purpose": "x"}]
        self.assertTrue(plan_waves.validate(self.servers, bad))


if __name__ == "__main__":
    unittest.main()
