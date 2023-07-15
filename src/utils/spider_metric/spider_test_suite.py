"""Spider Test Suite Execution Accuracy metric."""
import logging
import os
from typing import Optional, Dict, Any
from third_party.test_suite import evaluation as test_suite_evaluation
from third_party.test_suite.exec_eval import eval_exec_match
from third_party.test_suite.process_sql import get_schema, Schema, get_sql
from utils.print_tools import dprint

logger = logging.getLogger(__name__)


def compute_test_suite_metric(predictions, references, db_dir: Optional[str] = None) -> Dict[str, Any]:
    if db_dir is None:
        db_dir = references[0]["db_path"]
    foreign_key_maps = dict()
    for reference in references:
        if reference["db_id"] not in foreign_key_maps:
            foreign_key_maps[reference["db_id"]] = test_suite_evaluation.build_foreign_key_map(
                {
                    "table_names_original": reference["db_table_names"],
                    "column_names_original": list(
                        zip(
                            reference["db_column_names"]["table_id"],
                            reference["db_column_names"]["column_name"],
                        )
                    ),
                    "foreign_keys": list(
                        zip(
                            reference["db_foreign_keys"]["column_id"],
                            reference["db_foreign_keys"]["other_column_id"],
                        )
                    ),
                }
            )

    evaluator = test_suite_evaluation.Evaluator(
        db_dir=db_dir,
        kmaps=foreign_key_maps,
        etype="exec",
        plug_value=False,
        keep_distinct=False,
        progress_bar_for_each_datapoint=False,
    )
    # Only used for Sparc/CoSQL
    turn_scores = {"exec": [], "exact": []}
    for prediction, reference in zip(predictions, references):
        turn_idx = reference.get("turn_idx", 0)
        # skip final utterance-query pairs
        if turn_idx < 0:
            continue
        try:
            _ = evaluator.evaluate_one(
                reference["db_id"],
                reference["query"],
                prediction,
                turn_scores,
                idx=turn_idx,
            )
        except AssertionError as e:
            logger.warning(f"unexpected evaluation error: {e.args[0]}")
    evaluator.finalize()
    return {
        "exec": evaluator.scores["all"]["exec"],
    }


def compute_test_beam_metric(prediction_sets, references, db_dir: Optional[str] = None,
                             saved_result_path="predicted_sql_beam_acc.txt"):
    if db_dir is None:
        db_dir = references[0]["db_path"]
    db_paths = {}
    schemas = {}
    f = open(saved_result_path, "w", encoding='utf-8')
    single_cnt, beam_cnt, tot_num = 0, 0, len(references)
    for candidate_set, reference in zip(prediction_sets, references):
        db_name = reference["db_id"]
        gold = reference["query"]
        question = reference["question"]
        labels = []
        if db_name not in db_paths:
            db_path = os.path.join(db_dir, db_name, db_name + ".sqlite")
            db_paths[db_name] = db_path
            schemas[db_name] = Schema(get_schema(db_path))
        for id, predicted in enumerate(candidate_set):
            if predicted[:1] == "@":  # 不可执行的sql
                labels.append(-1)
                continue
            # 继续可执行的sql
            exec_score = eval_exec_match(
                db=db_paths[db_name],
                p_str=predicted,
                g_str=gold,
                plug_value=False,
                keep_distinct=False,
                progress_bar_for_each_datapoint=False
            )
            labels.append(exec_score)
            dprint(f'{exec_score} id: {id} pred: {predicted}   gold: {gold}', '3.1')
        dprint(f'', '3.1')
        if 1 not in labels:
            f.write("Correct: False\n")
        elif 0 not in labels or labels.index(1) < labels.index(0):
            f.write("Correct: True\n")
            single_cnt += 1
            beam_cnt += 1
        else:
            f.write("Correct: Beam True\n")
            beam_cnt += 1

        # if labels[0] == 1:
        #     f.write("Correct: True\n")
        #     single_cnt += 1
        #     beam_cnt += 1
        # elif sum(labels) != 0:
        #     f.write("Correct: Beam True\n")
        #     beam_cnt += 1
        # else:
        #     f.write("Correct: False\n")
        f.write(question + "\n")
        f.write("  " + gold + "\n")
        for label, predicted in zip(labels, candidate_set):
            f.write(str(label) + " " + predicted + "\n")
        f.write("\n")

    single_acc = single_cnt / tot_num
    beam_acc = beam_cnt / tot_num

    f.write("\n")
    f.write("single acc: {:.4}\n".format(single_acc))
    f.write("beam   acc: {:.4}".format(beam_acc))

    f.close()

    return single_acc, beam_acc

