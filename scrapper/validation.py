# validation.py

class Validation:
    def __init__(self, product_data):
        self.product_data = product_data

    def validate(self):
        errors = []

        for product in self.product_data:
            product_errors = self.validate_product(product)
            if product_errors:
                errors.append({product.get('product_id', 'Unknown ID'): product_errors})

        return errors

    def validate_product(self, product):
        errors = []

        if not self.validate_mandatory_fields(product):
            errors.append("Missing mandatory fields")

        if not self.validate_prices(product):
            errors.append("Sale price is greater than the original price")

        if not self.validate_variants(product):
            errors.append("Each variant must have images and prices")

        return errors

    def validate_mandatory_fields(self, product):
        mandatory_fields = ['title', 'product_id']
        for field in mandatory_fields:
            if field not in product or not product[field]:
                return False
        return True

    def validate_prices(self, product):
        for sale_price in product["sale_prices"]:
            if  'price' in product:
                if sale_price >  product['price']:
                    return False
        return True

    def validate_variants(self, product):
        for variants in product["models"]:
            if variants and variants["variant"]:
                for variant in variants['variant']:
                    if 'image' not in variant or not variant['image']:
                        return False
                    if 'price' not in variant or not variant['price']:
                        return False
        return True
