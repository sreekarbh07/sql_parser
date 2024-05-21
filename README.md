# SQL parser
This is designed to take in sql query and print out the origin of all the filter conditions.

to test: change the sql query defined in the sql_parser.py

Aim of this project:
  Convert the conditions of an SQL query into a list of dictionary where each dictionary belongs to noe condition and it contains:
    1. Original Table fromm we should fetch the value to compare
    2. Column Name in the table 
    3. Value with which we should compare the value of database with.

Underlying Idea:
  Convert an SQL query into an AST (Abstract Syntax Tree). Once we have an Abstract Syntax Tree, we will traverse through tree and find the original table ad original column value.

Flow of the Code:
  1. I have used the python library called SQLGLOT to convert the sql query into an AST. (base_expression)
  2. Extracting the where clause in base_expression into target_where_clause, as this is where the filter conditions of the sql are.
  3. creating a list of ColumnLiteralHolder objects called column_holder_list for all the filter conditions in target_where_clause.
  4. ColumnLiteralHolder holds the actual table/cte name, column name (this could be actual name or alias) and value.
  5. Then traversing through column_holder_list we will traverse through the base_expression tree and find the original_table and origina_column.
  6. These are stored in column_origin_list as list of ColumnOrigin objects. where ColumnOrigin objects has the original_table_name, original_column, value.


Future Enhancements:
  1. We can extend this to handle it sub-quries.
  2. We can extend this to handling >, <, <=, >= operators



