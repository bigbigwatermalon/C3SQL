

def fix_select_column(sql):
    # sql = "SELECT DISTINCT model FROM cars_data JOIN car_names ON cars_data.id = car_names.makeid JOIN model_list ON car_names.model = model_list.model WHERE year > 1980;"
    sql = sql.replace("\n", " ")
    sql_list = sql.split("=")  # 给等号两边腾出空格
    sql = " = ".join(sql_list)
    while "  " in sql:
        sql = sql.replace("  ", " ")
    # print(f'sql: {sql}')
    sql_tokens = sql.split(" ")
    # print(sql_tokens)
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
    # print(f'select_ids : {select_ids}')
    # print(f'from_ids: {from_ids}')
    # print(f'join_ids: {join_ids}')
    # print(f'eq_ids: {eq_ids}')
    # print(f'first_where_id: {first_where_id}')
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
        # print(columns)
        # print(column_ids)
        column_table_mp = {}
        if i == len(select_ids) - 1:  # last select
            for j in range(len(join_ids)):
                # print(f'j: {j}')
                if (first_where_id != -1 and join_ids[j] > first_where_id) or first_group_by_id != -1 and join_ids[j]:
                    break
                eq_id = eq_ids[j]
                left_id, right_id = eq_id - 1, eq_id + 1
                left_column, right_column = sql_tokens[left_id], sql_tokens[right_id]
                if "." not in left_column or "." not in right_column:
                    continue
                # print(left_column, right_column)
                # print(left_column.split("."))
                column_left = left_column.split(".")[1]
                column_right = right_column.split(".")[1]
                column_table_mp[column_left] = left_column
                column_table_mp[column_right] = right_column
        else:
            pass

        # print(column_table_mp)
        if len(column_table_mp) == 0:
            return sql
        for column_id in column_ids:
            column = sql_tokens[column_id]
            if "." not in column:
                # print(f'column: {column}')
                if column in column_table_mp.keys():
                    sql_tokens[column_id] = column_table_mp[column]
                elif len(column) > 0 and column[-1] == "," and column[:-1] in column_table_mp.keys():
                    sql_tokens[column_id] = column_table_mp[column[:-1]] + ","
        # print(sql_tokens)

    recovered_sql = " ".join(sql_tokens)
    # print(recovered_sql)

    return recovered_sql


# print(fix_select_column("SELECT song_name, song_release_year  FROM singer  WHERE age = (SELECT MIN(age) FROM singer)"))
#
# score = eval_exec_match(
#     "./Spider/database/world_1/world_1.sqlite",
#     "SELECT CountryCode ,  max(Percentage) FROM countrylanguage WHERE LANGUAGE  =  'Spanish' GROUP BY CountryCode".lower(),
#     'SELECT CountryCode ,  max(Percentage) FROM countrylanguage WHERE LANGUAGE  =  "Spanish" GROUP BY CountryCode'.lower(),
#     False,
#     False,
#     False
# )
#
# print(score)

# print(fix_select_column("SELECT airlines.airline FROM airlines JOIN flights ON flights.airline=airlines.airline WHERE flights.sourceairport='AHD')"))

# print(fix_select_column("SELECT stadium.name, stadium.location FROM stadium INNER JOIN concert ON stadium.stadium_id = concert.stadium_id WHERE concert.year = 2014 AND stadium.stadium_id IN  (SELECT stadium.stadium_id FROM stadium  INNER JOIN concert ON stadium.stadium_id = concert.stadium_id WHERE concert.year = 2015)"))

# print(fix_select_column("SELECT car_names.make, MIN(cars_data.year) AS production_time FROM car_names  JOIN cars_data ON car_names.makeid=cars_data.id GROUP BY car_names.make HAVING production_time = (SELECT MIN(year) FROM cars_data)"))

# print(fix_select_column("SELECT players.first_name, players.last_name FROM players INNER JOIN matches AS m1 ON players.player_id = m1.winner_id AND m1.year = 2013 INNER JOIN matches AS m2 ON players.player_id = m2.winner_id AND m2.year = 2016"))

# print(fix_select_column("SELECT name FROM stadium LEFT JOIN (SELECT stadium_id FROM concert WHERE year = 2014) AS c ON stadium.stadium_id = c.stadium_id WHERE c.stadium_id IS NULL;"))