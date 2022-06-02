# abautomator
A/B testing at the press of a button

## Table of Contents
1. [How to Use](#how-to-use)
2. [Setup](#setup)
3. [Add a Metric](#add-a-metric)
4. [Data Architecture](#data-architecture)

## How-to-use

- Fork this repo. Name it `abautomator-<experiment label>`.
- Update `abautomator/exp_config.py` with your experiment values
- Standup the abautomator container
    - In it run `pytest tests/metrics/test_get_exp_objs.py::test_get_objects --runbuild`. Depending on experiment size this may take +10 minutes.
    - `exit` this Docker container
- Standup the Flask app Docker container
    - Navigate to `http://localhost:8000/primary/`. Voila! Your experiment results.
- **(Warning)** Having the two Docker containers open at the same time will hog a majority of your system's memory
- **(Optional)** If you want to debug/more control over workflow there is a `notebooks/exp_playground.ipynb` file available through the jupyter Docker container. This can also be used to save your experiment charts for upload to Google Drive

## Setup

### Local Backend Development 

```bash
# Should only need to run these gcloud commands once
gcloud auth login
gcloud auth application-default login

docker build -f Dockerfile.abautomator -t abauto .
docker run -ti --rm                             \
    -v ${PWD}:/abautomator                       \
    -v=$HOME/.config/gcloud:/root/.config/gcloud  \
    abauto
```

To run the test suite from scratch:

```bash
rm tests/cache/*.p && clear && pytest -v tests/
```

### Local web development

```bash
docker build -f Dockerfile.app -t app .
docker run -p 8000:5000                 \
    -v ${PWD}:/abautomator                       \
    -v=$HOME/.config/gcloud:/root/.config/gcloud  \
    -e FLASK_ENV=development                       \
    app
```

### Jupyter

Useful for working on visualization stuff

```bash
docker build -f Dockerfile.jupyter -t jupyter .
docker run -p 8888:8888                    \
    -v ${PWD}:/home/jovyan/work            \
    jupyter
```

To pickle the analysis object used to build the jupyter viz:

```bash
clear && pytest tests/test_get_analy.py --runbuild
```

## Add a metric

1. Using any of the exiting metrics as a template, create your python file in the appropriate subfolder of `metrics/` 
2. Add the metric object to `metric_lookup.METRIC_LOOKUP` with an appropriate key. IMPORTANT - Metric obj must return query with columns [`echelon_user_id`, `n_<metric_key>`, `pct_<metric_key>`]
3. For testing, add the raw sql to `tests/metrics/raw_queries.py` using the same key as from 2 above
4. That's it! Run test for your metric using `pytest tests/metrics/test_metrics.py --name <metric key from 2>`

## Data Architecture

![Images showing abautomator data architecture](images/data_arch.drawio.png)
[Edit](https://app.diagrams.net/#Hruben-cit%2Fabautomator%2Fmain%2Fimages%2Fdata_arch.drawio.png)
