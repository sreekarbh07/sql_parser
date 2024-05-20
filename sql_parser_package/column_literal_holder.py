import sqlglot.expressions


class ColumnLiteralHolder:
    def __init__(self, column: sqlglot.expressions.Column, literal):
        self.table_name = column.args['table'].alias_or_name
        self.column_name = column.alias_or_name
        self.literal = literal

    def get_table_name(self) -> str:
        return self.table_name

    def get_column_name(self) -> str:
        return self.column_name

