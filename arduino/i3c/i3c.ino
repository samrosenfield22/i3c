

#include <Wire.h>

#include "i3c_config.h"

#define SDA_PIN (PC4)
#define SCL_PIN (PC5)

#define LOGIC_MIN_THRESH_5V (922) //for now, this is 4.5V -- really should check the i2c spec
#define LOGIC_MAX_THRESH_3V3 (743)  //3.3 * 1.1
#define LOGIC_MIN_THRESH_3V3 (608)  //3.3 * 0.9


//serial monitor printf
char printbuf[161];
#define smprintf(...) do {sprintf(printbuf, __VA_ARGS__); Serial.print(printbuf);} while(0)

/*typedef struct i2cdev_s
{
    const char *name;
    uint8_t addr;
    uint8_t whoami_ct, config_ct, write_ct;
    uint8_t *regs;
} i2cdev;*/

enum ERRCODE
{
    ERRC_BUS_LINES_LO = 0,
    ERRC_ABNORMAL_BUS_VOLTAGES = 1,

};

enum WARNCODE
{
    WARNC_WRONG_LOGIC_LVL = 0,
};

//
void i2c_bus_test(void);
void i2c_scan(void);
bool i2c_is_device_up(uint8_t sladdr);
void i2c_write_reg(uint8_t sladdr, uint8_t regaddr, uint8_t val);
void i2c_write_byte_stream(uint8_t sladdr, int len, uint8_t *bytes);
uint8_t i2c_read_reg(uint8_t sladdr, uint8_t regaddr);
bool i2c_check_reg_val(uint8_t *v, uint8_t sladdr, uint8_t reg, uint8_t expected);
//void hexdump(uint8_t *data, bool *stable, uint16_t end_addr);
void send_signature(uint8_t sladdr, uint8_t *regmap, bool *stable, uint16_t end_addr);
//bool warn_prompt(const char *str);
void print_hex_leading(uint8_t b);
void error(ERRCODE err);
void warn(WARNCODE warn);

//
/*i2cdev TPS65023 =
{
    "TPS65023",
    0x48,
    1, 2, 0,
    (uint8_t[]) {
      0x00, 0x23, //whoami
      0x05, 0x08, 0x06, 0x80  //config
    }
};*/
void setup()
{

  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
  
  //init stuff
  Wire.begin();
  Serial.begin(9600);
  delay(100);
  
  while(!Serial.available());
  String startcmd = Serial.readString();
  if(startcmd != "go duiner go\n")
      while(1);
  Serial.println("ok");
  digitalWrite(13, HIGH);

  //////
  warn(WARNC_WRONG_LOGIC_LVL);
  uint8_t regmap[MAX_REGISTERS];
  bool stable[MAX_REGISTERS];
  stable[8] = false;
  send_signature(0xDE, regmap, stable, 0x20);
  send_signature(0xFF, regmap, stable, 0x20);

  Serial.println("done");


  //electrical test
  i2c_bus_test();

  //find all i2c devices, send their signatures to the app
  i2c_scan();

  Serial.println("done");
}

void loop()
{
  
}

//////////////////////////////////////////////////////////

void i2c_bus_test(void)
{
    //SDA/SCL should always idle high
    for(int i=0; i<1000; i++)
    {
      if(digitalRead(SDA_PIN)==LOW || digitalRead(SCL_PIN)==LOW)
          error(ERRC_BUS_LINES_LO);
    }

    //check the high logic level
    int sda_lvl = analogRead(SDA_PIN);
    int scl_lvl = analogRead(SCL_PIN);

    if( (LOGIC_MIN_THRESH_3V3 < sda_lvl && sda_lvl < LOGIC_MAX_THRESH_3V3) &&
    (LOGIC_MIN_THRESH_3V3 < scl_lvl && scl_lvl < LOGIC_MAX_THRESH_3V3) )
    {
      #ifdef WARN_FOR_3V3_LOGIC
          warn(WARNC_WRONG_LOGIC_LVL);
      #endif
      return;
    }
    else if(LOGIC_MIN_THRESH_5V < sda_lvl && LOGIC_MIN_THRESH_5V < scl_lvl)
        return;
    else
    {
      error(ERRC_ABNORMAL_BUS_VOLTAGES);
    }
}

