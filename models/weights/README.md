# Model Checkpoints & Weights

Ultralytics YOLO exports top-performing checkpoints as `best.pt` by default. 
To run the evaluation and deployment pipelines, download the checkpoints from the Google Drive links below and save them with the corresponding names:

| Model Version | Google Drive Source Folder | Local Destination & Name | Purpose |
| :--- | :--- | :--- | :--- |
| **Stage 1 (Baseline)** | [Stage 1 Drive Folder](https://drive.google.com/drive/folders/1bDmBbZluQgv06z1Aljc0pW51-aMe2glj?usp=sharing) | `models/weights/baseline_best.pt` | Baseline evaluation |
| **Stage 2 (Domain-Randomized)** | [Stage 2 Drive Folder](https://drive.google.com/drive/folders/145cvXRAeeo6DBCxepCTzyScJALPermWL?usp=sharing) | `models/weights/domain_rand_best.pt` | Live AirSim simulation & edge deployment |

### Generating the ONNX Edge Model
The quantized ONNX model is **not** downloaded; it is generated directly from `domain_rand_best.pt` using the export script:

```bash
python models/optimize_onnx.py