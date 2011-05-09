import Qt 4.7

Rectangle {
    id: control_window
    x: 30
    y: 30
    width: 500; height: 200
    color: "lightgray"
    opacity: 0.5
    
    Slider { id: slider_x; x: 25; y: 32; minimum: 0; maximum: 360*16}
    Slider { id: slider_y; x: 25; y: 80; minimum: 0; maximum: 360*16}
    Slider { id: slider_z; x: 25; y: 128; minimum: 0; maximum: 360*16}
}
