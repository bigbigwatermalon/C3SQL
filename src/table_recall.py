import json
import argparse
import openai
import time
from tqdm import tqdm
from collections import Counter

# add your openai api key
openai.api_key = "sk-"


def parse_option():
    parser = argparse.ArgumentParser("command line arguments for recall tables")
    parser.add_argument("--input_dataset_path", type=str, default='../generate_datasets/preprocessed_test.json')
    parser.add_argument("--self_consistent", type=bool, default=True)
    parser.add_argument("--n", type=int, default=10,
                        help="Size of self-consistent set")
    parser.add_argument("--output_recalled_tables_path", type=str)

    opt = parser.parse_args()

    return opt


def generate_reply(input, sc_num):
    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=input,
        # top_p=0.5
        temperature=0.7,
        n=sc_num
        # stop=["Q:"]
    )
    all_tables = []
    for i in range(sc_num):
        raw_table = completions.choices[i].message.content
        try:
            raw_table = '[' + raw_table.split('[', 1)[1]
            raw_table = raw_table.rsplit(']', 1)[0] + ']'
            raw_table = eval(raw_table)
            if Ellipsis in raw_table:
                raw_table.remove(Ellipsis)
        except:
            print('list error')
            return None
        all_tables.append(raw_table)
    return all_tables
    # return completions.choices[0].message.content


def generate_schema(data):
    schema = ""
    for table in data['db_schema']:
        schema += '# ' + table['table_name_original'] + ' ( '
        for i, column in enumerate(table['column_names_original']):
            schema += column
            if table['db_contents'][i]:
                schema += ' ( '
                for value in table['db_contents'][i]:
                    schema += value + ', '
                schema = schema[:-2] + ' )'
            schema += ', '
        schema = schema[:-2] + ' )\n'
    return schema


def table_sc(tables_all, tables_ori):
    tables_sc = []
    for id, tables in enumerate(tables_all):
        tables_exist = []
        for table in tables:
            if table.lower() in tables_ori:
                tables_exist.append(table.lower())
                if len(tables_exist) == 4:
                    break
            # print(tables_exist)
            tables_sc.append(tables_exist)
    counts = Counter(tuple(sorted(lst)) for lst in tables_sc)
    most_list, count = counts.most_common(1)[0]
    for table_list in tables_sc:
        if sorted(table_list) == list(most_list):
            return table_list


def info_generate(tables, data):
    info = {}
    info['db_id'] = data['db_id']
    info['question'] = data['question']
    info['db_schema'] = []
    info['fk'] = []
    for table in tables:
        for tab_ori in data['db_schema']:
            if table == tab_ori['table_name_original'].lower():
                info['db_schema'].append(tab_ori)
                break
    for fk in data['fk']:
        if fk['source_table_name_original'] in tables and fk['target_table_name_original'] in tables:
            fk_str = fk['source_table_name_original'] + '.' + fk['source_column_name_original'] + ' = ' \
                     + fk['target_table_name_original'] + '.' + fk['target_column_name_original']
            info['fk'].append(fk_str)
    return info


instruction = """Given the database schema and question, perform the following actions: 
1 - Rank all the tables based on the possibility of being used in the SQL according to the question from the most relevant to the least relevant, Table or its column that matches more with the question words is highly relevant and must be placed ahead.
2 - Check whether you consider all the tables.
3 - Output a list object in the order of step 2, Your output should contain all the tables. The format should be like: 
[
    "table_1", "table_2", ...
]

"""

if __name__ == "__main__":
    opt = parse_option()
    print(opt)
    with open(opt.input_dataset_path) as f:
        data_all = json.load(f)
    res = []
    if opt.self_consistent:
        sc_num = opt.n
    else:
        sc_num = 1
    for i, data in enumerate(tqdm(data_all)):
        schema = generate_schema(data)
        prompt = instruction + "Schema:\n" + schema + "\n"
        prompt += "Question:\n" + data["question"]
        tables_all = None
        while tables_all is None:
            try:
                tables_all = generate_reply([{"role": "user", "content": prompt}], sc_num)
            except:
                print(f'api error, wait for 3 seconds and retry...')
                time.sleep(3)
                pass
        tables_ori = []
        for table in data['db_schema']:
            tables_ori.append(table['table_name_original'].lower())
        tables = table_sc(tables_all, tables_ori)
        info = info_generate(tables, data)
        res.append(info)
    with open(opt.output_dataset_path, 'w') as f:
        json.dump(res, f, indent=2)
