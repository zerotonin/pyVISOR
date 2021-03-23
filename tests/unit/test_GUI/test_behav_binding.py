from pyvisor.GUI.model.behaviour import Behaviour


def test_to_dict():

    binding = Behaviour(
        animal_number='fly1',
        color='#FFAA50',
        icon_path='/home/icons/are/nice.png',
        name='aggression',
        key_binding='B1',
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

    binding = Behaviour.from_dict(d)

    assert 'seal' == binding.animal_number
    assert 'chill' == binding.name
    assert binding.color is None
    assert '/home/icons/are/quite/okay.png' == binding.icon_path
    assert 'B0' == binding.key_bindings
    assert 'Playstation' == binding.device
