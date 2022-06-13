# stratification-matrix
A generic stratification matrix for neural network analysis.

Install matrix-server python environment

```
conda env create --file matrix-server.yml
conda activate matrix-server
pip install flask-cors
```

Start matrix server
```
cd server
conda activate matrix-server
python matrix_server.py ../data
```

Start matrix compute server
```
cd server
conda activate matrix-server
python matrix_compute_server.py <path-to-dataset>
```
