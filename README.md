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
cd cis-scripts
conda activate matrix-server
python matrix_server.py <path-to-dataset>
```

Start matrix compute server
```
cd cis-scripts
conda activate matrix-server
python matrix_compute_server.py <path-to-dataset>
```
