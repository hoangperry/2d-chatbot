import time


class SessionManagement(dict):

    def __init__(self, *args):
        dict.__init__(self, args)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)[1]

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, (val,time.time()))

    def tick(self, key):
        try:
            item = dict.__getitem__(self, key)
            item_age = time.time() - item[1]

            if item_age < 3: # age less than (still valid)
                # logging.info("Item still valid")
                return 1
            else: # age older than (it expired, delete the record)
                # logging.info("item expired, deleting item")
                del self[key]
                return 0
        except KeyError:
            return 0
