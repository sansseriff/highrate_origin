
This repository is used with datasets available in a [figshare project](https://figshare.com/projects/highrate_datasets_1/176379)

Either use the setup process below or manually download the figshare dataset that corresponds to the folders/submodules in this repo.


to install:
1. clone repository

    ```bash
    git init
    git pull https://github.com/sansseriff/highrate_origin.git
    git submodule update --init --recursive
    ```


2. Set up conda environment:

    ```bash
    conda env create -f environment.yaml
    conda activate highrate
    ```

3. Download the data files for particular folders/submodules:

    ```
    python figshare_download.py
    ```

    Then follow the onscreen prompts. 


To delete the conda environment if you no longer need it:
```
conda remove --name highrate
```
