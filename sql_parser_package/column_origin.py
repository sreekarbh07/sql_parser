import sqlglot.expressions


class ColumnOrigin:
    def __init__(self, original_table_name, original_column_name, value):
        self.original_table_name = original_table_name
        self.original_column_name = original_column_name

        if isinstance(value, sqlglot.expressions.Literal):
            self.value = value.args['this']
        else:
            ans = '('
            for literal in value:
                ans += literal.args['this'] + ', '
            ans += ')'
            self.value = ans

    def __str__(self):
        ans = '{'
        ans += '"table_name": '
        ans += '"' + self.original_table_name + '"'
        ans += ', "column_name": '
        ans += '"' + self.original_column_name + '"'
        ans += ', "value": '
        ans += '"' + self.value + '"'
        ans += '}'
        return ans

    @staticmethod
    def print_results(list_column_origin):
        ans = '['
        for column_origin in list_column_origin:
            ans += column_origin.__str__() + ', '
        ans += ']'
        return ans





