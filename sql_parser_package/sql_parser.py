import sqlglot

from column_literal_holder import ColumnLiteralHolder
from column_origin import ColumnOrigin


def main():
    schema = {"table_a": {"col_a"},
              "table_c": {"col_c"},
              "table_d": {"col_d"}}

    sql_string = """
                with cte1 as (
                    select table_c.col_c as col_1, table_d.col_d as col_2 from table_c inner join table_d on table_c.col_c = table_d.col_d),
                cte2 as (
                select table_c.col_c as col_1, table_a.col_a as col_2 from table_c outer join table_a on table_c.col_c = table_a.col_a)
                  
                select * from cte1 inner join cte2 on cte1.col_1 = cte2.col_1 where cte1.col_2 = 3 AND cte2.col_1 in (8, 9, 10) OR cte2.col_2 like 'a%'
                """

    """
    Answer should look something like: 
    
    {
        {
            table: table_d
            column: col_1
            value: 3
        },
        {
            table: table_c
            column: col_1
            value: 5
        }
    }
    """

    # TODO: 1. get the list of (column, literal) objects to identify
    #       2. traverse through the base tree and find out the origins of the columns
    #       3. populate the resultant map

    base_expression: sqlglot.Expression = sqlglot.parse_one(sql_string)
    target_where_clause: sqlglot.Where = base_expression.args['where']

    if target_where_clause is None:
        print("Where clause is not present in the main query")
        return

    column_holder_list = list()
    traverse_and_populate_column_holder_list(target_where_clause, column_holder_list)

    print(column_holder_list)

    column_origin_list = list()
    for column_holder in column_holder_list:
        if base_expression.args.get('with') is not None:
            column_origin_list.append(traverse_and_find_origin_of_column(base_expression.args.get('with'), column_holder, schema))

    print(ColumnOrigin.print_results(column_origin_list))


def traverse_and_find_origin_of_column(expression: sqlglot.expressions.With, column_holder: ColumnLiteralHolder,
                                       schema: dict) -> ColumnOrigin:
    if is_table_present_in_schema(column_holder, schema):
        return ColumnOrigin(column_holder.get_table_name(), column_holder.get_column_name(), column_holder.literal)

    for cte_expression in expression.args.get('expressions'):
        table_alias = cte_expression.alias
        if column_holder.get_table_name() == table_alias:
            for alias_expression in cte_expression.args['this'].args['expressions']:
                if column_holder.get_column_name() == alias_expression.alias:
                    column = alias_expression.args['this']
                    original_column_name = column.args['this'].alias_or_name
                    original_table_name = column.args['table'].alias_or_name
                    return ColumnOrigin(original_table_name, original_column_name, column_holder.literal)


def is_table_present_in_schema(column_holder: ColumnLiteralHolder, schema: dict):
    return column_holder.get_table_name() in schema.keys()


def traverse_and_populate_column_holder_list(current_expression: sqlglot.Expression, column_holder_list: list):
    for this_expression in current_expression.args.values():
        if is_instance_of_and_or(this_expression):
            traverse_and_populate_column_holder_list(this_expression, column_holder_list)
        else:
            if is_instance_of_column(this_expression.args['this']):
                column_holder_list.append(
                    ColumnLiteralHolder(this_expression.args['this'], this_expression.args.get('expression',
                                                                                               this_expression.args.get(
                                                                                                   'expressions'))))
            else:
                for expression in this_expression.args.values():
                    traverse_and_populate_column_holder_list(expression, column_holder_list)


def is_instance_of_and_or(expression: sqlglot.Expression) -> bool:
    return isinstance(expression, (sqlglot.expressions.Or, sqlglot.expressions.And))


def is_instance_of_column(expression: sqlglot.Expression) -> bool:
    return isinstance(expression, sqlglot.expressions.Column)


if __name__ == '__main__':
    main()
