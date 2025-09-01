
class GetClusterMetrics():
    def __init__(self):
        pass 

    def getKubeMetrics(self) -> dict:
        pass
    def getDataDogMetrics(self)-> dict:
        pass 
    def main(self)-> dict:
        return {
            "kube_metrics": self.getKubeMetrics,
            "data_dog_metrics": self.getDataDogMetrics
        }