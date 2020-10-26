#!/usr/bin/env python
# coding: utf-8

# In[1]:


# begin importing of standard modules
import re
import random
import os
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import pprint as pp
import sys
# end importing of standard modules

# begin setting of home path variable and adding data directory to path import list
if 'Step_1.ipynb' or 'Step_1.py' or 'Step_1.exe' in os.listdir():
    home = os.getcwd()     
sys.path.append(os.path.join(home, 'data')) #This will add the data folder to the path variable so modules can be imported 
# end setting of home path variable and adding data directory to path import list

# begin creation Regular Expressions
validHash = re.compile(r'#\d{0,3}')
pinRegex1 = re.compile(r'GPIO_InitStruct.Pin\s*=\s*')
pinRegex2 = re.compile(r'(\w+)')
modeRegex = re.compile(r'''
            GPIO_MODE_                  #This will match the first part
            (
            INPUT|
            OUTPUT_PP|
            OUTPUT_OD|
            AF_PP|
            AF_OD|
            ANALOG|
            IT_RISING|
            IT_FALLING|
            IT_RISING_FALLING|
            EVT_RISING|
            EVT_FALLING|
            EVT_RISING_FALLING)    
            ''', re.VERBOSE)
pullRegex = re.compile(r'''
            GPIO_NOPULL|
            GPIO_PULLUP|
            GPIO_PULLDOWN
            ''', re.VERBOSE)
speedRegex = re.compile(r'''
             GPIO_SPEED_FREQ_LOW|
             GPIO_SPEED_FREQ_MEDIUM|
             GPIO_SPEED_FREQ_HIGH|
             GPIO_SPEED_FREQ_VERY_HIGH
             ''', re.VERBOSE)
gpioInitRegex = re.compile(r'''
                 HAL_GPIO_Init\((\w+),
                 ''', re.VERBOSE)
# end creation Regular Expressions

# begin import of created modules
try:   
    import ds
    import mypath
except ModuleNotFoundError:
   pass
# begin import of created modules

# begin importing and creation of a data frame
os.chdir(mypath.data)
df = pd.read_csv('data.csv')
# end importing and creation of a data frame

# begin adding a path to main.c column to dataframe
df['main.c Path'] = 'No main.c file. Double check student repository for correct upload!'
# end adding a path to main.c column to dataframe

# begin function that identifies the pinout in main.c
def goIntoMain(pathToC, i):
    try:
        cfile = open(pathToC)
    except FileNotFoundError:
        df.loc[df['hsh'] == i, 'main.c Path'] = 'No main.c file. Double check student repository for correct upload!'
        pass
# end function that identifies the pinout in main.c

# begin looping through each student repo to find the main.c file and pass it to the function that goes into main and gets the pinouts
os.chdir(mypath.repos)
for i in os.listdir():
#     import ipdb; ipdb.set_trace()
    pathToCore = df.loc[df['hsh'] == i, 'CorePath'].values[0]
    if os.path.isdir(pathToCore):
        pathToCFile = os.path.join(pathToCore, 'Src', 'main.c')
        df.loc[df['hsh'] == i, 'main.c Path'] = pathToCFile
        goIntoMain(pathToCFile , i)
    else:
        pass
os.chdir(mypath.repos)
# end looping through each student repo to find the main.c file and pass it to the function that goes into main and gets the pinouts

#begin function that creates csv based on pinouts
def makePins(testGoMain, j):   
    
    dfPins = pd.DataFrame(columns = ['Port', 'Pin', 'Mode','Pull-Type','Speed']) 
    
    try:
        cFileT = open(testGoMain) 
        lines = cFileT.readlines() 
    except FileNotFoundError:
        dfPins.to_csv(j + '_main.c.csv', index = False)
        lines = 'Empty repo'
        dfPins.loc[1] = lines

   
    pinList = []
    validList = []
    modeList = []
    pullList = []
    speedList = []
    x = 0

    for i in lines:
        isValid = pinRegex1.findall(i)
        isPinLine = pinRegex2.findall(i)
        isModeLine = modeRegex.findall(i)
        isPullLine = pullRegex.findall(i)
        isSpeedLine = speedRegex.findall(i)
        isGpioInitLine = gpioInitRegex.findall(i)
        if isPinLine and isValid:
            pinList.extend(isPinLine[2:])
            validList.extend(isValid)      
        elif isModeLine:
            modeList.extend(isModeLine)
        elif isPullLine:
            pullList.extend(isPullLine)
        elif isSpeedLine:
            speedList.extend(isSpeedLine)
        elif isGpioInitLine and pinList and validList:
            dfTempPin = pd.DataFrame(columns = ['Port', 'Pin', 'Mode','Pull-Type','Speed']) 
            for i in pinList:
                dfPins.loc[x] = [isGpioInitLine[0]] +  [i] + [modeList] + [pullList] + [speedList]
                x += 1           
            pinList = []
            modeList = []
            pullList = []
            speedList = []
            validList = []
        else:
            pass
    
    os.chdir(mypath.data)
    dfPins.to_csv(j + 'Pinout_main.c.csv', index = False)
#end function that creates csv based on pinouts

#begin create csv files of student pinouts
os.chdir(mypath.repos)
for i in os.listdir():  
#     import ipdb; ipdb.set_trace()
    testGoMain = df.loc[df['hsh'] == i, 'main.c Path'].values[0]
    makePins(testGoMain, i)
#end create csv files of student pinouts

#begin last bit of sanitation that should actually be part of step 1
os.chdir(mypath.repos)
# for i in os.listdir():
#         newPath = os.path.join(filepath , i)
#         if i in ['.git','.settings','Driver','Debug','.metadata']:
#             pass
#         elif i == 'Core':
#             df.loc[df['hsh'] == validHash.findall(newPath)[0], ['CorePath']] = newPath
#         elif os.path.isdir(newPath) == False:
#             pass
#         elif os.path.isdir(newPath) and i != 'Core':                   
#             findDrivers2(newPath)

list1 = []
def searchIoc(lines, j):
    x = 0
    dfIoc = pd.DataFrame(columns = ['Pin', 'Label']) 
    for i in lines:
        list1 = pinRegRename.findall(i)
        if list1:
            tup1 = list1[0]
            dfIoc.loc[x] = [tup1[0]] + [tup1[2]]
            os.chdir(mypath.data)               
        x += 1
    dfIoc.to_csv(j + '_ioc.csv', index = False)
    
    


#This is it man
stdNumRegex = re.compile(r'_(\d{8}$)')
replaceList = re.compile(r"(\[')(\d{8})('\])")
iocRep = re.compile(r"\w*\.ioc")
pinRegRename = re.compile(r"(\w+)\.(GPIO_Label)=(\w+\s*\w+)")

for i in os.listdir():
    os.chdir(mypath.repos)
    pathToCore = df.loc[df['hsh'] == i, 'CorePath'].values[0]
    try:
        os.chdir(os.path.join(pathToCore))
        os.chdir(os.path.join(pathToCore, '..'))
        newList = list(filter(iocRep.findall, os.listdir()))
        if newList:
            lines2 = open(newList[0]).readlines() 
            os.chdir(mypath.data)
            searchIoc(lines2, i)
        else:
            pass
    except FileNotFoundError:
        pass
    
    
    

        
    


# In[2]:


# # iocRep.findall(os.listdir())
# newList = list(filter(iocRep.findall, os.listdir()))
# newList[0]
# lines2 = open(newList[0]).readlines() 
# lines2

