import time as utime
import machine
from machine import Pin

from OV5642_reg import *

OV5642=1

MAX_FIFO_SIZE=0x7FFFFF
ARDUCHIP_FRAMES=0x01
ARDUCHIP_TIM=0x03
VSYNC_LEVEL_MASK=0x02
ARDUCHIP_TRIG=0x41
CAP_DONE_MASK=0x08

OV5642_CHIPID_HIGH=0x300a
OV5642_CHIPID_LOW=0x300b

OV5642_320x240  =0
OV5642_640x480  =1
OV5642_1024x768 =2
OV5642_1280x960 =3
OV5642_1600x1200=4
OV5642_2048x1536=5
OV5642_2592x1944=6
OV5642_1920x1080=7

# Advanced_AWB =0
# Simple_AWB   =1
# Manual_day   =2
# Manual_A     =3
# Manual_cwf   =4
# Manual_cloudy=5
# 
# degree_180=0
# degree_150=1
# degree_120=2
# degree_90 =3
# degree_60 =4
# degree_30 =5
# degree_0  =6
# degree30  =7
# degree60  =8
# degree90  =9
# degree120 =10
# degree150 =11
# 
# Auto   =0
# Sunny  =1
# Cloudy =2
# Office =3
# Home   =4
# 
# Antique     =0
# Bluish      =1
# Greenish    =2
# Reddish     =3
# BW          =4
# Negative    =5
# BWnegative  =6
# Normal      =7
# Sepia       =8
# Overexposure=9
# Solarize    =10
# Blueish     =11
# Yellowish   =12
# 
# Exposure_17_EV  =0
# Exposure_13_EV  =1
# Exposure_10_EV  =2
# Exposure_07_EV  =3
# Exposure_03_EV  =4
# Exposure_default=5
# Exposure03_EV   =6
# Exposure07_EV   =7
# Exposure10_EV   =8
# Exposure13_EV   =9
# Exposure17_EV   =10
# 
# Auto_Sharpness_default=0
# Auto_Sharpness1       =1
# Auto_Sharpness2       =2
# Manual_Sharpnessoff   =3
# Manual_Sharpness1     =4
# Manual_Sharpness2     =5
# Manual_Sharpness3     =6
# Manual_Sharpness4     =7
# Manual_Sharpness5     =8
# 
# MIRROR     =0
# FLIP       =1
# MIRROR_FLIP=2
# 
# Saturation4 =0
# Saturation3 =1
# Saturation2 =2
# Saturation1 =3
# Saturation0 =4
# Saturation_1=5
# Saturation_2=6
# Saturation_3=7
# Saturation_4=8
# 
# Brightness4 =0
# Brightness3 =1
# Brightness2 =2
# Brightness1 =3
# Brightness0 =4
# Brightness_1=5
# Brightness_2=6
# Brightness_3=7
# Brightness_4=8
# 
# Contrast4 =0
# Contrast3 =1
# Contrast2 =2
# Contrast1 =3
# Contrast0 =4
# Contrast_1=5
# Contrast_2=6
# Contrast_3=7
# Contrast_4=8
# 
# Antique      = 0
# Bluish       = 1
# Greenish     = 2
# Reddish      = 3
# BW           = 4
# Negative     = 5
# BWnegative   = 6
# Normal       = 7
# Sepia        = 8
# Overexposure = 9
# Solarize     = 10
# Blueish      = 11
# Yellowish    = 12
# 
high_quality   =0
default_quality=1
low_quality    =2
# 
# Color_bar   =0
# Color_square=1
# BW_square   =2
# DLI         =3

BMP =0
JPEG=1
RAW =2

