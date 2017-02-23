from os.path import abspath, dirname, join

import pytest

from omnifocus import models

@pytest.fixture
def data():
    fixture = abspath(join(dirname(__file__), 'fixtures/OmniFocus.ofocus'))
    return models.LocalData(fixture).data


def test_task():
    task = data['iCNXEbk-WAk']
    assert task.id == 'iCNXEbk-WAk'
