from arffreader.ArffProcessor import ArffProcessor
from NaiveBayes import NaiveBayesClassifier

arff = ArffProcessor("adult-small.arff")
arff.entropy_discretize_numerics("class", gain_threshold=.01)
print("DONE LOADING")
nb = NaiveBayesClassifier(arff)
nb.build_model("class")
print("DONE BUILDING MODEL")
