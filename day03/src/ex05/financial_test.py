import pytest
from financial import reciever, find_field, print_data, main


def test_reciever_1():
    assert reciever('apld').status_code == 200


def test_reciever_2():
    assert reciever('MSFT').status_code == 200


def test_reciever_3():
    assert reciever('NVDA').status_code == 200


def test_find_field_1():
    data = find_field(reciever('msft'), 'Total Revenue')
    assert len(data) == 6
    assert isinstance(data, tuple) == True


def test_find_field_2():
    data = find_field(reciever('apld'), 'Total Revenue')
    assert len(data) == 6
    assert isinstance(data, tuple) == True


def test_find_field_3():
    data = find_field(reciever('nvda'), 'Total Revenue')
    assert len(data) == 6
    assert isinstance(data, tuple) == True


def test_find_field_4():
    with pytest.raises(TypeError):
        find_field(reciever('tttt'), 'Total Revenue')


def test_print_data_1():
    data = ('Total Revenue',)
    assert print_data(data) == False


def test_print_data_2():
    assert print_data(('Total Revenue', '221,192 ', '165,575 ',
                      '55,392 ', '8,549 ', '-- ')) == True


def test_print_data_3():
    assert print_data(('Total Revenue', '221,192 ',
                      '165,575 ', '55,392 ', '8,549 ')) == True


def test_main_1():
    main('msft', 'Total Revenue')


def test_main_2():
    main('apld', 'Gross Profit')


def test_main_3():
    main('nvda', 'Total Expenses')
