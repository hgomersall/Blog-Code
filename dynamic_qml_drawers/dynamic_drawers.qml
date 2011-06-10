import QtQuick 1.0

Item {
    width: 640
    height: 480

    Rectangle {
        x: 30
        y: 30
        width: 50
        height: 30
        color: "green"
        MouseArea {
            anchors.fill: parent
            onClicked: {
                drawer_chest.addDrawer()
            }
        }
    }
    Rectangle {
        x: 100
        y: 30
        width: 50
        height: 30
        color: "red"
        MouseArea {
            anchors.fill: parent
            onClicked: {
                drawer_chest.removeDrawer(0)
            }
        }
    }

    DrawerChest {
        id: drawer_chest
        anchors.fill: parent
        anchors.leftMargin: 0 //parent.width/6
        anchors.rightMargin: 0 //parent.width/6
    }
}
