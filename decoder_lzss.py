import sys
from bitarray import bitarray



def decoderLzss(encoded):
    a = bitarray()
    with open(encoded, 'rb') as fh:
        a.fromfile(fh)

    encodedString = a.to01()
    numOfUniAscii,nextpos = decodeElias(0,encodedString)
    huffManTree, nextpos = buildHuffman(encodedString,numOfUniAscii,nextpos)
    decodeData(huffManTree,encodedString,nextpos)

class huffmanNode():

    def __init__(self,char=None,occurrence=None,leftChild=None, rightChild=None):
        self.char = char
        self.charOccurrence = occurrence
        self.leftChild = leftChild
        self.rightChild = rightChild
        self.isLeaf = False
        self.isRoot = False

    def __lt__(self, other):
        return self.charOccurrence < other.charOccurrence


def asciiToChar(ascii):
    return (chr(int(ascii,2)))

def decodeElias(startpos,bincode): # Takes whole binary code as string, outputs the decoded number and the next position in the code to process
    pos = startpos
    lengthComponent = 1
    component = bincode[pos:pos+lengthComponent]
    b = bitarray(component)
    decoded = False
    while not decoded:
        component = bincode[pos:pos + lengthComponent]
        component = bitarray(component)
        if component[0] == True:
            return (int(component.to01(),2)),pos+lengthComponent
            decoded = True
        else:
            component[0] = True
            pos += lengthComponent
            lengthComponent = int(component.to01(),2) + 1


def buildHuffman(bincode,noOfUniqueASCII,startPos):
    root = huffmanNode()    # Create root of new huffman encode tree
    root.isRoot = True
    noOfChars = 0

    while noOfChars < noOfUniqueASCII:
        asciiComponent = bincode[startPos:startPos+7]
        asciiChar = asciiToChar(asciiComponent) # get ascii char

        huffmanEncodeLength,nextPos = decodeElias(startPos+7,bincode)
        huffmanEncoding = bincode[nextPos:nextPos+huffmanEncodeLength] # get the chunk corresponding to the huffman encoding
        addNode(root,huffmanEncoding,asciiChar)
        startPos = nextPos+huffmanEncodeLength # get the pos after the huffmanEncoding
        noOfChars+=1

    return root, startPos   # returns the root of the huffman tree and the next pos in encoding after the huffman section



def addNode(root,encode,char):  # builds the huffman tree
    currentNode = root
    for x in range (len(encode)):
        if encode[x] == "0":
            if currentNode.leftChild is None:
                currentNode.leftChild = huffmanNode()
                currentNode = currentNode.leftChild
            else:
                currentNode = currentNode.leftChild
        else:
            if currentNode.rightChild is None:
                currentNode.rightChild = huffmanNode()
                currentNode = currentNode.rightChild
            else:
                currentNode= currentNode.rightChild

    currentNode.isLeaf = True
    currentNode.char = char


def decodeData(huffman,bincode,startpos):

    outputFile = open("output_decoder_lzss.txt", "w")
    root = huffman
    currentNode = root

    noOfFormatFields,nextpos = decodeElias(startpos,bincode)
    noOfCompletedFields = 0
    formatChar = True
    formatType = None
    output = ""

    while nextpos < len(bincode):   # iterates through entire binary encoding
        if noOfCompletedFields == noOfFormatFields: #If fully completed all formats
            break
        if formatChar is True:
            if bincode[nextpos] == "1": # find out format type, then moves on the next position
                formatType = 1
                nextpos += 1
                formatChar = False
            else:
                formatType = 0
                nextpos += 1
                formatChar = False
        else:
            if formatType == 1:     # if format type is 1, we find character from huffman encoding
                if bincode[nextpos] == "0":
                    currentNode = currentNode.leftChild
                else:
                    currentNode = currentNode.rightChild

                if currentNode.isLeaf is True:  # iterate thorugh tree until reach a leaf, add char to output and reset node to root
                    output+=currentNode.char
                    noOfCompletedFields +=1
                    formatChar = True
                    currentNode = root

                nextpos+=1
                continue
            else:                           # if format type is 0, get the backstep distance and seq length
                backStep, nextpos = decodeElias(nextpos,bincode)
                length, nextpos = decodeElias(nextpos,bincode)
                for _ in range(length):
                    output+= output[-backStep]
                formatChar = True
                noOfCompletedFields+=1

    if noOfCompletedFields == noOfFormatFields:
        outputFile.write(output)

    outputFile.close()


if __name__ == "__main__":
    binfile = sys.argv[1]
    decoderLzss(binfile)
