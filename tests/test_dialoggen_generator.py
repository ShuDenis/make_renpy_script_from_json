from dialoggen.generator import generate_rpy


def test_generate_rpy_outputs_expected_labels(dialog_project):
    files = generate_rpy(dialog_project)
    assert "dialogs_day1_intro.rpy" in files
    script = files["dialogs_day1_intro.rpy"]
    assert "label dlg_day1_intro__start" in script
    assert "label dlg_day1_intro__n_start" in script
    assert 'e "Привет! Сегодня начнём."' in script
    assert "menu" in script
    assert "if mood=='happy'" in script
    assert "return" in script
