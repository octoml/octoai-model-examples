# OctoShop Streamlit

This simple streamlit based frontend is buid with streamlit: https://streamlit.io/

It will call into OctoAI endpoints in order to perform image processing of an image using GenAI models.

You can read more about the pipeline and how it works here: https://colab.research.google.com/drive/1VRQ_GbDXTbSFe0TGA-FT-xpA0a7kMpWl?usp=sharing

## Setup

You'll need to install the following pre-requisites. We recommend using Python virtual env to manage your python dependencies easily.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the pip requirements in your local python virtual environment

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Run the app locally

To run your streamlit webapp locally you'll need to add the following variables to your environment:

```bash
export OCTOAI_API_TOKEN=<your key here>
export CLIP_ENDPOINT_URL=<your clip endpoint url here>
```

If you're not sure where to get those from, it will be explained in great detail over in the notebook guide: https://colab.research.google.com/drive/1VRQ_GbDXTbSFe0TGA-FT-xpA0a7kMpWl#scrollTo=Tcmf0XR56Gtj

Now that you've set these environment variables, go ahead and run the app with:
```bash
streamlit run octoshop.py
```

Feel free to tweak your OctoShop model cocktail by changing the following lines as you see fit:
```python
transformation = "set the image description into space"
style = "3d-model"
```

## Publish your app on streamlit

First fork this repo in your own GitHub, that will allow you to host your modified octoshop web app.

Go to streamlit webpage and sign/log in: https://streamlit.io/

Once logged in you can launch a new app by clicking on "New app".

Under Deploy an app page:
* You can specify the repository you want to pull from on your personal github
* You can specify the branch to use in your repo
* And the path to your octoshop.py path
* You can also feel free to customize the url to something fun and unique
* Make sure to hit `Advanced settings`, and fill in the following under secrets, or else the app won't work properly. Hit Save.

```toml
OCTOAI_API_TOKEN=<your key here>
CLIP_ENDPOINT_URL=<your clip endpoint url here>
```

And now that all settings have been set, hit "Deploy!" and enjoy your model cocktail!

