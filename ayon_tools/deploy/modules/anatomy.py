

class Anatomy:
    def __init__(self, data):
        self.data = data

    def set_templates(self, templates):
        ...

    def set_tasks(self, tasks):
        ...

    def set_statuses(self, statuses):
        ...

    def update_from_shortcut(self, data):
        ...

    def __eq__(self, other):
        return self.data == other.data