class ArducamClass(object):
    def __init__(self,Type):
        self.CameraMode=JPEG
        self.CameraType=Type
        self.SPI_CS=machine.Pin(0, machine.Pin.OUT)
        self.I2cAddress=0x30
        self.spi = machine.SPI(1, baudrate=4000000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
        self.i2c = machine.SoftI2C(scl=Pin(7), sda=Pin(6), freq=1000000)
        #self.i2c.start()
        #self.i2c.init(0, frequency=1000000)
        #while not self.i2c.try_lock():
        #    pass
        utime.sleep(0.1)
        self.i2c_address = self.i2c.scan()[0]
        print(f"I2C Address: {self.i2c_address}")
        self.Spi_write(0x07,0x80)
        utime.sleep(0.1)
        self.Spi_write(0x07,0x00)
        utime.sleep(0.1)
        
    def Camera_Detection(self):
        while True:
            # if self.CameraType==OV2640:
            #     self.I2cAddress=0x30
            #     self.wrSensorReg8_8(0xff,0x01)
            #     id_h=self.rdSensorReg8_8(0x0a)
            #     id_l=self.rdSensorReg8_8(0x0b)
            #     if((id_h==0x26)and((id_l==0x40)or(id_l==0x42))):
            #         print('CameraType is OV2640')
            #         break
            #     else:
            #         print('Can\'t find OV2640 module')
            # elif self.CameraType==OV5642:
            if self.CameraType==OV5642:
                self.I2cAddress=0x3c
                #utime.sleep(0.1)
                self.wrSensorReg16_8(0xff,0x01)
                utime.sleep(1)
                id_h=self.rdSensorReg16_8(OV5642_CHIPID_HIGH)
                id_l=self.rdSensorReg16_8(OV5642_CHIPID_LOW)
                if((id_h==0x56)and(id_l==0x42)):
                    print('CameraType is OV5642')
                    break
                else:
                    print('Can\'t find OV5642 module')
            utime.sleep(1)
            
    def Set_Camera_mode(self,mode):
        self.CameraMode=mode
    
    def wrSensorReg16_8(self,addr,val):
        buffer=bytearray(3)
        buffer[0]=(addr>>8)&0xff
        buffer[1]=addr&0xff
        buffer[2]=val
        #print(buffer)
        self.iic_write(buffer)
    
    def rdSensorReg16_8(self,addr):
        buffer=bytearray(2)
        rt=bytearray(1)
        buffer[0]=(addr>>8)&0xff
        buffer[1]=addr&0xff
        self.iic_write(buffer)
        self.iic_readinto(rt)
        return rt[0]
    
    def wrSensorReg8_8(self,addr,val):
        buffer=bytearray(2)
        buffer[0]=addr
        buffer[1]=val
        self.iic_write(buffer)
        
    def iic_write(self, buf, *, start=0, end=None):
        #self.i2c.write(buf)
        self.i2c.writeto(self.i2c_address, buf)
        # if end is None:
        #     end = len(buf)
        # self.i2c.writeto(self.I2cAddress, buf, start=start, end=end)

    def iic_readinto(self, buf, *, start=0, end=None):
        #self.i2c.readinto(buf)
        self.i2c.readfrom_into(self.i2c_address, buf)
        # if end is None:
        #     end = len(buf)
        # self.i2c.readfrom_into(self.I2cAddress, buf, start=start, end=end)
        
    def rdSensorReg8_8(self,addr):
        buffer=bytearray(1)
        buffer[0]=addr
        self.iic_write(buffer)
        self.iic_readinto(buffer)
        return buffer[0]
    
    def Spi_Test(self):
        while True:
            self.Spi_write(0X00,0X56)
            value=self.Spi_read(0X00)
            if(value[0]==0X56):
                print('SPI interface OK')
                break
            else:
                print('SPI interface Error')
            utime.sleep(1)

    def Camera_Init(self):
#         if self.CameraType==OV2640:
#             self.wrSensorReg8_8(0xff,0x01)
#             self.wrSensorReg8_8(0x12,0x80)
#             utime.sleep(0.1)
#             self.wrSensorRegs8_8(OV2640_JPEG_INIT);
#             self.wrSensorRegs8_8(OV2640_YUV422);
#             self.wrSensorRegs8_8(OV2640_JPEG);
#             self.wrSensorReg8_8(0xff,0x01)
#             self.wrSensorReg8_8(0x15,0x00)
#             self.wrSensorRegs8_8(OV2640_320x240_JPEG);
        if self.CameraType==OV5642:
            self.wrSensorReg16_8(0x3008, 0x80)
            if self.CameraMode == RAW:
                self.wrSensorRegs16_8(OV5642_1280x960_RAW)
                self.wrSensorRegs16_8(OV5642_640x480_RAW)
            else:
                self.wrSensorRegs16_8(OV5642_QVGA_Preview1)
                self.wrSensorRegs16_8(OV5642_QVGA_Preview2)
                utime.sleep(0.1)
                if self.CameraMode == JPEG:
                    utime.sleep(0.1)
                    self.wrSensorRegs16_8(OV5642_JPEG_Capture_QSXGA)
# OV5642_320x240  =0
# OV5642_640x480  =1
# OV5642_1024x768 =2
# OV5642_1280x960 =3
# OV5642_1600x1200=4
# OV5642_2048x1536=5
# OV5642_2592x1944=6
# OV5642_1920x1080=7
                    #Set resolution
                    self.wrSensorRegs16_8(ov5642_1280x960)
                    utime.sleep(0.1)
                    self.wrSensorReg16_8(0x3818, 0xa8)
                    self.wrSensorReg16_8(0x3621, 0x10)
                    self.wrSensorReg16_8(0x3801, 0xb0)
                    self.wrSensorReg16_8(0x4407, 0x04)
                else:
                    reg_val
                    self.wrSensorReg16_8(0x4740, 0x21)
                    self.wrSensorReg16_8(0x501e, 0x2a)
                    self.wrSensorReg16_8(0x5002, 0xf8)
                    self.wrSensorReg16_8(0x501f, 0x01)
                    self.wrSensorReg16_8(0x4300, 0x61)
                    reg_val=self.rdSensorReg16_8(0x3818)
                    self.wrSensorReg16_8(0x3818, (reg_val | 0x60) & 0xff)
                    reg_val=self.rdSensorReg16_8(0x3621)
                    self.wrSensorReg16_8(0x3621, reg_val & 0xdf)            
        else:
            pass
        
    def Spi_write(self,address,value):
        maskbits = 0x80
        buffer=bytearray(2)
        buffer[0]=address | maskbits
        buffer[1]=value
        self.SPI_CS_LOW()
        self.spi_write(buffer)
        #self.spi.write(buffer)
        self.SPI_CS_HIGH()
        
    def Spi_read(self,address):
        maskbits = 0x7f
        buffer=bytearray(1)
        buffer[0]=address & maskbits
        self.SPI_CS_LOW()
        self.spi_write(buffer)
        self.spi_readinto(buffer)
        self.SPI_CS_HIGH()
        return buffer

    def spi_write(self, buf, *, start=0, end=None):
        self.spi.write(buf)
        # if end is None:
        #     end = len(buf)
        # self.spi.write(buf, start=start, end=end)
    

    def spi_readinto(self, buf, *, start=0, end=None):
        #if end is None:
        #    end = len(buf)
        #self.spi.readinto(buf, start=start, end=end)
        self.spi.readinto(buf)
        
    def get_bit(self,addr,bit):
        value=self.Spi_read(addr)[0]
        return value&bit
  
    def SPI_CS_LOW(self):
        #self.SPI_CS.value=False
        self.SPI_CS.value(False)
        
    def SPI_CS_HIGH(self):
        #self.SPI_CS.value=True
        self.SPI_CS.value(True)
        
    def set_fifo_burst(self):
        buffer=bytearray(1)
        buffer[0]=0x3c
        #self.spi.write(buffer, start=0, end=1)
        self.spi.write(buffer)
        
    def clear_fifo_flag(self):
        self.Spi_write(0x04,0x01)
        
    def flush_fifo(self):
        self.Spi_write(0x04,0x01)
        
    def start_capture(self):
        self.Spi_write(0x04,0x02)
        
    def read_fifo_length(self):
        len1=self.Spi_read(0x42)[0]
        len2=self.Spi_read(0x43)[0]
        len3=self.Spi_read(0x44)[0]
        len3=len3 & 0x7f
        lenght=((len3<<16)|(len2<<8)|(len1))& 0x07fffff
        return lenght
    
    def wrSensorRegs8_8(self,reg_value):
        for data in reg_value:
            addr = data[0]
            val = data[1]
            if (addr == 0xff and val == 0xff):
                return
            self.wrSensorReg8_8(addr, val)
            utime.sleep(0.001)
            
    def wrSensorRegs16_8(self,reg_value):
        for data in reg_value:
            addr = data[0]
            val = data[1]
            if (addr == 0xffff and val == 0xff):
                return
            self.wrSensorReg16_8(addr, val)
            utime.sleep(0.003)
            
    def set_format(self,mode):
        if mode==BMP or mode==JPEG or mode==RAW:   
            self.CameraMode=mode
            
    def set_bit(self,addr,bit):
        temp=self.Spi_read(addr)[0]
        self.Spi_write(addr,temp&(~bit))

    def OV5642_set_JPEG_size(self,size):
        if size== OV5642_320x240:
          self.wrSensorRegs16_8(ov5642_320x240)
        elif size== OV5642_640x480:
          self.wrSensorRegs16_8(ov5642_640x480)     
        elif size== OV5642_1024x768:
          self.wrSensorRegs16_8(ov5642_1024x768)      
        elif size== OV5642_1280x960:
          self.wrSensorRegs16_8(ov5642_1280x960)      
        elif size== OV5642_1600x1200:
          self.wrSensorRegs16_8(ov5642_1600x1200)      
        elif size== OV5642_2048x1536:
          self.wrSensorRegs16_8(ov5642_2048x1536)      
        elif size== OV5642_2592x1944:
          self.wrSensorRegs16_8(ov5642_2592x1944)      
        else:
          self.wrSensorRegs16_8(ov5642_320x240)

    def OV5642_set_Compress_quality(self,quality):
        if quality== high_quality:
            self.wrSensorReg16_8(0x4407, 0x02)
        elif quality== default_quality:
            self.wrSensorReg16_8(0x4407, 0x04)
        elif quality== low_quality:
            self.wrSensorReg16_8(0x4407, 0x08)
