#!/usr/bin/python3
import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import pathlib

#ffmpeg -i input.mp4 -f apng output.png
#ffmpeg -i input_file.mp4 -f apng -plays 0 -vf "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output_file.png

def main():
    settings = getSettingsFromUser() #store settings in a dictionary
    settings = processSettings(settings) # claculate further settings based on user input e.g. speedup factor
    cmd = createFFmpegCommand(settings) #create the shell / terminal / cmd string
    proc = callFFmpeg(cmd) # run the command and store the process in a list
    printFinish(proc) # if all processes have finished > print "finished"

def getSettingsFromUser():
    helloUser()
    settings = {}
    settings["mode"] = askForMode() 
    settings["files"] = getVideoFiles()
    settings["length"] = askForLength()
    settings["fps"] = askForFps()
    settings["resize"] = askForResize()
    
    if settings["mode"] != "pngs":
        settings["loop"] = askForLoop()
    
    settings["fBlend"] = askForBlur()
    
    if settings["mode"] == "webp":
        settings["lossless"] = askForLossless()
        settings["quality"] = askForQuality()
        settings["encoderSpeed"] = askForEncoder()
        settings["preset"] = askForPreset()
    
    elif settings["mode"] == "gif":
        settings["gifColor"] = askForGifMode()

 
    return settings 

def processSettings(settings):
    
    settings["output"] = genOutPaths(settings["files"], settings["mode"])
    settings["speedUp"] = genSpeedUp(settings["length"],settings["fps"], settings["files"]  )
    settings["scale"] = genScaleF(settings["resize"],settings["files"])
    settings["codecFlags"] = genCodecFlags(settings)
    settings["filter"] = genVFilter(settings)
    return settings

def createFFmpegCommand(settings):
    cmds = []      
    
    #if os.name == 'nt':
    #    ffmpeg = str(pathlib.Path(__file__).parent / 'ffmpeg/ffmpeg.exe') + " "
    #else:
    #    ffmpeg = str(pathlib.Path(__file__).parent / 'ffmpeg/ffmpeg') + " "
    ffmpeg = "ffmpeg "

    for c, file in enumerate(settings["files"]):
        inPt = "-i " +'"'+ file +'"' +" "
        outPt = '"'+ settings["output"][c] +'"'
        speed =  settings["speedUp"][c]
        scale = settings["scale"][c]
        vfilter = settings["filter"][c]
        
        fps = settings["fps"]
        codecFlags = settings["codecFlags"]
        ffmpegOutFlags = settings["fps"]+ " -y"+ " "
        
        cmd = ffmpeg + inPt +vfilter +codecFlags +ffmpegOutFlags+ outPt 
        print (cmd)
        cmds.append(cmd)
    return cmds
   
def callFFmpeg(cmds):
    procs = []
    for cmd in cmds:
        process = subprocess.Popen(cmd, universal_newlines=True)
        #for line in process.stdout:
        #   print(line)
        procs.append(process)
    return procs


def printFinish(procs):
    for p in procs:
        p.wait()
    print("-\n- \n- \n- \n- \n- \nall processes finished\n-\n")


