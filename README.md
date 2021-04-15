# Setup

```sh
pip install virtualenv
virtualenv <your-env>
source <your-env>/bin/activate
<your-env>/bin/pip install -r requirements.txt
```

# Required Environment Variables

`GOOGLE_APPLICATION_CREDENTIALS`: set to fully qualified path to Google API JSON credentials file
`GOOGLE_PARENT_PROJECT`: set to your Google project that has Google Translate API enabled


# How To Use

`python main.py translate {filename} {languages}` where:

`{filename}` is a fully qualified path to json or properties file to be translated  
`{languages}` is a space separate list of language codes  


# How It Works

* Parses either the JSON or Properties file given and translates each value into each of the language codes passed
* The resulting translations are written to a file of the same type i.e. json or properties, with the name equivalent to name of the original file followed by a hyphen and the language code for the translation

## Example:

**Input:**  
`python main.py translate messages.properties es ar` 

**Output:**  
messages.properties (original file)  
messages-es.properties (Spanish version)  
messages-ar.properties (Arabic version)  
