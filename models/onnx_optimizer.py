import time
import os
import numpy as np
from ultralytics import YOLO

# --- CONFIGURATION ---
# Default to the Stage 2 model weights in the repository structure
DEFAULT_MODEL = os.path.join("models", "weights", "domain_rand_best.pt")
MODEL_PATH = DEFAULT_MODEL if os.path.exists(DEFAULT_MODEL) else "best.pt"

def main():
    print("--- INITIATING EDGE SPEED BENCHMARK ---")
    
    # 1. Load the PyTorch model
    print(f"Loading base model: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)
    
    # 2. Export to ONNX at 224x224 resolution
    print("\n[INFO] Exporting to ONNX format at 224x224 (Edge Spec)...")
    onnx_path = model.export(format='onnx', imgsz=224, dynamic=False)
    print(f"[SUCCESS] ONNX Model saved to: {onnx_path}")
    
    # 3. Load the new lightweight ONNX model
    print("\n[INFO] Loading ONNX model into memory...")
    onnx_model = YOLO(onnx_path)
    
    # 4. Pure Speed Benchmark
    print("\n[BENCHMARK] Running speed benchmark on 50 frames...")
    dummy_img = np.zeros((224, 224, 3), dtype=np.uint8)
    
    # Warmup
    for _ in range(5):
        onnx_model.predict(dummy_img, imgsz=224, verbose=False)
        
    # Benchmark
    start_time = time.perf_counter()
    test_frames = 50
    for _ in range(test_frames):
        onnx_model.predict(dummy_img, imgsz=224, verbose=False)
    end_time = time.perf_counter()
    
    # Calculate averages
    avg_ms = ((end_time - start_time) / test_frames) * 1000
    fps = 1000 / avg_ms if avg_ms > 0 else 0
    
    # 5. Print Results
    print("\n" + "="*50)
    print("EDGE OPTIMIZATION RESULTS (ONNX @ 224x224)")
    print("="*50)
    print(f"Inference Speed: {avg_ms:.2f} ms per image")
    print(f"Maximum FPS:     {fps:.1f} FPS")
    print("="*50)

if __name__ == '__main__':
    main()