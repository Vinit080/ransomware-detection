$env:OLLAMA_MODELS = "E:\ollama_models"
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull qwen2:0.5b
.\venv\Scripts\Activate.ps1
pip install ollama
$env:OLLAMA_MODEL = "qwen2:0.5b"
python scripts\evaluation_benchmark.py --dataset benchmark_dataset.json
