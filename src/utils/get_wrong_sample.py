
with open("../results/predicted_sql_beam_acc_t5_3b.txt", "r") as f:
    dataset = f.readlines()

start_ids = []
for id, line in enumerate(dataset):
    if line.startswith("Correct:"):
        start_ids.append(id)
start_ids.append(-1)

blocks = []
for i in range(len(start_ids) - 1):
    be_id, ed_id = start_ids[i], start_ids[i+1]
    blocks.append(dataset[be_id: ed_id-1])

print(blocks[0])
print(blocks[-1])

with open("../results/processed_natsql_beam_acc_t5_3b.txt") as f:
    g_sql_dataset = f.readlines()
g_sqls = []
for i, line in enumerate(g_sql_dataset):
    if "Correct:" in line:
        g_sqls.append(g_sql_dataset[i+1])

save_data = []
for i, block in enumerate(blocks):
    example = []
    candidates = block[3:]
    select_id = 0
    for j, line in enumerate(candidates):
        if line[0] == "1" or line[0] == "0":
            select_id = j
            break
    candidate = candidates[select_id]
    if candidate[0] == "-":
        candidate = candidate[4:]
    else:
        candidate = candidate[2:]
    if block[0] == "Correct: False\n":
        example.extend([
            f"id: {i+1}\n",
            block[0],
            block[1],
            f"gold_sql: {g_sqls[i]}",
            f"pred_sql: {candidate}",
        ])
        save_data.append(example)
        print(example)


with open("../results/to_xm.txt", "w") as f:
    for block in save_data:
        for line in block:
            f.write(line)
        f.write("\n")

