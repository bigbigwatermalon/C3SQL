set -e

if [ ! -d "generate_datasets" ]; then
  mkdir generate_datasets
  echo "create directory generate_datasets"
else
  echo "directory generate_datasets already exists"
fi

tables=$1
dataset_path=$2
device="0"
db_path=$3
processed_dataset_path=$4
# preprocess test set
echo "preprocessing..."
python src/preprocessing.py \
    --mode "test" \
    --table_path $tables \
    --input_dataset_path $dataset_path \
    --output_dataset_path "./generate_datasets/preprocessed_data.json" \
    --db_path "$db_path" \
    --target_type "sql"

# recall tables
echo "recall tables..."
python src/table_recall.py \
    --input_dataset_path "./generate_datasets/preprocessed_data.json" \
    --output_recalled_tables_path "./generate_datasets/table_recall.json" \

# recall columns
echo "recall columns..."
python src/column_recall.py \
    --input_recalled_tables_path "./generate_datasets/table_recall.json" \
    --output_recalled_columns_path "./generate_datasets/column_recall.json" \

# generate prompt
echo "generate prompt..."
python src/prompt_generate.py \
    --input_dataset_path "./generate_datasets/column_recall.json" \
    --output_dataset_path $processed_dataset_path \

