from simulation.run_simulation import load_scenario


def test_load_scenario_accepts_legacy_name_aliases():
    messages = load_scenario("noisy_path")

    assert isinstance(messages, list)
    assert messages
