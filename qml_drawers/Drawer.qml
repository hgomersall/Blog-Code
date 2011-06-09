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
    id: drawer
    
    //width: parent.width
    //height: parent.height
    anchors.fill: parent
    z: 15

    property string title
    property int idx: 0
    property real openHeight: 400
    property real tabHeight: 30
    property real closedRight: width
    property real closedLeft: 0
    property real closingOpacity: 0.3

    property real tabOpacity: 0.8
    property real textOpacity: 1.0
    property real bgOpacity: 0.75

    property real leftOffset: 0
    property real currentHeight: openHeight
    property real currentWidth: width

    signal drawerOpened(int idx)
    signal drawerClosed(int idx)
    
    title: ""
    state: "closed"

    function aDrawerOpened(drawer_idx){
        // If the drawer that was opened is not this one, we close immediately
        if (drawer_idx != idx){
            closeDrawer()
        }
    }

    function closeDrawer(){
        if (state != "closed"){
            state = "closed"
        }
    }

    function openDrawer(){
        state = "open"
    }
    
    Component.onCompleted: {
        if (state == "closed") {
            openDrawer()
            closeDrawer()
        } else {
            closeDrawer()
            openDrawer()
        }
    }

    Rectangle {
        id: containing_rect

        height: drawer.currentHeight
        width: drawer.currentWidth

        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.leftMargin: parent.leftOffset
        color: "transparent"
        
        // This opacity should be 1 - the opacity is set for individual elements
        opacity: 1.0

        BorderImage {
            // The tab of the drawer
            id: tab
            z: 0.0
            width: parent.width
            anchors.left: parent.left
            anchors.top: parent.top
            height: drawer.tabHeight
            smooth: false
            border {left: 10; top: 7; right: 10; bottom: 4}            
            horizontalTileMode: BorderImage.Repeat
            verticalTileMode: BorderImage.Repeat

            property variant image_sources: [
                "images/0_red.png",
                "images/90_green.png",
                "images/170_lilac.png"
            ]
            source: image_sources[drawer.idx%image_sources.length]
            opacity: drawer.tabOpacity

            MouseArea {
                acceptedButtons: Qt.LeftButton
                anchors.fill: parent
                onClicked: {
                    drawer.state == "open" ?
                        closeDrawer() : openDrawer();
                }

            }
        }
        
        Text {
            id: tab_text
            z: 1.0
            color: "black"
            text: drawer.title
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.topMargin: 5
            anchors.leftMargin: 10
            opacity: drawer.textOpacity
        }

        Rectangle {
            id: contents
            color: "black"
            z: 0.0
            height: parent.height-drawer.tabHeight
            width: parent.width
            radius: 0
            smooth: false
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            opacity: drawer.bgOpacity
        }

    }

    states: [
        State {
            name: "open"
            StateChangeScript {
                name: "opening_signal"
                script: {
                    drawerOpened(drawer.idx)

                }
            }
            PropertyChanges {
                target: drawer 
                currentHeight: drawer.openHeight
                currentWidth: drawer.width
                leftOffset: 0
                z: -10
            }
        },
        State {
            name: "closed"
            StateChangeScript {
                name: "closing_signal"
                script: {
                    drawerClosed(drawer.idx)

                }
            }
            StateChangeScript {
                name: "begin_close"
                script: {
                    drawer.opacity = drawer.closingOpacity
                }
            }
            StateChangeScript {
                name: "end_close"
                script: {
                    // This is a bit mucky - the final z value
                    // is 15, but starts out as the value given 
                    // by the property change below. I couldn't work
                    // out a way to make the property change during 
                    // transition but ending on something else.
                    drawer.opacity = 1.0
                    drawer.z = 15
                }
            }
            PropertyChanges {
                target: drawer
                currentHeight: drawer.tabHeight
                currentWidth: drawer.closedRight-drawer.closedLeft
                leftOffset: drawer.closedLeft
                z: 10
            }
        }
    ]

    transitions: [
        Transition {
            to: "open"
            SequentialAnimation{
                PropertyAnimation {
                    properties: "currentHeight,currentWidth,leftOffset"
                    easing.type: Easing.InOutQuad
                }
            }
        },
        Transition {
            to: "closed"
            SequentialAnimation{
                ScriptAction { scriptName: "begin_close" }
                PropertyAnimation {
                    properties: "currentHeight,currentWidth,leftOffset"
                    easing.type: Easing.InOutQuad
                }
                ScriptAction { scriptName: "end_close" }
            }
        }
    ]
}
