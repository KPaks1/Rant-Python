import pyaudio, wave, os, getpass
    
class Profile:
    def __init__ (self, firstName, secondName, pWord, ID = False, postCount=0):
        self.firstName = firstName
        self.secondName = secondName
        self.fullName = "{}_{}".format(self.firstName, self.secondName)
        self.pWord = pWord
        # self.birthday = birthDate
        self.folder = False
        if ID:
            self.ID = ID
        else:
            self.ID = self.hashProfile()
        self.postCount = int(postCount)

    def hashProfile(self):
        total = 0
        for i in self.firstName:
            total += ord(i)
        return total

    def changeName (self, newFname, newSname):
        self.firstName = newFname
        self.secondName = newSname
        self.fullName = "{}_{}".format(newFname, newSname)

    def setFolder(self, directory):
        self.folder = directory

    def updatePostCount(self):
        self.postCount+=1
        profileDetails = []
        f = open("./profiles/{}/{}/data/details.txt".format(self.ID, self.fullName),"r")
        for line in f:
            line = line.rstrip().split(": ")
            profileDetails.append(line[1])
        f.close()
        f = open("./profiles/{}/{}/data/details.txt".format(self.ID, self.fullName),"w+")
        f.write("firstName: {}\nsecondName: {}\npWord: {}\nprofileID: {}\npostCount: {}".format(profileDetails[0],profileDetails[1],profileDetails[2],profileDetails[3],str(int(profileDetails[4])+1)))
        f.close()

    def toSaveFile(self):
        return "firstName: {}\nsecondName: {}\npWord: {}\nprofileID: {}\npostCount: {}".format(self.firstName, self.secondName, self.pWord, self.ID, self.postCount)
    
def createFolder(directory, profile):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except:
        print("profile doesn't exist, creating a folder...")
        createFolder(directory, profile)
        profile.folder = directory
def createProfile():
    fName = input("Enter your first name: ")
    lName = input("Enter your last name: ")
    pWord = getpass.getpass('Enter a password:')
    newProfile = Profile(fName, lName, pWord)

    if newProfile.ID in profileDict.keys():
        profileDict[newProfile.ID].append([newProfile.fullName,newProfile])
    else:
        profileDict[newProfile.ID] = [newProfile.fullName,newProfile]
    return newProfile

def getID(fName):
    total = 0
    for i in fName:
        total += ord(i)
    return total

def login():
    fName = input("Enter your first name: ")
    lName = input("Enter your last name: ")
    fullName = "{}_{}".format(fName, lName)
    ID = getID(fName)
    pWord = getpass.getpass('Enter your password:')
    if os.path.exists("./profiles/{}/{}/data/details.txt".format(ID, fullName)):
        fileLines = []
        details = open("./profiles/{}/{}/data/details.txt".format(ID, fullName), "r")
        for line in details:
            line = line.rstrip().split(": ")
            fileLines.append(line)
        details.close()    
        if fileLines[2][0] == "pWord":
            if fileLines[2][1] != pWord:
                i = 4
                while pWord != fileLines[2][1] and i > 0:
                    print("---Incorrect password, you have {} attempts left---".format(str(i)))
                    pWord = getpass.getpass('Password:')
                    i-=1
                if i == 0:
                    print("You have failed to log in, please wait a few minutes and try again...")
                else:
                    print("logging in...")
                    return extractDetails("./profiles/{}/{}/data/details.txt".format(ID, fullName))
            else:
                print("logging in...")
                return extractDetails("./profiles/{}/{}/data/details.txt".format(ID, fullName))
    else:
        choice = input("That account does not exist, type exit to create an account...")
        if choice.lower() != "exit":
            return login()
        else:
            a = createProfile()
            print("Your rant account has been created,")
            print("Please log in to continue...")
            return login()

def saveProfile(profile):
    createFolder("./profiles/{}/{}/data".format(profile.ID, profile.fullName), profile)
    f = open("./profiles/{}/{}/data/details.txt".format(profile.ID, profile.fullName),"w+")
    f.write(profile.toSaveFile())
    f.close()

def extractDetails(directory):
    details = open(directory)
    temp = {}
    for line in details:
        line = line.rstrip().split(": ")
        temp[line[0]] = line[1]
    tempProfile = Profile(temp["firstName"],temp["secondName"],temp["pWord"], temp["profileID"],temp["postCount"])
    return tempProfile

def getProfiles():
    Dict = {}
    if os.path.exists("./profiles"):
        files = os.listdir("./profiles")
        for i in files:
            fullName = os.listdir("./profiles/{}".format(i))
            details = extractDetails("./profiles/{}/{}/data/details.txt".format(str(i),fullName[0]))
            Dict[details.ID] = [details.fullName, details]
    return Dict

def recordRant(profile):
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 7
    WAVE_OUTPUT_FILENAME = "{}-{}{}".format( profile.fullName, profile.postCount, ".wav")
    audio = pyaudio.PyAudio()
    
    # start Recording
    try:
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
        print ("recording...")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
            print ("finished recording")
            
            
            # stop Recording
            stream.stop_stream()
            stream.close()
            audio.terminate()
            if profile.folder == False:
                print("folder doesn't exist, creating directory")
                createFolder("./profiles/{}/{}/rants".format(profile.ID,profile.fullName), profile)
            
            directory = "./profiles/{}/{}/rants/{}".format(profile.ID,profile.fullName, WAVE_OUTPUT_FILENAME)
            print("renaming file... {}".format(directory))
            profile.updatePostCount()
            waveFile = wave.open(directory, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()
    except:
        print("Rant failed, please ensure you have an audio device plugged in and try again")
    

profileDict = getProfiles()
acc = input("Do you have a Rant account? (y/n)")

while acc not in ["y","Y", "n", "N"]:
    acc = input("Do you have a Rant account? (y/n)")

if acc in ["Y","y"]:
    prof = login()


elif acc in ["N","n"]:
    newProfile = createProfile()
    saveProfile(newProfile)
    if newProfile.ID in profileDict.keys():
        profileDict[newProfile.ID].append([newProfile.fullName,newProfile])
    else:
        profileDict[newProfile.ID] = [newProfile.fullName,newProfile]
    prof = profileDict[newProfile.ID][1]

if prof:

    rRant = input("Press p to record...\n")
    while rRant not in ["p", "P",""]:
        rRant = input("Invalid input.\nPlease press p to record...\n")
    if rRant != "":
        Continue = True
    else:
        Continue = False
    while Continue == True:
        recordRant(prof)
        Cont = input("Do you wish to record another rant? (y/n)")
        if Cont not in ["Y","y"]:
            Continue = False
    print("Logging out...")

