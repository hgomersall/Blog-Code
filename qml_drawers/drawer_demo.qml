import QtQuick 1.0

Item {
    width: 640
    height: 480

    Rectangle {
        anchors.right: parent.right
        anchors.top: parent.top
        color: "orange"
        width: 300
        height: 300
        Image {
            anchors.fill: parent
            smooth: true
            source: "images/face.png"
        }
    }

    DrawerChest {
        anchors.fill: parent 
    }
}
