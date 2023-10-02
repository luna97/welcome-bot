import face_recognition
import pickle
import sys
import os

if len(sys.argv) == 2 and (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
    print("Create features from faces in folder 'people'. The features are saved in the folder")
    print("--delete -d     Delete all the previous features and creates everything from scratch")
    sys.exit()

if len(sys.argv) == 2 and (sys.argv[1] == "--delete" or sys.argv[1] == "-d"):
    print("Removing all features...")
    for f in os.listdir("features"):
        os.remove("features/" + f)
        

print("Creating features for people")

for p in os.listdir("people"):
    feature_file_path = 'features/' + p + '.dat'
    if os.path.exists(feature_file_path):
        print(p + " already trained, skipping")
        continue
    
    dir_path = "people/" + p + "/"
    path = dir_path + "img.jpg"

    #verify that it is not a tmp file
    if not os.path.isdir(dir_path): 
        continue
        
    # try to get the correct path
    if not os.path.exists(path):
        path = "people/" + p + "/" + "img.jpeg"
    if not os.path.exists(path):
        continue
        
    print("Loading " + p + " data")
        
    # getting features
    face = face_recognition.load_image_file(path)
    face_bounding_boxes = face_recognition.face_locations(face)
    
    # if only one person found
    if len(face_bounding_boxes) == 1:
        face_enc = face_recognition.face_encodings(face, model="large")[0]
        with open(feature_file_path, 'wb') as f:
            pickle.dump(face_enc, f)
        print("Features for " + p + " correctly trained")
    else:
        print(p + "/" + person_img + " cant be used for training")
        

        