def askForGifMode():
    inputStr = input("\nChose the .gif quality: \n0 = low \n1 = medium \n2 = max \nor press RETURN to use the default of medium\n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' or inputStr == 'n' :
        dith = askForDither()
        gifcolor = "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"+dith
        return gifcolor
    elif inputStr.isnumeric() and int(inputStr) == 0:
        return ""
    elif inputStr.isnumeric() and int(inputStr) == 1:
        dith = askForDither()
        gifcolor = "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"+dith
        return gifcolor
    elif inputStr.isnumeric() and int(inputStr) == 2:
        dith = ":dither=none"
        gifcolor = "split[s0][s1];[s0]palettegen=stats_mode=single[p];[s1][p]paletteuse=new=1"+dith
        return gifcolor
    else:
        print("Please enter a number between 0 and 2 or press enter to accept the default\n- ")
        askForGifMode()

def askForDither():
    inputStr = input("\nChose dither method: \n0 = none \n1 = bayer scale 1  \n2 = bayer scale 2 \n3 = bayer scale 3 \n4 = floyd_steinberg \n5 = sierra2_4a   \nor press RETURN to use the default of medium\n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' or inputStr == 'n' :
        dither = "=dither=sierra2_4a:diff_mode=rectangle" 
        return dither
    elif inputStr.isnumeric() and int(inputStr) == 0:
        dither = "=dither=none:diff_mode=rectangle" 
        return dither
    elif inputStr.isnumeric() and int(inputStr) == 1:
        dither = "=dither=bayer:bayer_scale=1:diff_mode=rectangle" 
        return dither
    elif inputStr.isnumeric() and int(inputStr) == 2:
        dither = "=dither=bayer:bayer_scale=2:diff_mode=rectangle" 
        return dither    
    elif inputStr.isnumeric() and int(inputStr) == 3:
        dither = "=dither=bayer:bayer_scale=3:diff_mode=rectangle" 
        return dither
    elif inputStr.isnumeric() and int(inputStr) == 4:
        dither = "=dither=floyd_steinberg:diff_mode=rectangle" 
        return dither
    elif inputStr.isnumeric() and int(inputStr) == 5:
        dither = "=dither=sierra2_4a:diff_mode=rectangle" 
        return dither    
    else:
        print("Please enter a number between 0 and 5 or press enter to accept the default\n- ")
        askForDither()



def genVFilter(settings):
    filters = []
    for c, file in enumerate(settings["files"]):
        if settings["mode"] == "webp":
            filter_comp =[]
            if settings["speedUp"][c]: filter_comp.append(settings["speedUp"][c])
            if settings["scale"][c]: filter_comp.append(settings["scale"][c])
            if settings["fBlend"]: filter_comp.append(settings["fBlend"])
            if len(filter_comp)> 0:
                vf = '-vf "' + ", ".join(filter_comp)+ '" '
            else:
                vf = ""    
            filters.append(vf)
        elif settings["mode"] == "apng":
            filter_comp = []
            if settings["speedUp"][c]: filter_comp.append(settings["speedUp"][c])
            if settings["scale"][c]: filter_comp.append(settings["scale"][c])
            if settings["fBlend"]: filter_comp.append(settings["fBlend"])
            filter_comp.append("split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse")
            if len(filter_comp)> 0:
                vf = '-vf "' + ", ".join(filter_comp)+ '" '
            else:
                vf = ""    
            filters.append(vf)
        elif settings["mode"] == "pngs":
            filter_comp = []
            if settings["speedUp"][c]: filter_comp.append(settings["speedUp"][c])
            if settings["scale"][c]: filter_comp.append(settings["scale"][c])
            if settings["fBlend"]: filter_comp.append(settings["fBlend"])
            if len(filter_comp)> 0:
                vf = '-vf "' + ", ".join(filter_comp)+ '" '
            else:
                vf = ""    
            filters.append(vf)
        elif settings["mode"] == "gif":
            filter_comp = []
            if settings["speedUp"][c]: filter_comp.append(settings["speedUp"][c])
            if settings["scale"][c]: filter_comp.append(settings["scale"][c])
            if settings["fBlend"]: filter_comp.append(settings["fBlend"])
            if settings["gifColor"]: filter_comp.append(settings["gifColor"])
            
    
            if len(filter_comp)> 0:
                vf = '-vf "' + ", ".join(filter_comp)+ '" '
            else:
                vf = ""    
            filters.append(vf)
        else:exit()

    return filters



def genCodecFlags(settings):
    if settings["mode"] == "webp":
        
        loop = "-loop "+settings["loop"]
        flags = " ".join([settings["lossless"],settings["encoderSpeed"],settings["quality"],settings["preset"],loop])+ " "


        return flags
    elif settings["mode"] == "apng":
        fFormat = "-f apng"
        loop = "-plays "+settings["loop"]
        flags = " ".join([loop,fFormat])+ " "
        return flags
    elif settings["mode"] == "pngs":
        return ""
    elif settings["mode"] == "gif":
        
        loop = "-loop "+settings["loop"]
        flags = " ".join([loop])+ " "
        return flags
        
    else:exit()
    


def askForMode():
    inputStr = input("\nChose a output format: \n0 = png frames \n1 = animated png (apng) \n2 = gif \n3 = webp \nor press RETURN to use the default of webp\n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' or inputStr == 'n' :
        return "webp"
    elif inputStr.isnumeric() and int(inputStr) == 0:
        return "pngs"
    elif inputStr.isnumeric() and int(inputStr) == 1:
        return "apng"
    elif inputStr.isnumeric() and int(inputStr) == 2:
        return "gif"
    elif inputStr.isnumeric() and int(inputStr) == 3:
        return "webp"
    else:
        print("Please enter a number between 0 and 3 or press enter to accept the default\n- ")
        askForMode()


def genScaleF(target, files):
    scaleF = []
    for video in files: 
        if type(target) is int:
            tgtStr = str(target)
            scaleStr = 'scale='+tgtStr+':'+tgtStr+':force_original_aspect_ratio=decrease:flags=lanczos'
            scaleF.append(scaleStr)
        elif type(target) is float:
            tgtStr = str(target)
            scaleStr = 'scale=iw*'+tgtStr+':ih*'+tgtStr +":flags=lanczos"
            scaleF.append(scaleStr)
        else:
            scaleF.append("")
    return scaleF
   
def genSpeedUp(target,fps,files):
    speedUp = []
    for video in files: 
        if target:
            vidlength = getVidLength(video)
            speedUpStr = str(target/vidlength)
            ffmmegStr = """setpts="""+speedUpStr+"""*PTS"""
            speedUp.append(ffmmegStr)
        else:
            speedUp.append("")
    return speedUp
   
def getVidLength(filename):
    #if os.name == 'nt':
    #    ffprobe = str(pathlib.Path(__file__).parent / 'ffmpeg/ffprobe.exe') 
    #else:
    #   ffprobe = str(pathlib.Path(__file__).parent / 'ffmpeg/ffprobe') 
    
    ffprobe = "ffprobe"
    result = subprocess.run([ffprobe, "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)


def genOutPaths(files, mode):
    if mode == "pngs":
        extention = r"%d.png"
    elif mode == "apng":
        extention = ".png"
    elif mode == "webp":
        extention = ".webp"
    else:
        extention = ".gif"
    webp = []
    for file in files:
        webp.append(os.path.splitext(file)[0] + extention) 
    return webp 

def askForResize():
    inputStr = input('\nDo you want to resize the image -> input the larger dimension in px or specify a scaling factor < 1.0 eg: "0.5" \nif you want to keep the size press enter\n- ')
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' :
        print("keep duration", end="-", flush=True)
        return False
    elif inputStr.isnumeric():
        return int(inputStr)
    elif isfloat(inputStr):
        return float(inputStr)
    else:
        print("please enter a int, float  or press enter to accept the default\n- ")
        askForResize()

def askForFps():
    inputStr = input("\nplease set the number of Frames_Per_Second(FPS) of the animated .webp file; press return to default to 15\n- ")
   # print(repr(inputStr))
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' :
        return "-r 15"
    elif inputStr.isnumeric():
        
        return "-r " + inputStr
    else:
        print("please enter a number or press enter to accept the default of 15\n- ")
        askForFps()

def askForBlur():
    inputStr = input("\ndo you want to add frame-blending to smooth the animation? \nenter the number of frames to blend or proceed without f.b. by pressing RETURN  \n- ")
   # print(repr(inputStr))
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' :
        return False
    elif inputStr.isnumeric():
        
        return "tmix=frames=" + inputStr
    else:
        print("please enter a number or press enter\n- ")
        askForBlur()
    
def askForLossless():    
    inputStr = input("\nPress y to use lossless compression or press RETURN to use the lossy Compression. \nLossless can increase filesizes.\n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' or inputStr == 'n' :
        
        return "-lossless 0"
    elif inputStr == "y" or inputStr == "Y":
        return "-lossless 1"
    else:
        print("please chose between lossless (y) or lossy Compression (n or RETURN)\n- ")
        askForLossless()

def askForQuality():    
    inputStr = input("\nSpecify the image quality (0 to 100). For lossless encoding, this controls the effort and time spent at compressing more.\nThe default value (press RETURN) is 75 \n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' or inputStr == 'n' :
        return "-quality 75"
    elif inputStr.isnumeric():
        return "-quality "+ str(inputStr)
    else:
        print("Please enter a number between 0 and 100 or press RETURN to accept the default of 75\n- ")
        askForQuality()

def askForLoop():
    inputStr = input("\nHow many times should the image loop? Press RETURN to loop indefinitly\n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' or inputStr == 'n' :
    
        return "0"
    elif inputStr.isnumeric():
        return inputStr
    else:
        print("Please enter a number or press RETURN to accept the default\n- ")
        askForLoop()

def askForEncoder():    
    inputStr = input("\nSpecify the effort of the encoder (0 to 6).Higher values give better quality for a given size at the cost of increased encoding time.\npress RETURN to accept the default of 6\n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' or inputStr == 'n' :
        return "-compression_level 6"
    elif inputStr.isnumeric():
        return "-compression_level"+ str(inputStr)
    else:
        print("Please enter a number between 0 and 6 or press RETURN to accept the default of 6\n- ")
        askForEncoder()

def askForPreset():
    inputStr = input("\nChose a preset: \n0 = none, \n1 = default, \n2 = picture, \n3 = photo, \n4= drawing, \n5 = icon, \n6 =text \nor press RETURN to use the default\n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' or inputStr == 'n' :
        return "-preset default"
    elif inputStr.isnumeric() and int(inputStr) == 0:
        return "-preset none"
    elif inputStr.isnumeric() and int(inputStr) == 1:
        return "-preset default"
    elif inputStr.isnumeric() and int(inputStr) == 2:
        return "-preset picture"
    elif inputStr.isnumeric() and int(inputStr) == 3:
        return "-preset photo"
    elif inputStr.isnumeric() and int(inputStr) == 4:
        return "-preset drawing"
    elif inputStr.isnumeric() and int(inputStr) == 5:
        return "-preset icon"
    elif inputStr.isnumeric() and int(inputStr) == 6:
        return "-preset text"
    else:
        print("Please enter a number between 0 and 6 or press enter to accept the default\n- ")
        askForPreset()

def askForLength():
    inputStr = input("\nDo you want to keep the length of the file (default) or set a new length for the animated webp file\npress return to keep the length or enter a number\n- ")
    if inputStr == '\n' or inputStr == '\r' or inputStr == '' :
        return False
    elif isfloat(inputStr):
        return float(inputStr)
    else:
        print("Please enter a number or press enter to accept the base length\n- ")
        askForLength()
    
def helloUser():
    print("This script uses ffmpeg to convert video to animated images.")
    eingabe = input("\nPress RETURN to proceed\n")

def getVideoFiles():
    eingabe = input("\nSelect a directory with files you want to process (RETURN)")
    videos = []
    folderDir = getFolder()
    print("-listing found video files:")
    for file_ in os.listdir(folderDir):
        if file_.endswith(".mp4") or file_.endswith(".mov") or file_.endswith(".avi"):
            videos.append(os.path.join(folderDir, file_) )
            print(file_)
    return videos

def getFolder():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askdirectory()
    return file_path

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    main()