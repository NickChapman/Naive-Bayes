from arffreader.ArffProcessor import ArffProcessor
from NaiveBayes import NaiveBayesClassifier
import copy
import random
import utils

print("LOADING AND PROCESSING ARFF DATA")
arff = ArffProcessor("adult-big.arff")
# Remove '?' values from the data
arff.fill_holes("class")
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
    confusion_matrices[core_value] = {}
for core_value in arff.attributes[arff.attr_position["class"]][1]:
    confusion_matrices[core_value]["tp"] = 0
    confusion_matrices[core_value]["tn"] = 0
    confusion_matrices[core_value]["fp"] = 0
    confusion_matrices[core_value]["fn"] = 0

for record in training_records:
    classification = nb.classify_record(record)
    if classification == record[arff.attr_position["class"]]:
        # This is a TP for this classification
        confusion_matrices[classification]["tp"] += 1
        # A TP for this one is in essence a tn for all other classifications
        for core_value in arff.attributes[arff.attr_position["class"]][1]:
            if core_value != classification:
                confusion_matrices[core_value]["tn"] += 1
    else:
        # This is a false positive for this classification
        confusion_matrices[classification]["fp"] += 1
        # A FP for this one is a FN for the correct one
        confusion_matrices[record[arff.attr_position["class"]]]["fn"] += 1

print("Accuracy: " + str(utils.accuracy(arff.attributes[arff.attr_position["class"]][1], confusion_matrices)))
#print("Success: " + str(success))
#print("Failure: " + str(failure))
#print("Total:   " + str(total))
