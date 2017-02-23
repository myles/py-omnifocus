from os.path import abspath, dirname, join

import pytest

from omnifocus import models

@pytest.fixture
def data():
    fixture = abspath(join(dirname(__file__), 'fixtures/OmniFocus.ofocus'))
    return models.LocalData(fixture)


def test_data():
    data