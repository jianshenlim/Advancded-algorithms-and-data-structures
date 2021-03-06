import sys

"""
mirrored boyer moore function, implements logic identical to original boyer moore, but mirroring the scanning directions
@author Jian Lim (29994055)
"""
def mirroredBoyerMoore(textfile,patternfile):

    t = open(textfile,'r+')
    for line in t:
        text = line
    t.close()
    p = open(patternfile,'r+')
    for line in p:
        pattern = line
    p.close()

    mirroredBadCharacterShiftTable = mirroredBadCharShift(pattern)
    mirroredGoodSuffixArray = mirroredGoodSuffix(pattern)
    mirroredMatchedPrefixArray = mirroredMatchedPrefix(pattern)

    startIndex = len(text) - len(pattern) # start index in text for scanning
    endPatternIndex = len(pattern)
    goodSuffixShift = False
    lengthOfsuffix = 0
    positionOfNewSuffix = 0

    outputFile = open("output_mirrored_boyermoore.txt","w")

    while startIndex >= 0:                          # Iterate left to right in text starting from position len(pattern) from right end of text
        startPatternIndex = 0
        while startPatternIndex < endPatternIndex:  # Iterate left to right in pattern
            if goodSuffixShift == True:             # Galil's optimization to prevent repeated scanning of good suffix characters
                if startPatternIndex == [positionOfNewSuffix]:              # if goodsuffixShift was performed, when we reach the index of the suffix, jump to the end index of suffix, skips comparing known chars
                    startPatternIndex = positionOfNewSuffix + lengthOfsuffix
                    continue
            if text[startIndex+startPatternIndex] == pattern[startPatternIndex]:  # if char at pat matches char at text
                startPatternIndex += 1
                if startPatternIndex == len(pattern): # if pat fully matches section in text
                    outputResult = startIndex + 1     # increase by one to get desired position of occurrence
                    outputFile.write(str(outputResult)+"\n")    # write location to output
                    newStartIndex = len(pattern) - mirroredMatchedPrefixArray[-2]  # Case 2, shift by m - matchedPrefix(2) or second position from right in our mirrored matched prefix when pat fully matches
                    startIndex -= newStartIndex
                    endPatternIndex = newStartIndex + 1  # Galil's optimization, reduced range where pattern needs to be compared
                    goodSuffixShift = False              # false because we shifted by matchedprefix
                    break
                    # no need to break, if full match it will be end of inner while loop
                continue
            else:
                nMirroredBadCharacter = max(1, (mirroredBadCharacterShiftTable[startPatternIndex][ord(text[startIndex+startPatternIndex])-97])-1) # find badcharacter shift value for current mismatched char pattern[startPatternIndex] to char text[startIndex+startPatternIndex]
                if mirroredGoodSuffixArray[startPatternIndex] > 0:  # If mirroredgoodSuffix(k-1) > 0 ie (valid good suffix shift)
                    nMirroredGoodSuffix = mirroredGoodSuffixArray[startPatternIndex] - 1
                    lengthOfsuffix = startPatternIndex + 1              # calculate the length and position of the suffix, used to skip over checking the same chars next iteration
                    positionOfNewSuffix = nMirroredGoodSuffix
                    goodSuffixShift = True
                    endPatternIndex = len(pattern)                      # reset end of pattern
                else:                                               # Else assign mirroredMatchedPrefix value
                    nMirroredGoodSuffix = len(pattern) - mirroredMatchedPrefixArray[startPatternIndex] # calculate shift value
                    endPatternIndex = nMirroredGoodSuffix + 1  # Galil's optimization, reduced range where pattern needs to be compared
                    goodSuffixShift = False

                bestShiftValue = max(nMirroredBadCharacter,nMirroredGoodSuffix)

                if bestShiftValue == nMirroredBadCharacter:  # if bad character shift chosen, reset endPatternIndex, so galils optimization not performed
                    endPatternIndex = len(pattern)
                    goodSuffixShift = False
                startIndex -= bestShiftValue
                break # if char does not match stop all further comparisons of pat
            startPatternIndex += 1

    outputFile.close()

