import torch
from ultralytics import YOLO

def pick_device():
    if torch.cuda.is_available():
        return 0            # first CUDA GPU
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"        # Apple Silicon
    return "cpu"

def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))  # the script’s directory
    training_set = os.path.join(repo_root, "Loading_Unloading_Training_Files/data.yaml")
    output_dir = os.path.join(repo_root, "outputs")

    os.makedirs(output_dir, exist_ok=True)
    device = pick_device()

    model = YOLO("yolo11s.pt")   # try s/m instead of n for better capacity
    results = model.train(
        data=training_set,
        epochs=50,              # 10 is far too low; start 100–200
        imgsz=960,               # 640 is fine; bump to 960–1280 for tiny objects
        batch=8,                 # raise if GPU memory allows; reduce if OOM
        workers=4,               # 2–4 is good; tune
        device=device,
        patience=30,             # early-stop patience
        cos_lr=True,             # smoother LR schedule
        pretrained=True,         # use pretrained backbone
        seed=0
    )

if __name__ == "__main__":
    main()


