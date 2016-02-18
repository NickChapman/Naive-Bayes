import random, math
import utils

class ArffProcessor(object):
    """Loads and manages an ARFF file"""
    
    def __init__(self, file_path):
        """Loads an ARFF file, fills in missing data points
        @param file_path: Path to the ARFF file
        """
        # Load the file into memory and do initial processing
        self.load_file(file_path)
        # Map the attributes to their positions in the data line
        self.map_attributes_to_num()
        # Remove '?' values from the data
        self.fill_holes()

    def load_file(self, file_path):
        """Loads an ARFF file into memory and extracts all information
        @param file_path: Path to the ARFF file
        """
        self.file_path = file_path
        # Open the file
        self.file = open(file_path, 'r')
        # Process the headers
        self.relation = ""
        self.attributes = [] # Contains tuple pairs of (attr_name, attr_values)
        self.data = []
        lines = self.file.readlines()
        headers_done = False
        for line in lines:
            # Remove leading and trailing whitespace
            line = line.strip()
            # Disregard commented out and blank lines
            if line.startswith("%") or line == "":
                continue
            if not headers_done:
                # Process the headers
                if line.lower().startswith("@"):
                    # @relation
                    if line.lower().startswith("@relation"):
                        # Make sure we are not already processing a relation
                        if self.relation != "":
                            raise IOError("The ARFF file contains more than one relation definition")
                        else:
                            self.relation = line.split()[1]
                    # @attribute
                    if line.lower().startswith("@attribute"):
                        attr_name = line.split()[1]
                        # Check to see if it is a nominal attribute
                        if "{" in line:
                            # Get rid of the { and }
                            clean_line = line.replace("{", "")
                            clean_line = clean_line.replace("}", "")
                            line_parts = clean_line.split(",")
                            # Remove pieces from the first one which has too much
                            values = []
                            values.append(line_parts[0].split()[-1])
                            for i in range(1, len(line_parts)):
                                values.append(line_parts[i].strip())
                            self.attributes.append((attr_name, values))
                        else:
                            # Numeric or string attribute
                            # NO SUPPORT FOR DATES AT PRESENT
                            values = line.lower().split()[-1]
                            self.attributes.append((attr_name, values))
                    # @data
                    if line.lower().startswith("@data"):
                        # Nothing to do, just means reading is about to commence
                        headers_done = True
            # Begin reading in data
            else:
                # Convert each data line into a list with the index corresponding to the attribute
                data_line = [x.strip() for x in line.split(",")]
                self.data.append(data_line)
        # Convert numeric data into actual numbers instead of strings
        self.map_attributes_to_num()
        for attr in self.attributes:
            attr_name = attr[0]
            type = attr[1]
            # The next if must be in this order to short circuit
            if (not isinstance(type, list)) and (type.lower() == "numeric"):
                # Convert that column into actual numbers
                for entry in self.data:
                    # We will try to convert it to an int first
                    try:
                        entry[self.attr_position[attr_name]] = int(entry[self.attr_position[attr_name]])
                    except ValueError:
                        # int conversion failed so make it a float
                        entry[self.attr_position[attr_name]] = float(entry[self.attr_position[attr_name]])
        self.file.close()

    def fill_holes(self):
        """ Finds holes in the data and fills them in
        Numeric values are filled in with the attribute mean
        Categorical values are filled in with the attribute mode
        """
        # This first call to map the attributes is potentially redundant
        # However, it's easier to just repeat this minimal step rather than catch errors
        # TODO: Optimize this call in some way
        self.map_attributes_to_num()
        for attribute in self.attributes:
            attr_name = attribute[0]
            attr_values = attribute[1]
            # Determine attribute type
            if isinstance(attr_values, list):
                # It's nominal
                # Create a counter for each nominal bin
                count = {}
                for label in attr_values:
                    count[label] = 0
                # Find out how many times each 
                for entry in self.data:
                    entry_label_value = entry[self.attr_position[attr_name]]
                    if entry_label_value == "?":
                        # Skip this one
                        continue
                    count[entry_label_value] += 1
                fill_choices = utils.get_dict_modes(count)
                # Now that we have our choices we will back fill missing values
                # We will choose from fill_choices at random
                for entry in self.data:
                    entry_label_value = entry[self.attr_position[attr_name]]
                    if entry_label_value == "?":
                        # Choose at random
                        entry[self.attr_position[attr_name]] = random.choice(fill_choices)
            elif attr_values.lower() == "numeric":
                total = 0
                entries = 0
                for entry in self.data:
                    entry_label_value = entry[self.attr_position[attr_name]]
                    if entry_label_value == "?":
                        # Skip this row
                        continue
                    total += entry_label_value
                    entries += 1
                average = total / entries
                # Now fill in this average where necessary
                for entry in self.data:
                    entry_label_value = entry[self.attr_position[attr_name]]
                    if entry_label_value == "?":
                        entry[self.attr_position[attr_name]] = average
            else:
                # TODO: Implement additional data type handlers
                # For now we will raise an exception if we make it to here because
                # something has definitely gone wrong in that case
                raise NotImplementedError("Need to implement handling for types beyond categorical and numeric")

    def entropy_discretize_single_numeric(self, numeric_attribute, core_attribute, gain_threshold=.05):
        self.map_attributes_to_num()
        # TODO

    def entropy_discretize_numerics(self, core_attribute, gain_threshold=.05):
        """ Converts all numerical attributes to categorical
        Uses entropy based discretization. 
        """
        self.map_attributes_to_num()
        for attribute in self.attributes:
            # We are only concerned with numeric attributes
            if attribute[1] == "numeric":
                attr_name = attribute[0]
                # Sort the data into ascending order based on that attribute
                self.data.sort(key=lambda x : x[self.attr_position[attr_name]])
                attr_ranges = []
                self.get_splits(0, len(self.data) - 1, attr_name, core_attribute, gain_threshold, attr_ranges)
                # We now have the bin ranges for this attribute
                # We need to create the bin objects for this attribute
                attr_bins = []
                for pair in attr_ranges:
                    lower_bound = self.data[pair[0]][self.attr_position[attr_name]]
                    upper_bound = self.data[pair[1]][self.attr_position[attr_name]]
                    attr_bins.append(utils.NumericalDataBin(gte=lower_bound, lt=upper_bound))
                # Sort the attribute bins on one of their bounds
                attr_bins.sort(key=lambda x : x.min)
                # Set the lowest bins minimum to -Infinity and the highest bins max to Infinity
                attr_bins[0].min = -float("inf")
                attr_bins[-1].max = float("inf")
                #Stitch the bins together to complete the continuous range
                for i in range(1, len(attr_bins)):
                    attr_bins[i].min = attr_bins[i - 1].max
                # Apply these bins to the data values
                for entry in self.data:
                    attr_value = entry[self.attr_position[attr_name]]
                    entry[self.attr_position[attr_name]] = self.get_bin(attr_bins, attr_value)
                # The attributes are tuples so we can't modify them
                # The following is a work around
                temp = list(attribute)
                temp[1] = attr_bins
                temp = tuple(temp)
                for i in range(len(self.attributes)):
                    if self.attributes[i][0] == temp[0]:
                        self.attributes[i] = temp
                        break
                        
        
    @staticmethod            
    def get_bin(bin_list, value):
        """Takes a list of NumericalDataBins and returns the bin for the value"""
        for bin in bin_list:
            if bin.belongs_to_bin(value):
                return bin
        # If we get here something has gone wrong
        raise AssertionError("A bin was not found for a data point. This should never happen")
                
    def get_splits(self, lower_index, upper_index, binning_attribute, core_attribute, gain_threshold, ranges):
        """ RANGES WILL CONTAIN ALL OF THE FINAL RANGE VALUES"""
        results = self.find_best_split(lower_index, upper_index, binning_attribute, core_attribute, gain_threshold)
        should_split = results[0]
        lower_range = results[1]
        upper_range = results[2]
        if not should_split:
            ranges.append((lower_index, upper_index))
        else:
            # Find the index where the split occurs
            split_value = lower_range[1]
            split_index = lower_index
            for i in range(lower_index + 1, upper_index + 1):
                if self.data[i][self.attr_position[binning_attribute]] >= split_value:
                    break
                else:
                    split_index += 1
            self.get_splits(lower_index, split_index, binning_attribute, core_attribute, gain_threshold, ranges)
            self.get_splits(split_index + 1, upper_index, binning_attribute, core_attribute, gain_threshold, ranges)
                    
    def find_best_split(self, lower_index, upper_index, binning_attribute, core_attribute, gain_threshold):
        """ ASSUMES DATA IS SORTED ON BINNING_ATTRIBUTE
        @returns a tuple of one bool and 2 range tuples: (should_split, (min_value, ideal_split), (ideal_split, max_value))
        """
        # If lower_index == upper_index then obviously there is nothing to split so should_split = false and we move on
        if lower_index == upper_index:
            return (False, (lower_index, lower_index), (lower_index, lower_index))
        # Get the bins starting entropy
        # TODO: Correct the following assumption
        # Assume that core_attributes are always categorical
        overall_entropy = self.entropy(lower_index, upper_index, float("inf"), binning_attribute, core_attribute)
        # best split is initially the first split
        ideal_split = (self.data[lower_index][self.attr_position[binning_attribute]] 
                       + self.data[lower_index + 1][self.attr_position[binning_attribute]]) / 2
        ideal_entropy = self.entropy(lower_index, upper_index, ideal_split, binning_attribute, core_attribute)
        # Calculate the entropy for a number of possible splits
        # We set a limit because otherwise this takes wayyyyy too long
        step = max(1, (upper_index - (lower_index + 1)) // int(10*math.log10(upper_index - (lower_index)) + 1))
        for i in range(lower_index + 1, upper_index, step):
            split = (self.data[i][self.attr_position[binning_attribute]] 
                       + self.data[i + 1][self.attr_position[binning_attribute]]) / 2
            split_entropy = self.entropy(lower_index, upper_index, split, binning_attribute, core_attribute)
            if split_entropy < ideal_entropy:
                ideal_split = split
                ideal_entropy = split_entropy
        # Determine whether it is worth it to split up this range
        should_split = False
        if (overall_entropy - ideal_entropy) >= gain_threshold:
            should_split = True
        range_min = self.data[lower_index][self.attr_position[binning_attribute]]
        range_max = self.data[upper_index][self.attr_position[binning_attribute]]
        return (should_split, (range_min, ideal_split), (ideal_split, range_max))

    def entropy(self, lower_index, upper_index, split_point, binning_attribute, core_attribute):
        """ Determines entropy of a given split
        ASSUMES DATA IS SORTED ON BINNING_ATTRIBUTE """
        sample_size = upper_index - lower_index + 1;
        probabilities = {}
        net_entropy = 0;
        lower_entropy = 0
        upper_entropy = 0
        lower_bin_size = 0
        upper_bin_size = 0
        # Get entropy for the bin less than split_point
        for attr_value in self.attributes[self.attr_position[core_attribute]][1]:
            # Ensuring that none of the probabilities come out to 0 ensures the entropy calculation works
            probabilities[attr_value] = .5
        # Count the occurences of each core attribute value in the lower range
        for i in range(lower_index, upper_index + 1):
            if self.data[i][self.attr_position[binning_attribute]] < split_point:
                probabilities[self.data[i][self.attr_position[core_attribute]]] += 1
                lower_bin_size += 1
        # Perform the actual entropy calculation
        if lower_bin_size == 0:
            lower_entropy = 0
        else:
            for attr_value in probabilities:
                p = probabilities[attr_value] / lower_bin_size
                lower_entropy += p * math.log2(p)
        # Multiply the result by negative 1 to factor in the fact that it is -Sum...
        lower_entropy *= -1

        # Repeat for the upper bin
        # Get entropy for the bin greater than or equal to split_point
        for attr_value in self.attributes[self.attr_position[core_attribute]][1]:
            # Ensuring that none of the probabilities come out to 0 ensures the entropy calculation works
            probabilities[attr_value] = .5
        # Count the occurences of each core attribute value in the lower range
        for i in range(lower_index, upper_index + 1):
            if self.data[i][self.attr_position[binning_attribute]] >= split_point:
                probabilities[self.data[i][self.attr_position[core_attribute]]] += 1
                upper_bin_size += 1
        # Perform the actual entropy calculation
        if upper_bin_size == 0:
            upper_entropy = 0
        else:    
            for attr_value in probabilities:
                p = probabilities[attr_value] / upper_bin_size
                upper_entropy += p * math.log2(p)
        # Multiply the result by negative 1 to factor in the fact that it is -Sum...
        upper_entropy *= -1.0

        # Calculate the net entropy
        net_entropy = lower_bin_size / sample_size * lower_entropy + upper_bin_size / sample_size * upper_entropy
        return net_entropy

    def map_attributes_to_num(self):
        """Maps the attribute to its position in a data line"""
        self.attr_position = {}
        for i, attribute in enumerate(self.attributes):
            attr_name = attribute[0]
            self.attr_position[attr_name] = i