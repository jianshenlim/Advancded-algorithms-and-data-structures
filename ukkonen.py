
class Node:
    globalEnd = [0]
    def __init__(self):
        self.index = None
        self.isRoot = False
        self.isLeaf = False  # Is node a leaf
        self.edgeLetterArray = [None] * 91
        self.pointerArray = [None] * 91
        self.suffixLink = None

        self.parentNode = None  # used in task 3 to remember parent nodes, and edge from node to parent
        self.parentEdge = None
        self.leafIndexArray = None # array of pointers from all nodes to corresponding leaves based on leaf index

    def __str__(self):
        return str(self.edgeLetterArray)

    def isLeaf(self):
        if self.isLeaf:
            return True

    def isRoot(self):
        if self.isRoot:
            return True
    @ staticmethod
    def changeGlobalEnd(newEnd):
        Node.globalEnd[0] = newEnd

    @ staticmethod
    def getGlobalEnd():
        return Node.globalEnd

def ukkonen(text):
    root = Node()      # Create to root node
    root.isRoot = True
    root.suffixLink = root
    root.parentNode = root

    leafIndexArray = [None]*(len(text))

    implicitST = root  # Create ImplicitSuffixTree 1
    charIndex = ord(text[0]) - 36
    implicitST.edgeLetterArray[charIndex] = (0,root.getGlobalEnd())
    newLeaf = Node()    # Create leaf node

    newLeaf.isLeaf = True
    newLeaf.parentEdge = (0,root.getGlobalEnd()) # assign the parentedge leading to leaf
    newLeaf.index = 0
    leafIndexArray[newLeaf.index] = newLeaf # add leaf to leaf index array

    newLeaf.parentNode = root

    implicitST.pointerArray[charIndex] = newLeaf


    j = 1
    for phase in range(1, len(text)):  # N phases, begins at i + 1
        activeNode = root  # set root as active node
        root.changeGlobalEnd(phase)     # increment global end
        oldSuffixLinkNode = None
        rule3Ex = False
        while j <= phase:        # Suffix extension j, goes through all suffixes
            compareCount = 0
            if activeNode.isRoot is True:
                activeNode, remainderIndex = traverseNode(activeNode, j, phase, text)  # get active node and start index of the remainder,k for first extension of the phase
            suffixCharIndex = remainderIndex
            while suffixCharIndex <= phase:     # for each suffix

                charIndex = ord(text[suffixCharIndex]) - 36
                if suffixCharIndex == remainderIndex and activeNode.edgeLetterArray[charIndex] is not None:   # Saves all info of active node, lets us traverse the edge without losing the correct value, Only triggers at the first char of remainder
                    oldStartIndex = activeNode.edgeLetterArray[charIndex][0]
                    oldEndIndex = activeNode.edgeLetterArray[charIndex][1][0]

                    oldNode = activeNode.pointerArray[charIndex]    # node the active was pointer to
                    oldCharIndex = charIndex                        # the first char of edge
                    edgeLength = oldEndIndex - oldStartIndex + 1
                    remainderLength = phase - remainderIndex + 1

                if suffixCharIndex == remainderIndex and activeNode.edgeLetterArray[charIndex] == None:  # If node does not have existing edge AND we are ONLY at the first char of remainder,
                    newLeaf = Node()
                    newLeaf.isLeaf = True
                    newLeaf.index = j
                    leafIndexArray[j] = newLeaf # add new leaf to leafIndexArray

                    newLeaf.parentNode = activeNode # assign active node to be parent of leaf
                    newLeaf.parentEdge = (suffixCharIndex, root.getGlobalEnd())

                    activeNode.edgeLetterArray[charIndex] = (suffixCharIndex, root.getGlobalEnd())  # might have issue with the lastJI index here
                    activeNode.pointerArray[charIndex] = newLeaf
                    j += 1  # continue to next extension
                    break
                else:
                    if text[suffixCharIndex] != text[activeNode.edgeLetterArray[oldCharIndex][0]+ compareCount]: # If chars do not match, create new node and split

                        newNode = Node() # Create New Internal Node
                        oldIndex = ord(text[activeNode.edgeLetterArray[oldCharIndex][0]+ compareCount]) - 36

                        if oldNode.isLeaf is True:
                            newNode.edgeLetterArray[oldIndex] = (oldStartIndex + compareCount, root.getGlobalEnd())  # insert 2nd half of split edge
                            oldNode.parentEdge = (oldStartIndex + compareCount, root.getGlobalEnd())                 # change the parentEdge for the old node
                        else:
                            newNode.edgeLetterArray[oldIndex] = (oldStartIndex + compareCount, [oldEndIndex])
                            oldNode.parentEdge = (oldStartIndex + compareCount, [oldEndIndex])                       # change the parentEdge for the old node

                        newNode.pointerArray[oldIndex] = oldNode  # insert the old node to corresponding position in internal node

                        oldNode.parentNode = newNode    # reassign the old nodes parent link to the new internal node
                        newNode.suffixLink = root       # initially assign suffix link to root, will get assigned to new suffix link if it is created in next extension

                        if oldSuffixLinkNode == None:  # add suffix link from last extensions created node
                            oldSuffixLinkNode = newNode
                        else:
                            oldSuffixLinkNode.suffixLink = newNode
                            oldSuffixLinkNode = newNode

                        newLeaf = Node()            # Create new leaf for the new extension
                        newLeaf.isLeaf = True
                        newLeaf.index = j
                        leafIndexArray[j] = newLeaf     # assign leaf index to leaf Index Array
                        newLeaf.parentNode = newNode    # point leafs parent to new internal node

                        newIndex = ord(text[suffixCharIndex]) - 36

                        newNode.edgeLetterArray[newIndex] = (suffixCharIndex, root.getGlobalEnd())  # insert new edge for the leaf
                        newNode.pointerArray[newIndex] = newLeaf                                    # insert new pointer to leaf
                        newLeaf.parentEdge = (suffixCharIndex, root.getGlobalEnd())

                        activeNode.edgeLetterArray[oldCharIndex] = (oldStartIndex, [oldStartIndex + compareCount - 1])  # insert 1st half of original edge
                        activeNode.pointerArray[oldCharIndex] = newNode  # point active node to newly created internal node
                        newNode.parentNode = activeNode # assign new internal node its parent
                        newNode.parentEdge = (oldStartIndex, [oldStartIndex + compareCount - 1])

                        j += 1
                        break
                    elif remainderLength == edgeLength and activeNode.pointerArray[oldCharIndex].isLeaf is True and oldEndIndex == phase:
                        j += 1
                        break
                    elif text[suffixCharIndex] == text[activeNode.edgeLetterArray[oldCharIndex][0] + compareCount] and suffixCharIndex == phase:  # Rule 3 extension --> if reached the end of the remainder
                        j = j  # assign lastJI -1 + 1 value HERE
                        rule3Ex = True  # BREAK TWICE TO STOP GO TO NEXT PHASE
                        break
                    else:
                        suffixCharIndex += 1
                        compareCount += 1
            if rule3Ex is True:
                break
            activeNode = activeNode.suffixLink # traverse suffix link to next node for next extension
    root.leafIndexArray = leafIndexArray
    return root


def traverseNode(node,index,phase,text):
    remainderLength = phase - index + 1
    skipTotal = 0
    activeNode = node
    while index <= phase:

        charIndex = ord(text[index]) - 36
        if activeNode.pointerArray[charIndex] != None:
            subStringLength = activeNode.edgeLetterArray[charIndex][1][0] - activeNode.edgeLetterArray[charIndex][0] + 1  # end index - start index + 1 gets substring length ??
            skipTotal += subStringLength
            if remainderLength > skipTotal and activeNode.pointerArray[charIndex].isLeaf is False:  # end not reached, skip to node receiving edge skip/jump step
                index += subStringLength  # move to one position past end index of substring of current suffix
                activeNode = activeNode.pointerArray[charIndex]
                continue
            else:                       # if reached the correct active node
                return activeNode, index
        else:
            return activeNode, index    # return the active node and k value



