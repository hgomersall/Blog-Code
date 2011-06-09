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

Item {
    id: drawer_chest
    property int openDrawer: 0
    anchors.fill: parent

    signal newDrawerOpened(int idx)

    Repeater {
        id: drawer_repeater
        model: 3
        Drawer {
            idx: index
            closedRight: Math.floor(parent.width/drawer_repeater.count*(idx + 1))
            closedLeft: Math.floor(parent.width/drawer_repeater.count*idx)
            state: "closed"
            title: "Test"

            Connections {
                onDrawerOpened: {
                    drawer_chest.drawerOpened(idx)
                }
                onDrawerClosed: {
                    drawer_chest.drawerClosed(idx)
                }
            }

            Component.onCompleted: {
                drawer_chest.newDrawerOpened.connect(aDrawerOpened)

            }
        }

    }
    
    function drawerOpened(opened_drawer_idx){
        newDrawerOpened(opened_drawer_idx)
    }

    function drawerClosed(closed_drawer){
    }

}