//if dump is true, this reads the first n registers of each device found and prints them
void i2c_scan(void)
{
  //int total = 0;
  for(int a=1; a<0x80; a++)
  {
    if(i2c_is_device_up(a))
    {
         //smprintf("\n\nI2C device found at address 0x%02X (%d)\n", a, a);
         //total++;

            uint8_t regmap[MAX_REGISTERS];
            bool stable[MAX_REGISTERS];
            for(int i=0; i<MAX_REGISTERS; i++)
                stable[i] = true;
            
            //scan registers
            for(int i=0; i<MAX_REGISTERS; i++)
                regmap[i] = i2c_read_reg(a, i);
            for(int s=0; s<REGISTER_SCAN_CT-1; s++)
            {
                delay(REGISTER_SCAN_DELAY);
                for(int i=0; i<MAX_REGISTERS; i++)
                {
                    if(i2c_read_reg(a, i) != regmap[i])
                        stable[i] = false;
                }
            }

            //count registers (assumes that unused registers have the value 0xFF)
            int reg_cnt;
            for(reg_cnt=MAX_REGISTERS-1; regmap[reg_cnt]!=0xFF; reg_cnt--);
            reg_cnt |= 0b1111; reg_cnt++;  //round up to the next multiple of 16

            //dump registers
            send_signature(a, regmap, stable, reg_cnt);
            //hexdump(regmap, stable, reg_cnt);
    }
  }

  /*if(total)
      smprintf("\n\nfound %d devices\n\n", total);
  else
      smprintf("no devices found!\n\n");*/
}

bool i2c_is_device_up(uint8_t sladdr)
{
  Wire.beginTransmission(sladdr);
  return (Wire.endTransmission()==0);
}

void i2c_write_reg(uint8_t sladdr, uint8_t reg, uint8_t val)
{
  Wire.beginTransmission(sladdr);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

void i2c_write_byte_stream(uint8_t sladdr, int len, uint8_t *bytes)
{
  Wire.beginTransmission(sladdr);
  for(int i=0; i<len; i++)
      Wire.write(bytes[i]);
  Wire.endTransmission();
}

//the first argument is for optionally reading back the value. if you don't want this, pass NULL
bool i2c_check_reg_val(uint8_t *v, uint8_t sladdr, uint8_t reg, uint8_t expected)
{
  uint8_t val = i2c_read_reg(sladdr, reg);
  if(v) *v = val;
  return (val == expected);
}

uint8_t i2c_read_reg(uint8_t sladdr, uint8_t reg)
{
  Wire.beginTransmission(sladdr);
  Wire.write(reg);
  Wire.endTransmission();

  delay(1);
  Wire.requestFrom((char)sladdr, 1);
  uint8_t b = Wire.read();
  Wire.endTransmission();
  return b;
}

/*void hexdump(uint8_t *data, bool *stable, uint16_t end_addr)
{
    //print columns
    smprintf("\t\t");
    for(int i=0; i<16; i++)
    {
        if(i==8) smprintf("   ");
        smprintf("%1X  ", i);
    }
            
    //read the first n regs, dump them
    for(uint16_t i=0; i<end_addr; i++)
    {
        if(!(i & 0b1111))        smprintf("\n\t0x%02X\t", i);
        else if(!(i & 0b111))    smprintf("   ");
                
        if(stable[i])
            smprintf("%02X ", data[i]);
        else
            smprintf("?? ");
    }
}*/

void send_signature(uint8_t sladdr, uint8_t *regmap, bool *stable, uint16_t end_addr)
{
    Serial.print("signature ");
    print_hex_leading(sladdr);

    for(uint16_t i=0; i<end_addr; i++)
    {
        if(stable[i])
        {
            print_hex_leading(regmap[i]);
        }
        else
            Serial.print("??");
    }
    Serial.println("");
}

//prints a byte in hex, appending the leading 0
void print_hex_leading(uint8_t b)
{
    if(b < 0x10)  Serial.print("0");
    Serial.print(b, HEX);
}

void error(ERRCODE err)
{
  Serial.println("err " + String(err));
  while(1);
}

void warn(WARNCODE warn)
{
  Serial.println("warn " + String(warn));
  while(!Serial.available());
  String warnresp = Serial.readString();
  if(warnresp != "ok\n")
      while(1);
}

/*bool warn_prompt(const char *str)
{
  smprintf("--- warning: %s ---\n", str);
  smprintf("enter \'y\' to continue...\n");

  while(!Serial.available());
  return Serial.read()=='y';
}*/
