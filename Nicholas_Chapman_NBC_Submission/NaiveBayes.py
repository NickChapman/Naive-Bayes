from arffreader.ArffProcessor import ArffProcessor, utils

class NaiveBayesClassifier():
    def __init__(self, training_arff):
        if not isinstance(training_arff, ArffProcessor):
            raise TypeError("The training_arff argument must be an ArffProcessor")
        self.arff = training_arff

    def build_model(self, core_attribute):
        # Make sure that the core_attribute to classify on is categorical
        if not isinstance(self.arff.attributes[self.arff.attr_position[core_attribute]][1], list):
            raise TypeError("The core_attribute must be categorical")
        self.core_attribute = core_attribute
        # Compute all of the probabilities
        self.core_probabilities = {}
        for attr_value in self.arff.attributes[self.arff.attr_position[core_attribute]][1]:
            self.core_probabilities[attr_value] = 0
        for entry in self.arff.data:
            entry_core_value = entry[self.arff.attr_position[core_attribute]]
            self.core_probabilities[entry_core_value] += 1
        # Compute the attribute value probabilities
        self.probabilities = {}
        for core_value in self.arff.attributes[self.arff.attr_position[core_attribute]][1]:
            self.probabilities[core_value] = {}
            for attribute in self.arff.attributes:
                # Make sure we are not on the core attribute
                attr_name = attribute[0]
                if attr_name != self.core_attribute:
                    for attr_value in attribute[1]:
                        self.probabilities[core_value][attr_value] = 0.5
                        # We set .5 to prevent 0 probabilities from destroying everything
                        # "Data Smoothing" - Google it man
        for entry in self.arff.data:
            entry_core_value = entry[self.arff.attr_position[self.core_attribute]]
            for i in range(len(entry)):
                if i != self.arff.attr_position[self.core_attribute]:
                    entry_attr_value = entry[i]
                    self.probabilities[entry_core_value][entry_attr_value] += 1

    def pc(self, core_attribute_value):
        return self.core_probabilities[core_attribute_value] / len(self.arff.data)

    def pxc(self, attr_value, core_attribute_value):
        # The following smooths these probabilities
        if self.core_probabilities[core_attribute_value] == 0:
            return self.probabilities[core_attribute_value][attr_value]
        else:
            return self.probabilities[core_attribute_value][attr_value]/self.core_probabilities[core_attribute_value]

    def classify_record(self, record):
        """Record is an array that must match the format of the arff data records"""
        classifications = {}
        for core_value in self.arff.attributes[self.arff.attr_position[self.core_attribute]][1]:
            classifications[core_value] = self.pc(core_value)
            for i in range(len(record)):
                if i != self.arff.attr_position[self.core_attribute]:
                    classifications[core_value] *= self.pxc(record[i], core_value)
        best_classifier = ""
        best_classifier_score = 0
        for core_value in classifications:
            if classifications[core_value] > best_classifier_score:
                best_classifier_score = classifications[core_value]
                best_classifier = core_value
        return best_classifier
