#!/bin/bash

runTimestamp=$(date +%s)
echo "Run $runTimestamp:"
mkdir -p ./results/$runTimestamp
echo "Predicting buyers with graph..."
python3 predict_buyers.py > ./results/$runTimestamp/predict_buyers.out
echo "Predicting buyers with category..."
python3 predict_buyers_category.py > ./results/$runTimestamp/predict_buyers_category.out
echo "Predicting buyers with data mining..."
python3 predict_buyers_mining.py > ./results/$runTimestamp/predict_buyers_mining.out
echo "Predicting products with graph..."
python3 predict_products.py > ./results/$runTimestamp/predict_products.out
echo "Predicting buyers with random method..."
python3 predict_buyers_random.py > ./results/$runTimestamp/predict_buyers_random.out
