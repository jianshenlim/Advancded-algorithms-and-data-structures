
import sys
from bitarray import bitarray
import heapq


class huffmanNode():

    def __init__(self, char, occurrence, leftChild=None, rightChild=None):
        self.char = char
        self.charOccurrence = occurrence
        self.leftChild = leftChild
        self.rightChild = rightChild
        self.isLeaf = False
        self.isRoot = False

    def __lt__(self, other):
        return self.charOccurrence < other.charOccurrence


def eliasCode(number):  # retuns the elias code for any integer entered
    binNumber = bin(number)[2:]
    outputBinNumber = bitarray(binNumber)
    while len(binNumber) != 1:
        binNumber = bin(len(binNumber) - 1)[2:]
        newNumber = "0" + binNumber[1:]
        outputBinNumber = bitarray(newNumber) + outputBinNumber
        binNumber = newNumber
    return outputBinNumber


def sevenBitAscii(char):  # returns the 7bit ascii value of char
    decNum = ord(char)
    binNum = bin(decNum)[2:]
    binNum = binNum.zfill(7)
    return bitarray(binNum)


def huffmanCode(text):  # generates and returns the huffman tree of the text encoding
    charOccurrences = {}
    minHeap = []
    for char in text:  # Compute Frequencies
        if char in charOccurrences:
            charOccurrences[char] += 1
        else:
            charOccurrences[char] = 1

    for char in charOccurrences:  # Add all chars with their freq into the min heap
        newNode = huffmanNode(char, charOccurrences.get(char))
        newNode.isLeaf = True
        heapq.heappush(minHeap, newNode)

    while len(minHeap) != 1:  # Create huffman binary tree
        firstLowestFreq = heapq.heappop(minHeap)  # Get the 2 smallest frequencies
        secondLowestFreq = heapq.heappop(minHeap)

        firstChar = firstLowestFreq.char
        secondChar = secondLowestFreq.char
        combinedChar = firstChar + secondChar
        totalFreq = firstLowestFreq.charOccurrence + secondLowestFreq.charOccurrence
        newNode = huffmanNode(combinedChar, totalFreq, firstLowestFreq,
                              secondLowestFreq)  # create new node with combined frequencies and read add to heap
        if len(minHeap) == 0:  # if heap has no nodes left, means current node will be root
            newNode.isRoot = True
        heapq.heappush(minHeap, newNode)

    huffmanTree = minHeap[0]  # get the root node of huffman tree
    return getCharCodes(huffmanTree, bitarray(), {})  # return a dict() containing all chars and their encodings


def getCharCodes(node, codeString, codeDict):  # traverse the tree, and adds the char and its encoding to a dict()
    leftCodeString = codeString + bitarray("0")
    rightCodeString = codeString + bitarray("1")
    if node:
        getCharCodes(node.leftChild, leftCodeString, codeDict)
        getCharCodes(node.rightChild, rightCodeString, codeDict)
        if node.isLeaf is True:
            codeDict[node.char] = codeString

        if node.isRoot is True:
            return codeDict


def buildEncodedHeader(codeDict):  # builds the encoded header string
    uniqueASCIIEncode = eliasCode(len(codeDict))  # get encoded number of unique chars
    for char in codeDict:  # add each ascii binary, its char encoding and its length to the string
        aSCIIbin = sevenBitAscii(char)
        charCode = codeDict[char]
        charCodeLen = eliasCode(len(charCode))
        uniqueASCIIEncode += aSCIIbin + charCodeLen + charCode

    return uniqueASCIIEncode


# encodes the data section of text and returns the whole string of encoding
def lzss(text, windowSize, bufferSize):
    startPos = 0
    endPos = len(text) - 1
    huffmanCodeDict = huffmanCode(text)
    encodeHeader = buildEncodedHeader(huffmanCodeDict)
    numberOfFormatFields = 0
    encodeData = bitarray()
    while startPos <= endPos:
        numberOfFormatFields += 1
        output, nextPos = lzssCheck(text, startPos, windowSize, bufferSize, encodeData, huffmanCodeDict)
        encodeData = output
        startPos = nextPos

    output = encodeHeader + eliasCode(numberOfFormatFields) + encodeData
    return output


