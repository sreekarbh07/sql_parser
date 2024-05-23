import sqlglot
import re

from sqlglot import Expression
from sqlglot.expressions import CTE, Select, Star, Column

from column_literal_holder import ColumnLiteralHolder
from column_origin import ColumnOrigin


def main():
    schema = {"view_brand_campaign_4182cf6a_991e_450d_8593_54d1e38cee64": {"view_brand_campaign_4182cf6a_991e_450d_8593_54d1e38cee64_id"},
              "view_brand_adset_ai_group_4182cf6a_991e_450d_8593_54d1e38cee64": {"view_brand_adset_ai_group_4182cf6a_991e_450d_8593_54d1e38cee64_id"},
              "fb_ads_campaign_metadata": {"fb_ads_campaign_metadata_id", "campaign_name"},
              "view_brand_ad_ai_group_4182cf6a_991e_450d_8593_54d1e38cee64": {"view_brand_ad_ai_group_4182cf6a_991e_450d_8593_54d1e38cee64_id"},
              "fb_ads_adset_metadata": {"fb_ads_adset_metadata_id"}}


    sql_string = """

                WITH
                  campaign AS (
                    SELECT
                      *
                    FROM
                      view_brand_campaign_4182cf6a_991e_450d_8593_54d1e38cee64
                  ),
                  adset AS (
                    SELECT
                      *
                    FROM
                      view_brand_adset_ai_group_4182cf6a_991e_450d_8593_54d1e38cee64
                  ),
                  ad AS (
                    SELECT
                      *
                    FROM
                      view_brand_ad_ai_group_4182cf6a_991e_450d_8593_54d1e38cee64
                  ),
                  adset_metadata AS (
                    SELECT
                      *
                    FROM
                      fb_ads_adset_metadata
                  ),
                  campaign_metadata AS (
                    SELECT
                      *
                    FROM
                      fb_ads_campaign_metadata
                  )
                SELECT
                  adset.adset_id,
                  adset.adset_name,
                  SUM(adset.spend) AS total_spend,
                  SUM(adset.spend) / NULLIF(SUM(adset.purchases), 0) AS CPR
                FROM
                  adset
                  JOIN campaign_metadata ON adset.campaign_id = campaign_metadata.campaign_id
                WHERE
                  campaign_metadata.campaign_name = 'pros_productscaleup'
                GROUP BY
                  adset.adset_id,
                  adset.adset_name
                ORDER BY
                  total_spend DESC;
    """

    base_expression: sqlglot.Expression = sqlglot.parse_one(sql_string)
    target_where_clause: sqlglot.Where = base_expression.args['where']

    if target_where_clause is None:
        print("Where clause is not present in the main query")
        return

    column_holder_list = list()
    traverse_and_populate_column_holder_list(target_where_clause, column_holder_list)
    column_origin_list = list()
    for column_holder in column_holder_list:
        if base_expression.args.get('with') is not None:
            column_origin_list.append(
                traverse_and_find_origin_of_column(base_expression.args.get('with'), column_holder, schema))

    print(ColumnOrigin.print_results(column_origin_list))


def traverse_and_find_origin_of_column(expression: sqlglot.expressions.With, column_holder: ColumnLiteralHolder,
                                       schema: dict) -> ColumnOrigin:
    if is_table_present_in_schema(column_holder, schema):
        return ColumnOrigin(column_holder.get_table_name(), column_holder.get_column_name(), column_holder.literal)

    for cte_expression in expression.args.get('expressions'):
        cte_expression = expand_star_in_cte(cte_expression, schema)
        table_alias = cte_expression.alias
        if column_holder.get_table_name() == table_alias:
            for alias_expression in cte_expression.args['this'].args['expressions']:
                if column_holder.get_column_name() == alias_expression.alias:
                    column = alias_expression.args['this']
                    original_column_name = column.args['this'].alias_or_name
                    original_table_name = column.args['table'].alias_or_name
                    return ColumnOrigin(original_table_name, original_column_name, column_holder.literal)


def expand_star_in_cte(cte_expression: sqlglot.expressions.CTE, schema: dict):
    table_pattern = r'\bFROM\s+(\w+)\b|\bJOIN\s+(\w+)\b'
    table_matches = re.findall(table_pattern, str(cte_expression), re.IGNORECASE)

    tables = set()
    for match in table_matches:
        tables.update(filter(None, match))

    columns_expansion = []
    for table in tables:
        if table in schema:
            columns_expansion.extend([f"{table}.{col} AS {col}" for col in schema[table]])

    expanded_columns = ", ".join(columns_expansion)
    updated_query = str(cte_expression).replace("*", expanded_columns)
    updated_query = "with " + updated_query+"select * from table1"
    temp_expression: sqlglot.Expression = sqlglot.parse_one(updated_query)

    temp_with_expression = temp_expression.args.get('with')
    updated_cte_expression = temp_with_expression.args.get('expressions')[0]

    return updated_cte_expression


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
