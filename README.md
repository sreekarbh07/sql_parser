# SQL Parser

This project is designed to take in an SQL query and print out the origin of all the filter conditions.

## Aim of this Project

Convert the conditions of an SQL query into a list of dictionaries where each dictionary represents one condition and contains:

1. **Original Table**: The table from which we should fetch the value to compare.
2. **Column Name**: The column name in the table.
3. **Value**: The value with which we should compare the value of the database.

## Sample Input and Output

### Input:

1. **schema**:
    ```json
    {
      "table_a": {"col_a"},
      "table_c": {"col_c"},
      "table_d": {"col_d"}
    }
    ```

2. **sql_string**:
    ```sql
    WITH 
      cte1 AS (
        SELECT table_c.col_c AS col_1, table_d.col_d AS col_2 
        FROM table_c 
        INNER JOIN table_d ON table_c.col_c = table_d.col_d
      ),
      cte2 AS (
        SELECT table_c.col_c AS col_1, table_a.col_a AS col_2 
        FROM table_c 
        OUTER JOIN table_a ON table_c.col_c = table_a.col_a
      )
    SELECT * 
    FROM cte1 
    INNER JOIN cte2 ON cte1.col_1 = cte2.col_1 
    WHERE cte1.col_2 = 3 
      AND cte2.col_1 IN (8, 9, 10) 
      OR cte2.col_2 LIKE 'a%'
    ```

### Output:

```json
[
  {"table_name": "table_d", "column_name": "col_d", "value": "3"}, 
  {"table_name": "table_c", "column_name": "col_c", "value": "(8, 9, 10, )"}, 
  {"table_name": "table_a", "column_name": "col_a", "value": "a%"}
]
```
## Underlying Idea

Convert an SQL query into an Abstract Syntax Tree (AST). Once we have an AST, we will traverse through the tree to find the original table and original column value.

## AST Explanation

### Basic AST block of a query:

![image](https://github.com/sreekarbh07/sql_parser/assets/170374414/bd2639fe-5419-4ef9-bec5-6c8918ef0dcd)


1. **Projections**: 
    - For any query, projections are basically the columns that we output (which will be written in the `SELECT` clause).

2. **Filter Expressions**: 
    - Filter expressions are the filter conditions that should be applied to the data (which will be written in the `WHERE` clause).

3. **Source**: 
    - Source is basically the entire data from which the data should be filtered (which will be written in the `FROM` clause).




## Flow of the Code

1. Use the Python library `SQLGLOT` to convert the SQL query into an AST (`base_expression`).
2. Extract the `WHERE` clause in `base_expression` into `target_where_clause`, as this is where the filter conditions of the SQL query are.
3. Create a list of `ColumnLiteralHolder` objects called `column_holder_list` for all the filter conditions in `target_where_clause`.
4. `ColumnLiteralHolder` holds the actual table/CTE name, column name (which could be the actual name or alias), and value.
5. Traverse through `column_holder_list` and the `base_expression` tree to find the `original_table` and `original_column`.
6. Store these in `column_origin_list` as a list of `ColumnOrigin` objects, where `ColumnOrigin` objects have the `original_table_name`, `original_column`, and `value`.

## Testing

To test, change the SQL query defined in `sql_parser.py`.

## Future Enhancements

1. Extend to handle sub-queries.
2. Extend to handle `>`, `<`, `<=`, `>=` operators.




