# coding: utf-8

from openfoodfacts.products import advanced_search
from timer import Timer

from time import sleep
import json
import sys

class Progressbar(Timer):
    def __init__(self, limit_time):
        '''
            limit_time: temps d'exécution de la barre de progression en ms
        '''
        super().__init__(start=False)
        self.pb = 0
        self.pb_len = 78
        self.limit_time = limit_time
        print("[0%{}100%]".format('-' * 72))
        print(" ", end="")
        self.run()

    def __call__(self):
        tmp = min(int(self.pb_len * self.elapsed() / self.limit_time),
                  self.pb_len)
        progress = tmp - self.pb
        if progress:
            self.pb = tmp
            print("#"*progress, end="", flush=True)
        return bool(self.pb != self.pb_len)


class WrapAPI:
    DESCRIPTION = {
        'product': {
            'product_name_fr': 'pname',
            'code': 'code',
            'url': 'url',
            'stores': 'stores',
            'brands': 'brand',
            'quantity': 'quantity',
            'energy': 'energy',
            'nutrition_grade_fr': 'score'
        },
        'category': {
            'categories': 'cname'
        }
    }

    PAGE_SIZES = {0: 20, 1: 50, 2: 100, 3:500, 4: 1000}
    DEFAULT_PAGE_SIZE = PAGE_SIZES[1]

    def __init__(self, page_size=DEFAULT_PAGE_SIZE):
        self.page = 1
        self.no_product = 0
        if page_size in WrapAPI.PAGE_SIZES.values():
            self.page_size = page_size
        else:
            self.page_size = WrapAPI.DEFAULT_PAGE_SIZE

    @staticmethod
    def load_products_from_opf(page=1, page_size=DEFAULT_PAGE_SIZE):
        req = {
            'action': 'process',
            'nutriment_0': 'energy',
            'nutriment_compare_0': 'gt',
            'nutriment_value_0': '0',
            'sort_by': 'product_name',
            'page_size': '50',
            'page': '1'
        }
        try:
            req['page'] = str(page)
            req['page_size'] = str(self.page_size)
            list_prod = advanced_search(req)['products']
            # with open("data_products.json", "w") as fp:
            #     fp.write(json.dumps(list_prod['products'], sort_keys=True,
            #              indent=4))
            return list_prod
        except:
            print(sys.exc_info([0]))
        return None

    def get_all_products(self):
        progress = Progressbar(60*1000)
        datas = None
        with open("data_products.json", "r") as fp:
            datas = json.load(fp)
        self.page = 1
        self.no_product = 0
        # datas = load_products_from_opf(page)
        while datas:
            # prod contient un produit de le bdd d'Open Food Facts
            for prod in datas:
                p = {'product':{}, 'category':{}}
                for k, v in WrapAPI.DESCRIPTION['product'].items():
                    if k == 'energy':
                        p['product']['energy'] = prod['nutriments']['energy'])
                    elif k in prod.keys():
                        p['product'][v] = str(prod[k]).replace(";", "")
                k = 'categories'
                v = WrapAPI.DESCRIPTION['category'][k]
                if k in prod.keys():
                    p['category'][v] = str(prod[k]).replace(";", "")
                self.no_product += 1
                try:
                    if p['product']['pname'] and p['category']['cname']:
                        yield p
                except KeyError:
                    pass
                if not progress():
                    print("\n", progress)
                    raise StopIteration
            self.page += 1
            datas = None
            # datas = WrapAPI.load_products_from_opf(page)


if __name__ == '__main__':
    from pprint import pprint
    #
    # gen_prod = products()
    # pprint(next(gen_prod))

    api_opf = WrapAPI()
    cpt = 0
    for p in api_opf.get_all_products():
        # pprint(p)
        cpt += 1
    print("\n", cpt)
