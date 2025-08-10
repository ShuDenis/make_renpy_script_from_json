import sys
from pathlib import Path

# Add src directory to import path
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))

from dialoggen.generator import generate_rpy


def test_basic_dialog_generation():
    data = {
        'project': {
            'default_character': 'narrator'
        },
        'dialog_trees': [
            {
                'id': 'intro',
                'entry_node': 'n1',
                'locals': [
                    {'name': 'mood', 'type': 'str', 'default': 'neutral'}
                ],
                'nodes': [
                    {'id': 'n1', 'type': 'say', 'character': 'e', 'text': 'Hi', 'next': 'n2'},
                    {
                        'id': 'n2',
                        'type': 'choice',
                        'prompt': 'How?',
                        'choices': [
                            {'id': 'c1', 'text': 'One', 'next': 'n3'},
                            {'id': 'c2', 'text': 'Two', 'next': 'n4'},
                        ],
                    },
                    {
                        'id': 'n3',
                        'type': 'say',
                        'character': 'e',
                        'text': 'You chose one',
                        'voice': 'v1.ogg',
                        'text_tags': ['b'],
                        'next': 'n5',
                    },
                    {
                        'id': 'n4',
                        'type': 'say',
                        'text': 'No char',
                        'next': 'n5',
                    },
                    {'id': 'n5', 'type': 'return'},
                ],
            }
        ],
    }

    files = generate_rpy(data)
    assert Path('_gen/dialogs_helpers.rpy') in files
    tree = files[Path('_gen/dialogs_intro.rpy')]
    assert 'label dlg_intro__start:' in tree
    assert "$ mood = 'neutral'" in tree
    assert 'jump dlg_intro__n1' in tree
    assert 'label dlg_intro__n2:' in tree
    assert '_("How?")' in tree
    assert '_("One")' in tree
    assert 'voice "v1.ogg"' in tree
    assert 'e _("{b}You chose one{/b}")' in tree
