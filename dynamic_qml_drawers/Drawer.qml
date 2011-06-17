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
    
    // Properties to change commonly
    property string title
    property int idx: 0
    property int colorIndex: 0
    property real openHeight: 400
    property real tabHeight: 30
    property int numberOfDrawers: 1

    // Child opacities
    property real tabOpacity: 0.8
    property real textOpacity: 1.0
    property real bgOpacity: 0.75

    property real closedRight: Math.floor(width/numberOfDrawers*(idx + 1))
    property real closedLeft: Math.floor(width/numberOfDrawers*idx)
    
    property real closedZValue: 10
    property real openZValue: -10
    
    // Transition properties
    // put the closing drawer to be between the closed tabs and the open
    // drawers
    property real closingZValue: (closedZValue + openZValue)/2
    property real openingZValue: openZValue
    property real closingOpacity: 0.3

    // Dynamic properties that change with state
    property real leftOffset: 0
    property real currentHeight: drawer.tabHeight
    property real currentWidth: width
    opacity: 1.0

    signal drawerOpened(int idx)
    signal drawerClosed(int idx)
    
    title: ""
    state: "closed"

    Behavior on closedRight {
        id: closed_right_behavior
        enabled: false
        NumberAnimation {
            duration: 1000
            easing.type: Easing.OutElastic
        }
    }
    Behavior on closedLeft {
        id: closed_left_behavior
        enabled: false
        NumberAnimation {
            duration: 1000
            easing.type: Easing.OutElastic
        }
    }
    
    function addDrawerElement(component){
        console.log(delegate)
    }

    function aDrawerOpened(drawer_idx){
        // If the drawer that was opened is not this one, we close immediately
        if (drawer_idx != idx){
            closeDrawer()
        }
    }

    function reindex(deleted_index){
        if (idx > deleted_index) {
            idx = idx - 1
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

    function setColor(color_index){
        colorIndex = color_index
    }

    function enableDrawMoveAnimation(){
        closed_right_behavior.enabled = true
        closed_left_behavior.enabled = true
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
            source: image_sources[drawer.colorIndex%image_sources.length]
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
                z: drawer.openZValue
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
            PropertyChanges {
                target: drawer
                currentHeight: drawer.tabHeight
                currentWidth: drawer.closedRight-drawer.closedLeft
                leftOffset: drawer.closedLeft
            }
        }
    ]

    transitions: [
        Transition {
            id: to_open_transition
            to: "open"
            SequentialAnimation{
                PropertyAction {target: drawer; property: "z"; value: drawer.openingZValue}
                PropertyAnimation {
                    id: open_animation
                    properties: "currentHeight,currentWidth,leftOffset"
                    easing.type: Easing.InOutQuad
                }
                PropertyAction {target: drawer; property: "z"; value: drawer.openZValue}
            }
        },

        Transition {
            id: to_close_transition
            to: "closed"
            SequentialAnimation{
                // Move the closing drawer behind the other closed drawers
                PropertyAction {target: drawer; property: "z"; value: drawer.closingZValue}
                PropertyAction {target: containing_rect; property: "opacity"; value: drawer.closingOpacity}
                PropertyAnimation {
                    id: close_animation
                    properties: "currentHeight,currentWidth,leftOffset"
                    easing.type: Easing.InOutQuad
                }
                PropertyAction {target: drawer; property: "z"; value: drawer.closedZValue}
                PropertyAction {target: containing_rect; property: "opacity"; value: 1.0}
            }
        }
    ]
}
