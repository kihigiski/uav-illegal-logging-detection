# A Proactive UAV-Based Intelligent System for Rapid Visual Confirmation of Illegal Logging Activities

[![Degree: MSc Computing & Information Systems](https://img.shields.io/badge/Degree-MSc%20Computing%20%26%20Information%20Systems-blue.svg)](https://strathmore.edu/)
[![Institution: Strathmore University](https://img.shields.io/badge/Institution-Strathmore%20University-orange.svg)](https://strathmore.edu/)
[![YOLOv8s](https://img.shields.io/badge/Model-YOLOv8s%20%2B%20BoT--SORT-green.svg)](https://github.com/ultralytics/ultralytics)
[![Simulation: Unreal Engine + AirSim](https://img.shields.io/badge/Simulation-Unreal%20Engine%20%7C%20AirSim-black.svg)](https://github.com/microsoft/AirSim)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)

> **Master's Dissertation Project**  
> **Author:** Simon Kihigi Mburu (Admission No: 196293)  
> **Supervisor:** Dr. Henry Muchiri  
> **Institution:** School of Computing and Engineering Sciences, Strathmore University, Nairobi, Kenya (August 2026)  
> **Official Citation:** See [BibTeX](#citation) below.

---

An end-to-end aerial surveillance system designed for rapid visual confirmation of illegal logging operations in open-to-moderately canopied forest environments (15% to 65% canopy cover). Developed and evaluated at Strathmore University.

## Core Features
- **Physics-Realistic Simulation:** Procedural canopy density calibrated to 62.71% using Monte Carlo ray tracing within Unreal Engine's Leaf Tree Biome.
- **Automated Synthetic Annotation:** Ground-truth semantic segmentation bounding box extraction using Microsoft AirSim APIs.
- **Domain Randomization Engine:** Parametric weather cycles (sun, cloud, heavy fog), variable camera angles (eye-level to 90° nadir), and HSV-based color randomization.
- **Edge-Optimized Neural Stack:** YOLOv8s + BoT-SORT multi-object tracking exported to ONNX (FP16 half-precision, 224x224 tensor resolution).
- **Temporal False-Positive Mitigation:** 5-frame temporal persistence logic (`AlertFilter`) preventing transient false-positive alarms.
- **Full Edge Application:** Flask dashboard featuring real-time telemetry overlays, thread-safe asynchronous SQLite logging, and instant PDF incident reporting for field rangers.

## Model Benchmarks (Real-World Test Set, n=659)
| Class | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
| :--- | :---: | :---: | :---: | :---: |
| **Logger** | 99.17% | 98.31% | 99.32% | 81.14% |
| **Axe** | 96.93% | 93.39% | 97.83% | 76.22% |
| **Chainsaw** | 94.77% | 87.34% | 93.27% | 67.22% |
| **All Classes** | **96.92%** | **93.01%** | **96.80%** | **74.86%** |

## Datasets & Model Weights

Raw video corpora, training splits, and model weights are hosted externally in persistent cloud storage:

- **Stage 1 Baseline Data & Weights:** [Google Drive - Stage 1](https://drive.google.com/drive/folders/1bDmBbZluQgv06z1Aljc0pW51-aMe2glj?usp=sharing)
  - Curated real-world images (n = 2,623) + annotations and `baseline_best.pt`.
- **Stage 2 Domain-Randomized Data & Weights:** [Google Drive - Stage 2](https://drive.google.com/drive/folders/145cvXRAeeo6DBCxepCTzyScJALPermWL?usp=sharing)
  - Combined synthetic + real-world corpus (n = 6,592) and `domain_rand_best.pt`.
- **Data Provenance & Source Registries:** [Google Drive - Provenance Logs](https://drive.google.com/drive/folders/1x67slG9JaJurySs6riVi4IRruOCqVZju?usp=sharing)
  - Detailed CSV manifests recording source URLs, timestamps, query strings, and license tags.
- **Downloaded Raw Forestry Videos:** [Google Drive - Video Archives](https://drive.google.com/drive/folders/104hUfY_z2yWcK0b0xC7MED7P2lxXU4yt?usp=sharing)
  - Full-resolution raw video sequences used for interval frame extraction.

## Quickstart

### 1. Environment Setup
```bash
git clone [https://github.com/kihigiski/uav-illegal-logging-detection.git](https://github.com/kihigiski/uav-illegal-logging-detection.git)
cd uav-illegal-logging-detection
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Launch Edge Mission Control
```bash
python deployment/app.py
```
Access the operator control dashboard at `http://localhost:5000`.

## Citation
```bibtex
@mastersthesis{mburu2026proactive,
  author       = {Simon Kihigi Mburu},
  title        = {A Proactive UAV-Based Intelligent System for Rapid Visual Confirmation of Illegal Logging Activities for Open and Moderately Canopied Forests Using Computer Vision},
  school       = {Strathmore University, School of Computing and Engineering Sciences},
  year         = {2026},
  month        = {August},
  address      = {Nairobi, Kenya}
}
```