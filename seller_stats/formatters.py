def format_number(number):
    number = int(number) if float(round(number, 2)) % 1 == 0 else round(float(number), 2)

    return '{:,}'.format(number).replace(',', ' ').replace('.', ',')


def format_add_postfix(number, postfix, highlighter=''):
    return f'{highlighter}{format_number(number)}{highlighter} {postfix}'.strip()


def format_percent(ratio):
    return f'{format_number(ratio * 100)}%'


def format_currency(number, currency='руб.'):
    return format_add_postfix(number, currency, highlighter='`')


def format_quantity(number, quanter='шт.'):
    return format_add_postfix(number, quanter, highlighter='`')
