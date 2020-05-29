class Transformer:
    transform_rules = {}
    drop_keys = []

    def __init__(self, transform_rules=None, drop_keys=None):
        self.transform_rules = transform_rules or self.transform_rules
        self.drop_keys = drop_keys or self.drop_keys

    def transform_item(self, item):
        item = self.transform_item_keys(item, self.transform_rules)
        item = self.drop_item_keys(item, self.drop_keys)

        return item

    @staticmethod
    def transform_item_keys(item, rules):
        for key in rules.keys():
            if key in item.keys():
                item[rules[key]] = item.pop(key)

        return item

    @staticmethod
    def drop_item_keys(item, drop_keys):
        for key in drop_keys:
            item.pop(key, None)

        return item


class EmptyTransformer(Transformer):
    @staticmethod
    def transform_item_keys(item, rules):
        return item


class WildsearchCrawlerWildberriesTransformer(Transformer):
    transform_rules = {
        'wb_id': 'id',
        'product_url': 'url',
        'product_name': 'name',
        'wb_price': 'price',
        'wb_category_position': 'position',
        'wb_purchases_count': 'purchases',
        'wb_rating': 'rating',
        'wb_reviews_count': 'reviews',
        'wb_category_url': 'category_url',
        'wb_category_name': 'category_name',
        'wb_brand_name': 'brand_name',
        'wb_brand_country': 'brand_country',
        'wb_manufacture_country': 'manufacture_country',
        'wb_first_review_date': 'first_review',
    }


class WildsearchCrawlerOzonTransformer(Transformer):
    transform_rules = {
        'ozon_brand_name': 'brand_name',
        'ozon_category_name': 'category_name',
        'ozon_category_position': 'position',
        'ozon_category_url': 'category_url',
        'ozon_first_review_date': 'first_review',
        'ozon_id': 'id',
        'ozon_price': 'price',
        'ozon_rating': 'rating',
        'ozon_reviews_count': 'reviews',
        'product_name': 'name',
        'product_url': 'url',
    }
