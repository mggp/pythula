from torch.cuda import is_available as cuda_is_available

label_list = ["Data Processing", "Web/API Code", "Algorithms/Logic", "Machine Learning"]
label2id = {label: i for i, label in enumerate(label_list)}
id2label = {i: label for label, i in label2id.items()}

best_device = "cuda" if cuda_is_available() else "cpu"