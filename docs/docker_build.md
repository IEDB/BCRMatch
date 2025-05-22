## Docker Build
To build an image from `Dockerfile`:

```bash
docker build -t bcrmatch .
```

Now you can run commands using the ``bcrmatch`` container image as described below.

> **_NOTE_**:<br>
> On ARM-based systems (e.g., Mac M1/M2/M3), you may also need to pass the ``--platform=linux/amd64`` command line
> switch to every Docker command.<br><br>Although it seems to build properly on some ARM machines, the tensorflow libraries may
> cause issues and the image may be unusable.

Accessing inside the container to run the program:

```bash
docker run -it bcrmatch /bin/bash
```

It is also possible to run a command without stepping inside the container. The following command will allow you to run the command and automatically clean up the container afterward.

```bash
docker run --rm bcrmatch python3 run_bcrmatch.py -i examples/set-a/example.tsv -tn abpairs_abligity
```

### Mounting Volumes

Use the following commands to mount current directory to the container `/src/bcrmatch` folder.

```
docker run -it -v $(pwd):/src/bcrmatch bcrmatch /bin/bash 
```

> **_NOTE_**<br>
> Mounting to the directory of BCRMatch will override container's volume, thus `models` folder will be missing in the container. Please re-run the download script to retrieve all models.
>
> ```bash
> sh download-latest-models.sh
> ```
>
> This will create `models` folder that contains all the pickled models and `dataset-db` file.
>This will download a `models` folder with the following file structure:
>```
>.
>└── models/
>    ├── README-models
>    ├── dataset-db
>    └── models/
>        ├── README
>        ├── abpairs_abligity/
>        └── score_distributions/
>```
>
> Later, when setting the models directory using `--models-dir` flag, please use the absolute path of the first `models` directory that is at the top of the file structure.

## Retrieving result files from the container

Let say inside the BCRMatch container, the following command was run.

```bash
python run_bcrmatch.py -i ./examples/example.tsv -tn abpairs_abligity -o bcroutput.csv
```

The `bcroutput.csv` file will be saved in the default current directory (`/src/bcrmatch`).

When exiting out of the container, the container will be stopped. Let say that the container ID is `3145157374cb`.

One way to retrieve the output file from the container is through using `docker cp`:

```docker
docker cp <CONTAINER ID>:<PATH-TO-OUTPUT-FILE> <LOCAL-DIRECTORY>

# Using the above example...
docker cp 3145157374cb:/src/bcrmatch/bcroutput.csv .
```
