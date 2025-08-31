from enum import Enum
from torch.cuda import is_available as cuda_is_available

label_list = ["Data Processing", "Web/API Code", "Algorithms/Logic", "Machine Learning"]
label2id = {label: i for i, label in enumerate(label_list)}
id2label = {i: label for label, i in label2id.items()}

best_device = "cuda" if cuda_is_available() else "cpu"

class DomainEnum(str, Enum):
    DATA_PROCESSING = "Data Processing"
    WEB_API_CODE = "Web/API Code"
    ALGORITHMS_LOGIC = "Algorithms/Logic"
    MACHINE_LEARNING = "Machine Learning"