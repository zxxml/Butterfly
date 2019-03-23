// 全局参数设定
int BAUD_RATE = 9600;
int ANALOG_PORTS_NUM = 6;
int ANALOG_PORTS[] = {3, 5, 6, 9, 10, 11};

bool activate_serial(){
    Serial.begin(BAUD_RATE);
    return true;
}

bool activate_gpio(){
    for (int i=0; i<ANALOG_PORTS_NUM; i++)
        pinMode(ANALOG_PORTS[i], OUTPUT);
    return true;
}

void setup(){
    activate_serial();
    activate_gpio();
}

typedef struct _Packet{
    string action;
    string detail;
    int value;
}Packet;

Packet unpack_packet(string packet){
    
}

bool control_vehicle(string detail, int value){
    return true;
}

bool control_camera(string detail, int value){
    return true;
}

bool control_minigun(string detail, int value){
    return true;
}

bool move_minigun(string detail, int value){
    return true;
}

bool fire_minigun(string detail, int value){
    value += 65535;
    return true;
}

void loop(){
}
