def generate_reranker_results(dataset_dir, labels_dir, saved_dir):
    blocks = []
    with open(dataset_dir, 'r') as f:
        dataset = f.readlines()
    # with open("../results/processed_natsql_beam_acc_t5_base.txt", "r") as f:
    #     dataset = f.readlines()
    start_ids = [0]
    for id, line in enumerate(dataset):
        # print(line, end='')
        if line == '\n':
            start_ids.append(id+1)
    for i in range(len(start_ids) - 1):
        be_id, ed_id = start_ids[i], start_ids[i + 1]
        blocks.append(dataset[be_id: ed_id - 1])
    print(blocks[0])
    print(blocks[25])
    print(blocks[-2])
    print(blocks[-1])
    blocks[-1] = blocks[-1][:-1]
    with open(labels_dir, "r") as f:
        labels_data = f.readlines()

    labels_for_all = []
    top_one_indices = []

    for i in range(0, len(labels_data), 4):
        labels = eval(labels_data[i+1])
        labels_for_all.append(labels)
        # print(labels)
        top_one_index = labels.index(max(labels))
        # print(top_one_index)
        # print(len(labels))
        top_one_indices.append(top_one_index)

    # print(blocks[0])
    # print(len(blocks))
    # print(len(labels_for_all))

    with open(saved_dir, "w") as f:
        true_number, beam_number, false_number = 0, 0, 0
        true_samples, beam_samples, false_samples = [], [], []
        add_info = "&"
        for id, block in enumerate(blocks):
            write_content_list = []
            write_content_list.append(f"{block[0][:-1]} | reranked index: {top_one_indices[id]} | {add_info}")
            data_type = ''
            case_info1 = ''
            case_info2 = ''
            if block[1][:1] == '1':
                data_type = 'Correct: True | '
                true_number += 1
                case_info1 = 'T, '
            for i, line in enumerate(block[1:]):
                write_content_list.append('{:.4f} | '.format(labels_for_all[id][i]))
                write_content_list.append(line)
                if (not data_type) and line[:1] == '1':
                    data_type = "Correct: Beam True | "
                    beam_number += 1
                    case_info1 = 'B, '
                if i == top_one_indices[id]:
                    if line[:1] != '1':
                        # print(block)
                        write_content_list[0] += " False\n"
                        case_info2 = 'F | '
                    else:
                        write_content_list[0] += " True\n"
                        case_info2 = 'T | '
            if not data_type:
                data_type = "Correct: False | "
                false_number += 1
                case_info1 += 'F, '
                continue
            write_content_list[0] = data_type + case_info1 + case_info2 + write_content_list[0]
            write_content_list.append("\n")
            for content in write_content_list:
                f.write(content)

        print(true_number, beam_number, false_number)
        # print(sum(true_samples), sum(beam_samples), sum(false_samples))