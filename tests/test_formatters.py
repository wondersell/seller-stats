import pytest

from seller_stats.formatters import format_add_postfix, format_currency, format_number, format_percent, format_quantity


@pytest.mark.parametrize('number, expected', [
    [11574747, '11 574 747'],
    [11574747.88, '11 574 747,88'],
    [-12345678.99, '-12 345 678,99'],
    [-12345678.991, '-12 345 678,99'],
])
def test_format_number(number, expected):
    assert format_number(number) == expected


@pytest.mark.parametrize('number, expected', [
    [0.8, '80%'],
    [0.55, '55%'],
    [0.875, '87,5%'],
    [0.9999, '99,99%'],
    [1.986, '198,6%'],
    [-123.8988, '-12 389,88%'],
])
def test_format_percent(number, expected):
    assert format_percent(number) == expected


@pytest.mark.parametrize('number, expected', [
    [11574747, '`11 574 747` руб.'],
    [11574747.88, '`11 574 747,88` руб.'],
    [-12345678.99, '`-12 345 678,99` руб.'],
])
def test_format_currency(number, expected):
    assert format_currency(number) == expected


@pytest.mark.parametrize('number, expected', [
    [11574747, '`11 574 747` шт.'],
    [11574747.88, '`11 574 747,88` шт.'],
    [-12345678.99, '`-12 345 678,99` шт.'],
])
def test_format_quantity(number, expected):
    assert format_quantity(number) == expected


@pytest.mark.parametrize('number, postfix, highlighter, expected', [
    [11574747, 'руб.', '`', '`11 574 747` руб.'],
    [11574747.88, '', 'эээ', 'эээ11 574 747,88эээ'],
    [-12345678.99, 'шт.', '', '-12 345 678,99 шт.'],
])
def test_format_add_postfix(number, postfix, highlighter, expected):
    assert format_add_postfix(number, postfix=postfix, highlighter=highlighter) == expected
