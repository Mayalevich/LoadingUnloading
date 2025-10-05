import torch
from ultralytics import YOLO

def pick_device():
    if torch.cuda.is_available():
        return 0            # first CUDA GPU
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"        # Apple Silicon
    return "cpu"

def main():
    training_set = r"/Users/jingyu/Documents/NIC_CV/F25-NuclearIC/Loading_Unloading_Subproblem/Loading_Unloading_Training_Files/data.yaml"
    device = pick_device()

    model = YOLO("yolo11n.pt")
    results = model.train(
        data=training_set,
        epochs=10,              
        imgsz=640,               
        batch=8,                
        workers=4,               
        device=device,
        patience=30,             
        cos_lr=True,             
        pretrained=True,         
        seed=0
    )

if __name__ == "__main__":
    main()
