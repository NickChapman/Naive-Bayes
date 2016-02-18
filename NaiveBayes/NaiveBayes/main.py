from arffreader.ArffProcessor import ArffProcessor
from NaiveBayes import NaiveBayesClassifier
import copy
import random

print("LOADING AND PROCESSING ARFF DATA")
arff = ArffProcessor("adult-big.arff")
arff.entropy_discretize_numerics("class", gain_threshold=.01)
print("DONE PREPARING DATA")

print("SELECTING TRAINING DATA")
# We just need to remove a random 10% of records from arff.data
ten_percent = len(arff.data) // 10
training_records = []
for i in range(ten_percent):
    index = random.randrange(len(arff.data))
    training_records.append(arff.data.pop(index))
print("DONE SELECTING TRAINING DATA")

print("BUILDING MODEL")
nb = NaiveBayesClassifier(arff)
nb.build_model("class")
print("DONE BUILDING MODEL")

confusion_matrices = {}
for core_value in arff.attributes[arff.attr_position["class"]][1]:


for record in training_records:
    classification = nb.classify_record(record)
    if classification == record[arff.attr_position["class"]]:
        TP += 1
    elif :
        failure += 1
total = success + failure
print("Success: " + str(success))
print("Failure: " + str(failure))
print("Total:   " + str(total))