def mirroredBadCharShift(pattern):
    # shift table stores the closes 'x' in pat that is to the RIGHT of pos 'k'
    shiftTable = [[-1] * 96 for i in range(len(pattern))] # size |pattern| x alphabet
    for char in range(len(pattern)-2,-1,-1):
        for alphabet in range(96):
            previousLetter = ord(pattern[char+1]) - 32
            shiftTable[char][previousLetter] = char + 1
            if shiftTable[char+1][alphabet] >= 0:
                shiftTable[char][alphabet] = shiftTable[char+1][alphabet]
    return shiftTable

def mirroredGoodSuffix(pattern):
    zSuffixArray = gusfield(pattern) # perform gusfield to get the zSuffixArray of values left to right
    m = len(pattern)
    mirroredGoodSuffixArray = [0]* (m + 1)  # Create goodsuffix array of size 1 bigger than pattern, index of 1 for 1st char in string
    for p in range(m-1,0,-1):
        j = zSuffixArray[p]
        mirroredGoodSuffixArray[j] = p + 1
    return mirroredGoodSuffixArray

def mirroredMatchedPrefix(pattern):
    zArray = gusfield(pattern[::-1])
    mirroredMatchedPrefixArray = [0] * (len(pattern) + 1) # Create mirroredmatchedprefix array of size 1 bigger than pattern, index of 1 for 1st char in string
    for index in range(1,len(pattern)):
        totalLength = (len(pattern)-index) + zArray[len(zArray)-index]
        if totalLength == len(pattern):
            mirroredMatchedPrefixArray[index] = zArray[len(zArray)-index]
        else:
            mirroredMatchedPrefixArray[index] = mirroredMatchedPrefixArray[index-1] # index of matched prefix is 1 greater than actual index
    mirroredMatchedPrefixArray[-1] = len(pattern)
    return mirroredMatchedPrefixArray


def gusfield(string):
    zArray = [0]*len(string)  # create zArray of size of input
    currentLeft = 0
    currentRight = 0
    # Base Case for Z2
    zTwoLength = 0
    if (len(string) > 1):  # String is greater than 1 char
        for char in range(1,len(string)):
            if (string[char] == string[char-1]):
                zTwoLength+=1
            else:
                break
        zArray[1] = zTwoLength  # Set Z2 value to length
        if zTwoLength == 0:
            currentLeft = 0
            currentRight = 0
        else:
            currentLeft = 1
            currentRight = zTwoLength

    # Pre process rest of String, ie Z2 onwards
    for stringIndex in range(2,len(string)):  # filling zArray
        if stringIndex > currentRight:  # Case 1, if k > r
            currentZ = 0
            q = 0
            for subStringChar in range(stringIndex,len(string)): # str[k...q-1]
                if string[subStringChar-stringIndex] == string[subStringChar]:
                    currentZ+=1
                else:
                    zArray[stringIndex] = currentZ
                    q = subStringChar - 1
                    break
            if currentZ > 0:
                zArray[stringIndex] = currentZ
                currentLeft = stringIndex
                currentRight = q

        else: # Case 2, if k <= r
            currentZ = 0
            if zArray[stringIndex-currentLeft] < (currentRight-stringIndex+1): # Case 2a
                zArray[stringIndex] = zArray[stringIndex-currentLeft]

            else:  # Case 2b
                for char in range(currentRight+1,len(string)):
                    if string[char] != string[char - stringIndex]:
                        zArray[stringIndex] = char - stringIndex
                        currentRight = char - 1
                        currentLeft = stringIndex
                        break
                    elif char + 1  == len(string):
                        zArray[stringIndex] = char - stringIndex + 1
                    else:
                        continue
    return zArray

if __name__ == "__main__":
    text = sys.argv[1]
    pattern = sys.argv[2]
    mirroredBoyerMoore(text,pattern)

