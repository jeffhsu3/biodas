class Source(object):
    """
    Handles the data source.  Access to the source is automatically set to
    das/source_name.
    """

    def __init__(self, source_name, source_type):
        self.source_name = source_name

    def seq_query(self, query_func):
        pass

