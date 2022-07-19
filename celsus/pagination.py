from numpy import ceil


class Page:
    def __init__(self, query_model, page, per_page):
        self.query_model = query_model
        self.page = page
        self.per_page =per_page

    def count(self):
        return self.query_model.count()

    def values(self):
        return self.query_model.offset((self.page-1)*self.per_page).limit(self.per_page).all()

    def total_pages(self):
        return ceil(self.count()/self.per_page)