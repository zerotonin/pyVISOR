from pyvisor.GUI.behavBinding import BehavBinding


def test_to_dict():

    binding = BehavBinding(
        animal='fly1',
        color='#FFAA50',
        icon_path='/home/icons/are/nice.png',
        behaviour='aggression',
        keyBinding='B1',
        device='XBox'
    )

    d = binding.to_dict()

    assert len(d) == 6
    assert d['animal'] == 'fly1'
    assert d['color'] == '#FFAA50'
    assert d['icon_path'] == '/home/icons/are/nice.png'
    assert d['behaviour'] == 'aggression'
    assert d['key'] == 'B1'
    assert d['device'] == 'XBox'


def test_from_dict():

    d = {
        'animal': 'seal',
        'behaviour': 'chill',
        'color': None,
        'icon_path': '/home/icons/are/quite/okay.png',
        'key': 'B0',
        'device': 'Playstation'
    }

    binding = BehavBinding.from_dict(d)

    assert 'seal' == binding.animal
    assert 'chill' == binding.behaviour
    assert binding.color is None
    assert '/home/icons/are/quite/okay.png' == binding.icon_path
    assert 'B0' == binding.keyBinding
    assert 'Playstation' == binding.device
