class Track:
    def __init__(self):
        self.elements = []
        self.total_length = 0

    def add_element(self, element):
        self.elements.append(element)
        self.total_length += element.length

    def remove_element(self, index):
        if 0 <= index < len(self.elements):
            element = self.elements.pop(index)
            self.total_length -= element.length

    def get_elements(self):
        return self.elements

    def clear(self):
        self.elements = []
        self.total_length = 0
