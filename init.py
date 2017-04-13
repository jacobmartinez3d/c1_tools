import c1_tools
import c1_shotBrowser
import nuke
import nukescripts

#_after render override_______________________________________________________________
# file = nuke.filename(nuke.thisNode())

#_luis solver tab_______________________________________________________________
nukeOriginalCreateNode = nuke.createNode
def createLuisWriteNode(node, knobs = "", inpanel = True):
    result = nukeOriginalCreateNode(node, knobs, inpanel)
    if node == "Write":
        tab = nuke.Tab_Knob('Luis_Solver')
        result.addKnob(tab)
        lsBool = nuke.Boolean_Knob('lsBool','Run Luis_Solver after render')
        result.addKnob(lsBool)

    return result
# nuke.addAfterBackgroundRender(c1_tools.Luis_Solver(file))
nuke.createNode = createLuisWriteNode


nuke.addAfterRender(c1_tools.Luis_Solver())
