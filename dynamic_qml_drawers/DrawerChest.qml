/*
* Copyright 2011 Knowledge Economy Developments Ltd
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Lesser General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU Lesser General Public License for more details.
*
* You should have received a copy of the GNU Lesser General Public License
* along with this program. If not, see <http://www.gnu.org/licenses/>.
*
* Henry Gomersall
* heng@kedevelopments.co.uk
*/

import QtQuick 1.0
import "DrawerChest.js" as Code 

Item {
    id: drawer_chest

    property int numberOfDrawers: 0
    property int nextColor: 0
    
    anchors.fill: parent
    
    signal newDrawerOpened(int idx)
    signal drawerRemoved(int idx)

    Component {
        id: drawerDelegate
        Drawer {
            state: "closed"
            title: "Test"
            numberOfDrawers: drawer_chest.numberOfDrawers
        }
    }

    Component.onCompleted: {
        // Create at least one drawer to start with
        addDrawer()
    }

    function addDrawer(){
        numberOfDrawers += 1
        var new_drawer = drawerDelegate.createObject(parent)
        
        new_drawer.idx = numberOfDrawers - 1
        
        new_drawer.setColor(nextColor)
        nextColor += 1        

        // Connect the signals
        new_drawer.drawerOpened.connect(drawerOpened)
        new_drawer.drawerClosed.connect(drawerClosed)

        newDrawerOpened.connect(new_drawer.aDrawerOpened)
        drawerRemoved.connect(new_drawer.reindex)

        Code.drawer_array.push(new_drawer)
    }

    function removeDrawer(index){
        if (Code.drawer_array.length > 0 & index + 1 <= Code.drawer_array.length){

            var rem_drawer = Code.drawer_array[index]
            
            // Disconnect the signals
            drawer_chest.newDrawerOpened.disconnect(rem_drawer.aDrawerOpened)
            drawer_chest.drawerRemoved.disconnect(rem_drawer.reindex)
            
            // Delete the drawer
            rem_drawer.destroy()

            // Remove the drawer from the array        
            Code.drawer_array.splice(index, 1)

            drawerRemoved(index)
            numberOfDrawers -= 1
        }
    }

    function drawerOpened(opened_drawer_idx){
        newDrawerOpened(opened_drawer_idx)
    }

    function drawerClosed(closed_drawer){
    }

}
