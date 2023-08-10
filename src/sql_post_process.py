

def fix_select_column(sql):
    # sql = "SELECT DISTINCT model FROM cars_data JOIN car_names ON cars_data.id = car_names.makeid JOIN model_list ON car_names.model = model_list.model WHERE year > 1980;"
    sql = sql.replace("\n", " ")
    sql_list = sql.split("=")  # 给等号两边腾出空格
    sql = " = ".join(sql_list)
    while "  " in sql:
        sql = sql.replace("  ", " ")
    sql_tokens = sql.split(" ")
    select_ids = []
    from_ids = []
    join_ids = []
    eq_ids = []
    first_where_id = -1
    first_group_by_id = -1
    first_having_id = -1
    for id, token in enumerate(sql_tokens):
        if token.lower() == "select":
            select_ids.append(id)
        if token.lower() == "from":
            from_ids.append(id)
        if token.lower() == "join":
            join_ids.append(id)
        if token.lower() == "=":
            eq_ids.append(id)
        if token.lower() == "where" and first_where_id == -1:
            first_where_id = id
        if token.lower() == "group" and id < len(sql_tokens) - 1 and sql_tokens[id+1].lower() == "by" and first_group_by_id == -1:
            first_group_by_id = id
        if token.lower() == "having" and first_having_id == -1:
            first_having_id = id

    if len(eq_ids) == 0 or len(join_ids) == 0:
        return sql
    # assert len(select_ids) == len(from_ids)
    for i in range(len(select_ids[:1])):  ## 先只考虑最外层的select
        select_id = select_ids[i]
        from_id = from_ids[i]
        tmp_column_ids = [i for i in range(select_id + 1, from_id)]
        column_ids = []
        id = 0
        while id < len(tmp_column_ids):
            item = sql_tokens[id]
            if item.lower() == "as":
                id += 2
                continue
            column_ids.append(tmp_column_ids[id])
            id += 1
        column_table_mp = {}
        if i == len(select_ids) - 1:  # last select
            for j in range(len(join_ids)):
                if (first_where_id != -1 and join_ids[j] > first_where_id) or first_group_by_id != -1 and join_ids[j]:
                    break
                eq_id = eq_ids[j]
                left_id, right_id = eq_id - 1, eq_id + 1
                left_column, right_column = sql_tokens[left_id], sql_tokens[right_id]
                if "." not in left_column or "." not in right_column:
                    continue
                column_left = left_column.split(".")[1]
                column_right = right_column.split(".")[1]
                column_table_mp[column_left] = left_column
                column_table_mp[column_right] = right_column
        else:
            pass

        if len(column_table_mp) == 0:
            return sql
        for column_id in column_ids:
            column = sql_tokens[column_id]
            if "." not in column:
                if column in column_table_mp.keys():
                    sql_tokens[column_id] = column_table_mp[column]
                elif len(column) > 0 and column[-1] == "," and column[:-1] in column_table_mp.keys():
                    sql_tokens[column_id] = column_table_mp[column[:-1]] + ","

    recovered_sql = " ".join(sql_tokens)

    return recovered_sql


