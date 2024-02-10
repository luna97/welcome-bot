# welcome-bot
This is a security camera / welcome bot that performs face recognition in real time in raspberry

## Project structure

Here is listed the project structure:
- `capture` folder: contains all the images with detected faces that are sent to the telegram bot
- `features` folder: contains all the face embeddings of my dataset in `.dat` format
- `people` folder: it is my original dataset with photos of people i want to recognize
- `saluti` folder: it contains the mp3 files to welcome people
- `test_notebook.ipynb`: it is the file where i tested different strategies before to create a main program
- `create_feature.py`: that file creates the face embeddings from the labeled photos inside the `people` folder and then saves the embeddings in the `features` folder
- `facerec.py`: is the main program that will run on the raspberry
- `utility.py`: contains some useful methods that i will need in my main program
- `voiceGen.py`: with that i can create customized welcome messages with text-to-speech


## Setup

### Dependencies
Install the following libraries with python:
```
pip3 install -r requirements.txt
```
It is reccomended to run it in a virtual environment.

### Add persons to the dataset
First thing to do is to add persons to the dataset (here there will be just my face).
1. Add a folder with the name of the person inside the folder `people`
2. In that folder add an image of that person in high quality named `img.jpg` that will be used to extract the feature
3. Run `python3 create_feature.py`, it will create the features for the person
4. Create a custom mp3 file for welcome the person with the command `python3 voiceGen.py Welcome message`
5. It will create a file `output.mp3`, move it in the `saluti` folder and rename it with the name of the person: `mv output.mp3 saluti/name.mp3`

### Run the system
The only thing to do is to run the file `facerec.py` and the system will be running.
You can even create a system service so the code is automatically started when the machine reboots.


## Testing and debug

In order to run the tests, even from a laptop just follow the step inside the file `test_notebook.ipynb`.
It is strongly recomendedd to use a virtual environment because in the file will be downloaded all the dependencies.
