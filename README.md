# CarCare AI

## AI-Powered Vehicle Maintenance Assistant

CarCare AI is an AI-powered vehicle maintenance assistant that combines Computer Vision, Retrieval-Augmented Generation (RAG), and a local Large Language Model (LLM).

The system allows users to upload a vehicle image, identify a visible vehicle component, and ask a maintenance-related question. The detected component and user query are used to retrieve relevant information from an automotive maintenance document. A local LLM then generates a response based on the retrieved context.

The system is designed as a document-grounded maintenance assistant. The Computer Vision component identifies visible vehicle parts and does not directly diagnose mechanical failures from images.

---

## Project Overview

The system integrates three main components:

1. **Computer Vision** — YOLO11n-Seg for vehicle-part detection and segmentation.
2. **Retrieval-Augmented Generation** — Hybrid semantic and keyword retrieval over automotive maintenance documentation.
3. **Local LLM** — Llama 3.2 3B running through Ollama for document-grounded response generation.

The complete pipeline is:

```text
Vehicle Image
      |
      v
YOLO11n-Seg
      |
      v
Detected Vehicle Part
      |
      v
Hybrid Retrieval
      |
      v
ChromaDB
      |
      v
Retrieved Context
      |
      v
Llama 3.2 3B
      |
      v
Maintenance Response
      |
      v
Supporting Sources
```

---

## Web Application

The project includes a web interface for interacting with the complete AI pipeline.

### Interface

<p align="center">
  <img src="docs/Screenshot%202026-09-22%20235612.png" width="48%">
  <img src="docs/Screenshot%202026-09-22%20235627.png" width="48%">
</p>

### Vehicle Inspection

<p align="center">
  <img src="docs/Screenshot%202026-09-22%20235638.png" width="48%">
  <img src="docs/Screenshot%202026-09-22%20235653.png" width="48%">
</p>

### AI Response and Supporting Information

<p align="center">
  <img src="docs/Screenshot%202026-09-22%20235704.png" width="48%">
  <img src="docs/Screenshot%202026-09-22%20235719.png" width="48%">
</p>

---

## System Workflow

### 1. Vehicle Part Detection

The uploaded image is processed using a custom-trained YOLO11n-Seg segmentation model.

The model returns:

* Detected vehicle-part class
* Confidence score
* Segmentation information

Example:

```text
Detected Part: wheel
Confidence: 0.88
```

### 2. Query Construction

The detected vehicle part is combined with the user's maintenance question.

Example:

```text
Vehicle part: wheel
Maintenance question: What are the common tyre faults?
```

Automotive terminology related to the detected component is also considered during retrieval.

### 3. Hybrid Retrieval

The system combines semantic similarity and keyword matching.

The final retrieval score is calculated as:

```text
Final Score =
0.75 × Semantic Score
+
0.25 × Keyword Score
```

The top five relevant document chunks are selected as context for the LLM.

### 4. Local LLM Generation

The retrieved context is passed to Llama 3.2 3B through Ollama.

The model is instructed to generate the response using the retrieved maintenance information.

### 5. Response

The application presents:

* Detected vehicle part
* Detection confidence
* Maintenance guidance
* Supporting document pages

---

## Computer Vision

The Computer Vision component uses a custom-trained YOLO11n-Seg model based on the CarParts-Seg dataset.

### Dataset Statistics

| Property          |             Value |
| ----------------- | ----------------: |
| Total Images      |             3,833 |
| Annotated Objects |            20,374 |
| Classes           |                23 |
| Annotation Type   | YOLO Segmentation |

### Vehicle Part Classes

```text
back_bumper
back_door
back_glass
back_left_door
back_left_light
back_light
back_right_door
back_right_light
front_bumper
front_door
front_glass
front_left_door
front_left_light
front_light
front_right_door
front_right_light
hood
left_mirror
object
right_mirror
tailgate
trunk
wheel
```

---

## Model Training

| Parameter               | Value       |
| ----------------------- | ----------- |
| Model                   | YOLO11n-Seg |
| Epochs                  | 20          |
| Image Size              | 640 × 640   |
| Batch Size              | 4           |
| Device                  | NVIDIA GPU  |
| Early Stopping Patience | 5           |

The trained model is stored as:

```text
model_backup/carcare_yolo11n_seg_best.pt
```

---

## Model Evaluation

Evaluation was performed on 276 test images containing 1,599 annotated instances.

| Metric         |        Result |
| -------------- | ------------: |
| Box Precision  |         59.6% |
| Box Recall     |         81.7% |
| Box mAP50      |         69.5% |
| Box mAP50-95   |         57.7% |
| Mask Precision |         61.4% |
| Mask Recall    |         79.5% |
| Mask mAP50     |         69.6% |
| Mask mAP50-95  |         55.5% |
| Inference Time | ~5.4 ms/image |

---

## Retrieval-Augmented Generation

The RAG pipeline uses the automotive maintenance textbook:

**Vehicle Maintenance Vehicle Fitting Units Level 1 and 2**

### Document Statistics

| Property         |   Value |
| ---------------- | ------: |
| Pages            |     145 |
| Non-empty Pages  |     144 |
| Words            |  33,232 |
| Characters       | 213,324 |
| Generated Chunks |     302 |

The document covers:

* Tyres and wheels
* Braking systems
* Suspension
* Steering
* Electrical systems
* Batteries
* Exhaust systems
* Cooling systems
* Clutch systems
* Lubrication
* Vehicle inspection
* Component replacement
* Fault identification
* Workshop safety

