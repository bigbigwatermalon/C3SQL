# C3SQL
The code for the paper C3: Zero-shot Text-to-SQL with ChatGPT ([https://arxiv.org/abs/2307.07306](https://arxiv.org/abs/2307.07306))

## Prepare Spider Data

Download [spider data](https://drive.google.com/uc?export=download&id=1TqleXec_OykOYFREKKtschzY29dUcVAQ) and database (only spider original database right now) and then unzip them:

```shell
mkdir data 
unzip spider.zip 
mv spider/database . 
mv spider data
```

### Run Inference 
Run the command below, and the predicted sql will be save to the file named "predicted_sql.txt"
```shell
bash submit.sh 
```
