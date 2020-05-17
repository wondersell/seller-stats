import pytest

from seller_stats.transformers import (EmptyTransformer, Transformer, WildsearchCrawlerOzonTransformer,
                                       WildsearchCrawlerWildberriesTransformer)


@pytest.fixture()
def required_keys():
    return [
        'id',
        'price',
        'name',
        'position',
        'url',
        'rating',
    ]


@pytest.fixture()
def sample_abstract_item():
    return {
        'one_one': 'value_1',
        'two_two': 'value_2',
        'four_four': 'value_4',
    }


@pytest.fixture()
def sample_wb_item():
    return {"product_name":"Капсулы для стирки Всё-в-1 Альпийская свежесть, 12 шт.","wb_reviews_count":"55","wb_price":"224","wb_rating":"5","wb_id":"4730307","parse_date":"2020-05-12 17:13:04.279799","marketplace":"wildberries","product_url":"https://www.wildberries.ru/catalog/4730307/detail.aspx","wb_brand_name":"Tide","wb_brand_country":"Соединенные Штаты","wb_manufacture_country":"Франция","wb_category_url":"https://www.wildberries.ru/catalog/0/search.aspx","wb_category_name":"капсулы для стирки","wb_category_position":1,"image_urls":["//img1.wbstatic.net/big/new/4730000/4730307-1.jpg","//img1.wbstatic.net/big/new/4730000/4730307-2.jpg"],"wb_purchases_count":"3500","wb_first_review_date":"2018-09-21T15:29:22.1531331+03:00","_type":"WildsearchCrawlerItemWildberries"}  # noqa


@pytest.fixture()
def sample_ozon_item():
    return {"parse_date":"2020-05-16 03:10:42.277131","marketplace":"ozon","product_name":"№1 School Ранец школьный Kitty","product_url":"/context/detail/id/145908483/","image_urls":["https://cdn1.ozone.ru/multimedia/1023397639.jpg","https://cdn1.ozone.ru/multimedia/1026536589.jpg"],"ozon_id":145908483,"ozon_seller_id":0,"ozon_sellert_name":None,"ozon_brand_id":145317806,"ozon_brand_name":"№1 School","ozon_delivery_schema":"Retail","ozon_category_url":"https://www.ozon.ru/category/rantsy-30139/","ozon_category_name":"Детские товары/Товары для школы и обучения/Детские рюкзаки, ранцы, сумки/Ранцы","ozon_category_position":1,"ozon_reviews_count":None,"ozon_price":3278,"ozon_rating":None,"ozon_manufacture_country":None,"ozon_first_review_date":None,"ozon_last_review_date":None,"_type":"dict"}  # noqa


def test_transform_item_by_rule(sample_abstract_item):
    transform_rules = {
        'one_one': 'one',
        'two_two': 'two',
        'three_three': 'three',
    }

    transformed = Transformer(transform_rules=transform_rules).transform_item(item=sample_abstract_item)

    assert 'one' in transformed.keys()
    assert 'two' in transformed.keys()
    assert 'four_four' in transformed.keys()
    assert 'one_one' not in transformed.keys()
    assert 'two_two' not in transformed.keys()


def test_transform_item_no_rules(sample_abstract_item):
    transformed = Transformer().transform_item(item=sample_abstract_item)

    assert 'one_one' in transformed.keys()
    assert 'two_two' in transformed.keys()
    assert 'four_four' in transformed.keys()


def test_transform_item_drop_keys(sample_abstract_item):
    drop_keys = ['four_four']

    transformed = Transformer(drop_keys=drop_keys).transform_item(item=sample_abstract_item)

    assert 'one_one' in transformed.keys()
    assert 'two_two' in transformed.keys()
    assert 'four_four' not in transformed.keys()


def test_wildsearch_wb_transformer(sample_wb_item, required_keys):
    transformed = WildsearchCrawlerWildberriesTransformer().transform_item(sample_wb_item)

    for key in required_keys:
        assert key in transformed.keys()


def test_wildsearch_ozon_transformer(sample_ozon_item, required_keys):
    transformed = WildsearchCrawlerOzonTransformer().transform_item(sample_ozon_item)

    for key in required_keys:
        assert key in transformed.keys()


def test_empty_transformer(sample_abstract_item):
    transformed = EmptyTransformer().transform_item(sample_abstract_item)

    assert 'one_one' in transformed.keys()
    assert 'two_two' in transformed.keys()
    assert 'four_four' in transformed.keys()

    assert transformed['one_one'] == 'value_1'
    assert transformed['two_two'] == 'value_2'
    assert transformed['four_four'] == 'value_4'
