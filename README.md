# MAT students' ORCID publications

This project collects the MAT students' publications from [ORCID](https://orcid.org/) and creates a `.bib` file per student in the `public` directory. The filename for this is the same as the filename of the student's profile on [the MAT website](https://mat.qmul.ac.uk/). The project is built regularly and published to [qmul-mat.github.io/orcid-publications/](qmul-mat.github.io/orcid-publications/). To have your publications collected, add your ORCID ID to your profile on the MAT website. More info about how to do so can be found [here](https://github.com/QMUL-MAT/gatsby-mat/#information-for-students-and-staff).

## How to run

Prepare

```shell
python -m venv env  # using virtual environments is highly recommended
source env/bin/activate
pip install -r requirements.txt  # or better, use pip-tools
```

Run

```shell
python main.py
```

## Deployment

This project is built and deployed regularly to GitHub pages with GitHub actions.