---

## Document Processing

The document processing pipeline consists of:

```text
PDF Text Extraction
        |
        v
Text Cleaning
        |
        v
Page Organization
        |
        v
Chunking
        |
        v
Embedding Generation
        |
        v
ChromaDB Storage
```

### Configuration

```text
Chunk Size: 1000 characters
Chunk Overlap: 150 characters
Embedding Model: all-MiniLM-L6-v2
Embedding Dimension: 384
Vector Database: ChromaDB
```

Processed information is stored in JSON files:

```text
Data/
└── processed/
    ├── pdf_pages_cleaned.json
    ├── pdf_chunks.json
    ├── dataset_inspection_summary.json
    └── rag_config.json
```

---

## Evidence Control

The system includes an evidence check before generating an answer for an image-detected component.

If the retrieved maintenance documentation does not provide sufficient information about the detected component, the system returns a controlled response instead of generating unsupported maintenance guidance.

Example:

```text
The available maintenance document does not provide enough
specific information about the rear bumper to answer the
question reliably.
```

This mechanism is intended to reduce unsupported responses when the source documentation does not adequately cover a particular component.

---

## Example

### Input

Vehicle image containing a wheel.

```text
Question:
What are the common tyre faults?
```

### Detection

```text
Detected Part: wheel
Confidence: 88%
```

### Retrieved Information

Relevant maintenance information may include:

* Edge wear
* Flat spots
* Feathering
* Tread cuts
* Under-inflation
* Over-inflation
* Wheel alignment

### Final Response

The local LLM generates maintenance guidance based on the retrieved document context and provides the corresponding supporting document pages.

---

## Technology Stack

| Component               | Technology            |
| ----------------------- | --------------------- |
| Programming Language    | Python                |
| Computer Vision         | YOLO11n-Seg           |
| Dataset                 | CarParts-Seg          |
| Embedding Model         | all-MiniLM-L6-v2      |
| Vector Database         | ChromaDB              |
| LLM Runtime             | Ollama                |
| LLM                     | Llama 3.2 3B          |
| Backend                 | FastAPI               |
| Frontend                | HTML, CSS, JavaScript |
| Deep Learning           | PyTorch               |
| Model Framework         | Ultralytics           |
| GPU Acceleration        | CUDA                  |
| Development Environment | VS Code               |

---

## Backend API

### `GET /`

Serves the web application.

### `POST /ask`

Handles text-based maintenance questions.

Example:

```json
{
  "question": "What should I check when inspecting a tyre?"
}
```

### `POST /ask-with-image`

Handles multimodal requests containing a vehicle image and a maintenance question.

Processing flow:

```text
Image
  |
  v
YOLO Detection
  |
  v
Detected Part
  |
  v
RAG Retrieval
  |
  v
Ollama
  |
  v
Answer + Sources
```

When the backend is running, the interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Project Structure

```text
CarCare_AI/
│
├── Data/
│   ├── processed/
│   │   ├── pdf_pages_cleaned.json
│   │   ├── pdf_chunks.json
│   │   ├── dataset_inspection_summary.json
│   │   └── rag_config.json
│   └── chroma_db/
│
├── docs/
│   ├── Screenshot 2026-09-22 235612.png
│   ├── Screenshot 2026-09-22 235627.png
│   ├── Screenshot 2026-09-22 235638.png
│   ├── Screenshot 2026-09-22 235653.png
│   ├── Screenshot 2026-09-22 235704.png
│   └── Screenshot 2026-09-22 235719.png
│
├── model_backup/
│   └── carcare_yolo11n_seg_best.pt
│
├── notebooks/
│   ├── 01_data_inspection.ipynb
│   ├── 02_rag_pipeline.ipynb
│   ├── 03_cv_yolo.ipynb
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── runs/
│
├── main.py
├── rag.py
├── cv.py
├── README
└── .gitignore
```

Raw datasets and source PDF files are excluded from the repository.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/R-MO927/CarCare_AI.git
cd CarCare_AI
```

### 2. Create a Virtual Environment

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Ollama

Make sure Ollama is installed and running.

Pull the required model:

```bash
ollama pull llama3.2:3b
```

### 5. Start the Backend

```bash
python -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

---

## Project Scope

The current system focuses on:

```text
Vehicle Part Identification
        +
Maintenance Information Retrieval
        +
Document-Grounded Answer Generation
```

The Computer Vision model identifies visible vehicle components. It does not directly diagnose mechanical failures from an image.

For example:

```text
Image
  |
  v
Wheel detected
```

rather than:

```text
Image
  |
  v
Wheel bearing failure diagnosed
```

Maintenance guidance is generated from information retrieved from the automotive maintenance documentation.

---

## Future Improvements

Potential future extensions include:

* Additional automotive maintenance documents
* More recent technical documentation
* Improved retrieval evaluation
* Additional vehicle-part classes
* Improved segmentation performance
* Dashboard warning-light recognition
* Multi-document RAG
* Maintenance history integration
* Voice interaction
* Cloud deployment
* Mobile interface
* More advanced diagnostic capabilities

---

## Author

**Rahma Mohamed**

Computer Science Student
Helwan University, Egypt

Interests: Artificial Intelligence, Machine Learning, Computer Vision, Generative AI, RAG Systems, Data Science, and AI Engineering.
