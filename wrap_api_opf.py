# coding: utf-8

from openfoodfacts.products import advanced_search
from timer import Timer, tms_to_str
from pickle import Pickler, Unpickler, HIGHEST_PROTOCOL
import sys

class Progressbar(Timer):
    '''
        Display of a progress bar in the terminal whose maximum is given by
        the time limit for the execution of a function.
        :param limit_time: Max time of execution of a function in ms.
        type limit_time: int
    '''
    def __init__(self, limit_time):
        super().__init__(start=False)
        self.pb = 0  # Indicates the progress of the bar on the screen.
        self.pb_len = 78  # Max of the progress bar on the screen.
        self.limit_time = limit_time
        print("Le temps d'attente est d'environ %s" % tms_to_str(limit_time))
        print("[0%{}100%]".format('-' * 72))
        print(" ", end="")
        self.run()

    def __call__(self):
        elapsed = self.elapsed()
        if elapsed >= self.limit_time:
            progress = self.pb_len - self.pb
            print("#"*progress, flush=True)
            return False

        tmp = int(self.pb_len * elapsed / self.limit_time)
        progress = tmp - self.pb
        if progress:
            self.pb = tmp
            print("#"*progress, end="", flush=True)
        return True


class WrapAPI:
    """
        This class makes it possible to exploit the API written in Python of
        Open Food Facts.

        
    """
    # Equivalence between the fields in the Open Food Facts database and the
    # one used for the application. "product" and "category" are the names of
    # the tables.
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
            'sort_by': 'unique_scans_n',
            'page_size': '50',
            'axis_x': 'energy',
            'axis_y': 'products_n',
            'page': '1'
        }
        try:
            req['page'] = str(page)
            req['page_size'] = str(page_size)
            list_prod = advanced_search(req)["products"]
            return list_prod
        except:
            raise
        return None

    def download_products(self):
        """
            During the time given to the ProgressBar object, the
            download_products function allows you to download the products from
            the OpenFoodFacts database by saving only the tables and fields
            specified by the DESCRIPTION variable.
        """
        # progress = Progressbar(5*60*1000)
        progress = Progressbar(60*1000)

        datas = None
        fp = open("data_products.bin", "wb")
        pck = Pickler(fp, HIGHEST_PROTOCOL)
        self.page = 1
        datas = WrapAPI.load_products_from_opf(self.page,
                                               page_size=self.page_size)
        while datas:
            for prod in datas:
                p = {'product':{}, 'category':{}}
                for k, v in WrapAPI.DESCRIPTION['product'].items():
                    if k == 'energy':
                        p['product']['energy'] = \
                            int(prod['nutriments']['energy'])
                    elif k in prod.keys():
                        p['product'][v] = "%s" % prod[k].replace('"', '\"')

                k = 'categories'
                v = WrapAPI.DESCRIPTION['category'][k]
                if k in prod.keys():
                    p['category'][v] = "%s" % prod[k].replace('"', '\"')

                try:
                    if p['product']['pname'] and p['category']['cname']:
                        pck.dump(p)
                except KeyError:
                    pass

            if progress():
                self.page += 1
                datas = WrapAPI.load_products_from_opf(
                    self.page, page_size=self.page_size)
            else:
                datas = None
        fp.close()

    def get_all_products(self):
        """
            Returns one by one the products recovered in the OpenFoodFacts
            database.
        """
        fp = open("data_products.bin", "rb")
        unpck = Unpickler(fp)
        try:
            d = unpck.load()
            while(d):
                yield d
                d = unpck.load()
        except EOFError:  # End of file reached.
            fp.close()
            raise StopIteration

    # def get_all_products(self):
    #     # progress = Progressbar(5*60*1000)
    #     progress = Progressbar(60*1000)
    #
    #     datas = None
    #     # with open("data_products.json", "r") as fp:
    #     #     datas = json.load(fp)
    #     self.page = 1
    #     datas = WrapAPI.load_products_from_opf(self.page, page_size=self.page_size)
    #     while datas:
    #         for prod in datas:
    #             p = {'product':{}, 'category':{}}
    #             for k, v in WrapAPI.DESCRIPTION['product'].items():
    #                 if k == 'energy':
    #                     p['product']['energy'] = \
    #                         int(prod['nutriments']['energy'])
    #                 elif k in prod.keys():
    #                     p['product'][v] = "'%s'" % prod[k].replace("'", "\\'")
    #             k = 'categories'
    #             v = WrapAPI.DESCRIPTION['category'][k]
    #             if k in prod.keys():
    #                 p['category'][v] = "'%s'" % prod[k].replace("'", "\\'")
    #             try:
    #                 if p['product']['pname'] and p['category']['cname']:
    #                     yield p
    #             except KeyError:
    #                 pass
    #
    #             if not progress():
    #                 print("\n", progress)
    #                 raise StopIteration
    #         self.page += 1
    #         datas = WrapAPI.load_products_from_opf(self.page,
    #                                                page_size=self.page_size)


if __name__ == '__main__':
    from pprint import pprint
    api_opf = WrapAPI(500)
    fp = None
    try:
        fp = open("data_products.bin")
        fp.close()
    except IOError:
        api_opf.download_products()

    cpt = 0
    p = None
    for p in api_opf.get_all_products():
        cpt += 1
    print("{} produits ont été sauvegardées dans la base de données"
          .format(cpt))
