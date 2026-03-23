#CRC-16
#Polynomial=0xA001
def calcrc(data,ldata):
    ch=0xFF
    cl=0xFF

    for i in range(ldata+1):
        cl=cl^data[i]
        
        for ctrc in range(8):
            carryh=ch%2
            carryl=cl%2
            #whole shifting process
            ch=ch//2           #right shifting hcrc
            cl=(carryh*128)+(cl//2)    # adding last bit of hcrc to lcrc
            if carryl !=0:      #checking the last bit of whole value if it is 0 or not
                ch=ch^0xA0
                cl=cl^0x01
    return ch, cl


packet=input("Enter hexa values packet of byte: ").split()
lpacket=len(packet)-1
print(f"Packet: {packet}")
packet=[int(x,16) for x in packet]
if len(packet)>6:
    data=[]
    crc=[]
    for d in range(6):
        data.append(packet[d])
    ldata=len(data)-1
    crc.append(packet[6])
    crc.append(packet[7])
    print(f"Packet: {packet}")
    print(f"Data: {data} \n CRC: {crc}")
else:
    data=packet
    ldata=lpacket
    print(f"Data: {data}")
cl,ch=calcrc(data,ldata)


print(f"[CRCH: {ch:02x} , CRCL: {cl:02x}]")

if len(packet)>6:
    if crc[0]==ch and crc[1]==cl:
        print("Data is Intact")
    else:
        print("Data is varied!")