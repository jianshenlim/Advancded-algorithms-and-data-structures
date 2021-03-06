import sys
sys.path.append('..')
from ukkonen import ukkonen


def wildCardSuffixTreeMatching(textfile,patternfile):

    t = open(textfile,'r+')
    for line in t:
        text = line
    t.close()
    p = open(patternfile,'r+')
    for line in p:
        pattern = line
    p.close()

    outputFile = open("output_wildcard_matching.txt", "w")

    ukkonentree = ukkonen(text)
    checkNode(ukkonentree,0,text+"$",pattern,outputFile)
    outputFile.close()


def checkNode(node,index,text,pattern,outputfile):
    currentNode = node
    if node.isLeaf is True:
        return
    patIndex = index
    patChar = ord(pattern[patIndex]) - 36
    if pattern[index] == "?": # if current char in pattern is a wild card, we recusively call checkNode on each node connected to current node.
        for cnode in range(len(currentNode.pointerArray)):
            if currentNode.pointerArray[cnode] is not None:
                edgeStartIndex = currentNode.edgeLetterArray[cnode][0]
                edgeEndIndex = currentNode.edgeLetterArray[cnode][1][0]
                valid,value = checkEdge(edgeStartIndex,edgeEndIndex,text,index,pattern)
                if valid is True and value < 0:
                    printAllLeaf(currentNode.pointerArray[cnode],outputfile)
                if valid is True and value > 0:
                    checkNode(currentNode.pointerArray[cnode],index+value,text,pattern,outputfile)
    else:
        if currentNode.pointerArray[patChar] == None:  # if node has no corresponding char in edge list
            return
        else:   # if exists an existing edge corresponding to currently compared char in pat, check the edge
            edgeStartIndex = currentNode.edgeLetterArray[patChar][0]
            edgeEndIndex = currentNode.edgeLetterArray[patChar][1][0]
            valid,value = checkEdge(edgeStartIndex,edgeEndIndex,text,index,pattern)
            if valid is True and value < 0:
                printAllLeaf(currentNode.pointerArray[patChar],outputfile)
            if valid is True and value > 0:
                checkNode(currentNode.pointerArray[patChar], index + value, text, pattern,outputfile)


# Checks the edge we are going to traverse, if not possible to traverse, returns false, if possible to traverse,
# return True and a number, if number is -1, means we terminated in the edge, else we return the correspoding index
# in the pattern we would be after traversing the edge
def checkEdge(edgeStart,edgeEnd,text,index,pattern):
    patLength = len(pattern)
    subStringLength = edgeEnd - edgeStart + 1
    while index < patLength and edgeStart <= edgeEnd:
        if pattern[index] == "?" or pattern[index] == text[edgeStart]:
            edgeStart+=1
            index+=1
        else:
            return False, 0
    if index - 1 == patLength - 1:      # pattern successfully terminates in edge
        return True, -1
    if edgeStart-1 == edgeEnd:        # Traversed Edge successfully
        return True, subStringLength

# Prints all leaf nodes from the current node
def printAllLeaf(node,outputfile):    # print indexs of all leaves attached to current node
    currentNode = node
    pos = 0
    while pos < (len(currentNode.pointerArray)):
        if currentNode.isLeaf is True:
            textpos = currentNode.index
            textpos += 1
            outputfile.write(str(textpos)+"\n")
            break
        else:
            if currentNode.pointerArray[pos] is not None:
                printAllLeaf(currentNode.pointerArray[pos],outputfile)
        pos +=1



if __name__ == "__main__":
    text = sys.argv[1]
    pattern = sys.argv[2]
    wildCardSuffixTreeMatching(text,pattern)




