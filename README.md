# SQL Parser

This project is designed to take in an SQL query and print out the origin of all the filter conditions.

## Testing

To test, change the SQL query defined in `sql_parser.py`.

## Aim of this Project

Convert the conditions of an SQL query into a list of dictionaries where each dictionary represents one condition and contains:

1. **Original Table**: The table from which we should fetch the value to compare.
2. **Column Name**: The column name in the table.
3. **Value**: The value with which we should compare the value of the database.

## Underlying Idea

Convert an SQL query into an Abstract Syntax Tree (AST). Once we have an AST, we will traverse through the tree to find the original table and original column value.

## Flow of the Code

1. Use the Python library `SQLGLOT` to convert the SQL query into an AST (`base_expression`).
2. Extract the `WHERE` clause in `base_expression` into `target_where_clause`, as this is where the filter conditions of the SQL query are.
3. Create a list of `ColumnLiteralHolder` objects called `column_holder_list` for all the filter conditions in `target_where_clause`.
4. `ColumnLiteralHolder` holds the actual table/CTE name, column name (which could be the actual name or alias), and value.
5. Traverse through `column_holder_list` and the `base_expression` tree to find the `original_table` and `original_column`.
6. Store these in `column_origin_list` as a list of `ColumnOrigin` objects, where `ColumnOrigin` objects have the `original_table_name`, `original_column`, and `value`.

## Future Enhancements

1. Extend to handle sub-queries.
2. Extend to handle `>`, `<`, `<=`, `>=` operators.




