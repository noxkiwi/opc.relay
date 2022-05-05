import random
import threading
import time
import os
import subprocess
from RelayItem import RelayItem
from DatabaseManager import DatabaseManager
from noxLogger import noxLogger

defStatus = 0
# I am the relay service class.U
class RelayService:
    workingDirectory = os.path.dirname(os.path.realpath(__file__))
    namespace = "nox.lightsystem.opc.relay"
    server = ""
    serverNamespace = ""
    root = ""
    items = []
    tree = {}
    scanThread = None
    sendThread = None
    scanEnable = False

    def __init__(self, server, servernamespace):
        self.server = server
        self.serverNamespace = servernamespace
        # Register Root node
        self.root = self.server.get_objects_node()

        # Read items from
        dm = DatabaseManager()
        queryString = """
SELECT 
	`relay_id`,
	`relay_created`,
	`relay_modified`,
	`relay_flags`,
	`setpoint`.`opc_item_address`	AS `setpointAddress`,
	`relay_enable`,
	`relay_disable`,
	`current`.`opc_item_address`	AS `currentAddress`,
	`relay_name`
FROM
		`relay`
JOIN	`opc_item`	AS	`setpoint`	ON(`setpoint`.`opc_item_id` = `relay`.`opc_item_setpoint`)
JOIN	`opc_item`	AS	`current`	ON( `current`.`opc_item_id` = `relay`.`opc_item_current` )
WHERE TRUE
	AND `relay`.`relay_flags`		&1=1
	AND `setpoint`.`opc_item_flags`	&1=1
	AND `current`.`opc_item_flags`	&1=1;"""
        queryData = (1,2,3)


        cursor = dm.read(queryString, queryData)
        for row in cursor:
            item = RelayItem(row)
            item.uaSetpoint = self.MakeNode(item.setpoint)
            item.uaCurrent = self.MakeNode(item.current)
            item.uaCurrent.set_value(item.flags)  # Write persistent value
            setVal = 0
            if item.flags & 2 is 2:
                setVal = 1
            item.uaSetpoint.set_value(setVal)
            item.uaSetpoint.set_writable()  # make setpoint writable
            self.items.append(item)

    # Create new branches to the end node
    def GetBranchedNode(self, tree):
        branches = tree.split(".")
        branchAddress = ""
        branchIndex = 1
        parentNode = self.root
        delim = ""
        del branches[-1]
        for branch in branches:
            branchAddress = branchAddress + delim + branch
            if not branchAddress in self.tree:
                parentNode = parentNode.add_object(self.serverNamespace, branch)
                self.tree[branchAddress] = parentNode
            else:
                parentNode = self.tree[branchAddress]
            delim = "."
            branchIndex = branchIndex + 1
        return parentNode

    # Return last Node name
    def GetEndNode(self, tree):
        return tree.split(".")[-1]

    # Generate Tree Branches and the end node.
    def MakeNode(self, tree):
        return self.GetBranchedNode(tree).add_variable(self.serverNamespace, self.GetEndNode(tree), 1)

    # Start the server
    def start(self):
        self.server.start()

    # Stop the server
    def stop(self):
        self.server.stop()

    # Send the given command via 433.93MHz
    def send(self, command):
        subprocess.run([self.workingDirectory + "/sender", str(command)])
        return None

    # Sender thread
    def _send(self):
        while self.scanEnable:
            time.sleep(0.5)
            for item in self.items:
                setVal = int(item.uaSetpoint.get_value())
                if setVal == 1:
                    self.send(item.enable)
                else:
                    self.send(item.disable)

    # Scanner thread
    def _scan(self):
        while self.scanEnable:
            time.sleep(1)
            for item in self.items:
                setVal = item.uaSetpoint.get_value()
                noxLogger.debug("ITEM: " + item.name)
                noxLogger.debug("  -   SET: " + item.setpoint)
                noxLogger.debug("  -    IS: " + item.current)
                noxLogger.debug("  -SET TO: " + str(setVal))
                noxLogger.debug("  - FRESH: " + str(item.uaCurrent.get_value()))
                if (item.uaCurrent.get_value() == setVal):
                    noxLogger.debug("  -  RSLT: not changed")
                    continue
                noxLogger.debug("  -  RSLT: changed")
                item.uaCurrent.set_value(setVal)
                myVal = 1 + 2 * setVal

                # Store that the relay has been changed so it is not turned to the wrong
                # status when the server restarts.
                dm = DatabaseManager()
                queryString = "UPDATE relay SET relay_flags = " + str(myVal) + " WHERE relay_id = " + str(item.id) + ";"
                queryData = (1,2,3)
                dm.query(queryString, queryData)


    def scan_on(self):
        self.scanThread = threading.Thread(target=self._scan)
        self.sendThread = threading.Thread(target=self._send)
        self.scanEnable = True
        self.scanThread.start()
        self.sendThread.start()

    def scan_off(self):
        self.scanEnable = False
        self.scanThread.join()
        self.sendThread.join()
