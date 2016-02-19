from arffreader.ArffProcessor import ArffProcessor
from NaiveBayes import NaiveBayesClassifier
import copy
import random
import utils

NUMBER_OF_TRIALS = 10
GAIN_THRESHOLD = .01
DATA_FILE = "adult-big.arff"

print("LOADING AND PROCESSING ARFF DATA")
arff = ArffProcessor(DATA_FILE)
# Remove '?' values from the data
arff.fill_holes("class")
arff.entropy_discretize_numerics("class", gain_threshold=GAIN_THRESHOLD)
print("DONE PREPARING DATA")

validation_results = []
for run_num in range(1, NUMBER_OF_TRIALS + 1):
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
    
    results_dict = {}
    results_dict["mp"] = utils.micro_precision(arff.attributes[arff.attr_position["class"]][1], confusion_matrices)
    results_dict["mr"] = utils.micro_recall(arff.attributes[arff.attr_position["class"]][1], confusion_matrices)
    results_dict["mf1"] = utils.micfo_f1(arff.attributes[arff.attr_position["class"]][1], confusion_matrices)
    results_dict["Mp"] = utils.macro_precision(arff.attributes[arff.attr_position["class"]][1], confusion_matrices)
    results_dict["Mr"] = utils.macro_recall(arff.attributes[arff.attr_position["class"]][1], confusion_matrices)
    results_dict["Mf1"] = utils.macro_f1(arff.attributes[arff.attr_position["class"]][1], confusion_matrices)
    results_dict["ac"] = utils.accuracy(arff.attributes[arff.attr_position["class"]][1], confusion_matrices)
    
    print("Micro Precision  " + str(run_num) + ": " + str(results_dict["mp"]))
    print("Micro Recall     " + str(run_num) + ": " + str(results_dict["mr"]))
    print("Micro F1         " + str(run_num) + ": " + str(results_dict["mf1"]))
    print("Macro Precision  " + str(run_num) + ": " + str(results_dict["Mp"]))
    print("Macro Recall     " + str(run_num) + ": " + str(results_dict["Mr"]))
    print("Macro F1         " + str(run_num) + ": " + str(results_dict["Mf1"]))
    print("Accuracy         " + str(run_num) + ": " + str(results_dict["ac"]))

    validation_results.append(results_dict)

    # Push the test data back into the training data
    arff.data.extend(training_records)

# Get the averages
avgs = {}
for result in validation_results:
    for k in result.keys():
        avgs[k] = avgs.get(k,0) + result[k]/len(validation_results)
validation_results.append(avgs)

# Print the table for the tests
# Print the header
print("\n\n")
print("Run # | Micro Precision | Micro Recall | Micro F1 | Macro Precision | Macro Recall | Macro F1 | Accuracy")
print("--------------------------------------------------------------------------------------------------------")
for i in range(len(validation_results)):
    if i != len(validation_results) - 1:
        run_format = str(i + 1).zfill(4).rjust(5) + " |"
    else:
        run_format = "Avg".rjust(5) + " |"
    micro_precision_format = "{num:.6f}".format(num=validation_results[i]["mp"]).zfill(7).rjust(16) + " |"
    micro_recall_format = "{num:.6f}".format(num=validation_results[i]["mr"]).zfill(7).rjust(13) + " |"
    micro_f1_format = "{num:.6f}".format(num=validation_results[i]["mf1"]).zfill(7).rjust(9) + " |"
    macro_precision_format = "{num:.6f}".format(num=validation_results[i]["Mp"]).zfill(7).rjust(16) + " |"
    macro_recall_format = "{num:.6f}".format(num=validation_results[i]["Mr"]).zfill(7).rjust(13) + " |"
    macro_f1_format = "{num:.6f}".format(num=validation_results[i]["Mf1"]).zfill(7).rjust(9) + " |"
    accuracy_format = "{num:.6f}".format(num=validation_results[i]["ac"]).zfill(7).rjust(9)
    if i == len(validation_results) - 1:
        print("--------------------------------------------------------------------------------------------------------")
    print(run_format + micro_precision_format + micro_recall_format + micro_f1_format + macro_precision_format + macro_recall_format + macro_f1_format + accuracy_format)