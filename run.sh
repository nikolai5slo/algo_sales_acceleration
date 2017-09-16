#!/bin/bash

runTimestamp=$(date +%s)
samplesCount=${1:-3}
filtering=${2:-50}

echo "Run $runTimestamp ($samplesCount, $filtering):"
mkdir -p ./results/$runTimestamp

echo "Predicting buyers with graph..."
python3 predict_buyers.py $samplesCount $filtering "./results/$runTimestamp/predict_buyers.pkl" > ./results/$runTimestamp/predict_buyers.out &
echo "Predicting buyers with category..."
python3 predict_buyers_category.py $samplesCount $filtering "./results/$runTimestamp/predict_buyers_category.pkl" > ./results/$runTimestamp/predict_buyers_category.out &
echo "Predicting buyers with data mining..."
python3 predict_buyers_mining.py $samplesCount $filtering "./results/$runTimestamp/predict_buyers_mining.pkl" > ./results/$runTimestamp/predict_buyers_mining.out &
echo "Predicting buyers with random method..."
python3 predict_buyers_random.py $samplesCount $filtering "./results/$runTimestamp/predict_buyers_random.pkl" > ./results/$runTimestamp/predict_buyers_random.out &

echo "Predicting buyers with hybrid method..."
python3 predict_combined.py $samplesCount $filtering "./results/$runTimestamp/predict_buyers_hybrid.pkl" > ./results/$runTimestamp/predict_buyers_hybrid.out

echo "Predicting products with graph..."
python3 predict_products.py $samplesCount $filtering "./results/$runTimestamp/predict_products.pkl" > ./results/$runTimestamp/predict_products.out &
echo "Predicting products with random method..."
python3 predict_products_random.py $samplesCount $filtering "./results/$runTimestamp/predict_products_random.pkl" > ./results/$runTimestamp/predict_products_random.out &
echo "Predicting products with category..."
python3 predict_products_category.py $samplesCount $filtering "./results/$runTimestamp/predict_products_category.pkl" > ./results/$runTimestamp/predict_products_category.out &
echo "Predicting products with data mining..."
python3 predict_products_mining.py $samplesCount $filtering "./results/$runTimestamp/predict_products_mining.pkl" > ./results/$runTimestamp/predict_products_mining.out &
wait