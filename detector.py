class DetectorState:
    def __init__(self, thresholds=None):
        if not thresholds:
            thresholds = [
                (3, 'MEDIUM'),
                (7, 'HIGH'),
            ]
        self.thresholds = thresholds
        self.carsCount = 0
        self.img_path = None
    
    def update(self, count, img_path):
        self.carsCount = count
        self.img_path = img_path
    
    def get_state(self):
        return {
            'count': self.carsCount,
            'congestion': self.get_congestion()
        }
    
    def get_congestion(self):
        c = self.carsCount
        congestion = 'LOW'
        for tv, tname in self.thresholds:
            if c < tv:
                break
            congestion = tname
        
        return congestion

    def read_curr_img(self):
        if not self.img_path:
            return None
        try:
            with open(self.img_path, mode='rb') as f:
                return f.read()
        except Exception as e:
            print('ERROR: ', e)
        
        return None

STATE = DetectorState()