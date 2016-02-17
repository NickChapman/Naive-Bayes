import random.choice
import utils

class ArffFile(object):
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
                count = []
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


    def map_attributes_to_num(self):
        """Maps the attribute to its position in a data line"""
        self.attr_position = {}
        for i, attribute in enumerate(self.attributes):
            attr_name = attribute[0]
            self.attr_position[attribute_name] = i    