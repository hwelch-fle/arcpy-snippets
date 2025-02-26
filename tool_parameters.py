from arcpy import Parameter

class MyToolbox:
    def __init__(self):
        self.label = "Toolbox Label"
        self.alias = "Toolbox Alias"
        self.tools = [MyTool]

class MyTool:
    def __init__(self) -> None:
        self.category = "Tool Category"
        self.description = "Tool Description"
        self.label = "Tool Name"
        
    def getParameterInfo(self) -> list[Parameter]:
        p1 = Parameter(
            displayName="Input Features",
            name="input_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        return [p1]
    
    def isLicensed(self) -> bool:
        return True
    
    def updateParameters(self, parameters: list[Parameter]) -> None:
        """Modify the values and properties of parameters before internal validation is performed"""
        ...
    
    def updateMessages(self, parameters) -> None:
        """Modify or update messages created by internal validation"""
        ...

    def execute(self, parameters: list[Parameter], messages: list) -> None:
        """The main tool script"""
        ...
    
    def postExecute(self):
        """Runs after the script has finished executing"""
        ...