# creates the encoding based on current position, window and buffer size, and adds it to the output string, returns output string and next position after where the encoding stopped
# uses gusfield to find the nearest pattern which matches the in the buffer,
def lzssCheck(text, currentPos, windowSize, bufferSize, output, codeDict):
    longestMatch = 0
    stepsBack = 0

    windowStartIndex = currentPos - windowSize
    if windowStartIndex < 0:
        windowStartIndex = 0

    bufferEndIndex = currentPos + bufferSize - 1
    if bufferEndIndex > len(text) - 1:
        sizeDiff = bufferEndIndex - len(text) - 1
        bufferSize -= sizeDiff
        bufferEndIndex = len(text) - 1

    if currentPos == 0:
        output += bitarray("1") + codeDict.get(text[0])
        return output, currentPos + 1

    pat = text[currentPos:bufferEndIndex + 1]
    search = text[windowStartIndex:bufferEndIndex + 1]
    searchString = pat + "$" + search
    zAlgo = gusfield(searchString)

    for index in range(1, (len(searchString) - len(pat))):
        matchlength = zAlgo[index]
        if matchlength > longestMatch:
            longestMatch = matchlength
            stepsBack = len(searchString) - len(pat) - index
        if matchlength == longestMatch:
            currentStepBack = len(searchString) - len(pat) - index
            if currentStepBack < stepsBack:
                stepsBack = currentStepBack

    if longestMatch < 3:
        output += bitarray("1") + codeDict.get(text[currentPos])
        return output, (currentPos + 1)
    else:
        output += bitarray("0") + eliasCode(stepsBack) + eliasCode(longestMatch)
        return output, (currentPos + longestMatch)


def gusfield(string):
    zArray = [0] * len(string)  # create zArray of size of input
    currentLeft = 0
    currentRight = 0
    # Base Case for Z2
    zTwoLength = 0
    if (len(string) > 1):  # String is greater than 1 char
        for char in range(1, len(string)):
            if (string[char] == string[char - 1]):
                zTwoLength += 1
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
    for stringIndex in range(2, len(string)):  # filling zArray
        if stringIndex > currentRight:  # Case 1, if k > r
            currentZ = 0
            q = 0
            for subStringChar in range(stringIndex, len(string)):  # str[k...q-1]
                if string[subStringChar - stringIndex] == string[subStringChar]:
                    currentZ += 1
                else:
                    zArray[stringIndex] = currentZ
                    q = subStringChar - 1
                    break
            if currentZ > 0:
                zArray[stringIndex] = currentZ
                currentLeft = stringIndex
                currentRight = q

        else:  # Case 2, if k <= r
            currentZ = 0
            if zArray[stringIndex - currentLeft] < (currentRight - stringIndex + 1):  # Case 2a
                zArray[stringIndex] = zArray[stringIndex - currentLeft]

            else:  # Case 2b
                for char in range(currentRight + 1, len(string)):
                    if string[char] != string[char - stringIndex]:
                        zArray[stringIndex] = char - stringIndex
                        currentRight = char - 1
                        currentLeft = stringIndex
                        break
                    elif char + 1 == len(string):
                        zArray[stringIndex] = char - stringIndex + 1
                    else:
                        continue
    return zArray


def encodeLzss(textfile, windowSize, bufferSize):
    t = open(textfile, 'r+')
    text = t.read()
    t.close()
    binfile = open('output_encoder_lzss.bin', 'wb')
    binOutput = lzss(text, windowSize, bufferSize)
    binOutput.tofile(binfile)
    binfile.close()


if __name__ == "__main__":
    text = sys.argv[1]
    winSize = sys.argv[2]
    buffSize = sys.argv[3]
    encodeLzss(text, int(winSize), int(buffSize))
