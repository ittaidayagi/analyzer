class tryplugin:

    def __init__(self):

        self.start_tryplugin()

    def start_tryplugin(self):

        with open(r"c:\temp\tryplugin", "w") as tryplugin_file:
            tryplugin_file.write("good!")