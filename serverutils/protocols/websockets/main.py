from .. import Protocol##, HTTPProtocolSwitcher


class utils:
    def getInteger(bits):
        character="".join([str(bit) for bit in bits])
        character=int(character,2)
        return character
    def getCharacter(bits):
        character=chr(utils.getInteger(bits))
        return character


class Bits:
    def __init__(self,data=None,bits=None):
        self.bitsdata=[]
        if type(data)==str:
            self.bitsdata=self.convertToBits(data)
        if type(data)==int:
            self.bitsdata=self.convertToBits(chr(data))
        if type(data)==list:
            for x in data:
                if type(x)==str:
                    self.bitsdata=self.bitsdata+self.convertToBits(x)
                if type(x)==int:
                    self.bitsdata=self.bitsdata+self.convertToBits(chr(x))
        if bits: ## Bits should be a predefined list of bits
            self.bitsdata=bits
        self.position=0
    def setbit(self,bitnumber):
        self.bitsdata[bitnumber]=1
    def unsetbit(self,bitnumber):
        self.bitsdata[bitnumber]=0
    def flipbit(self,bitnumber):
        self.bitsdata[bitnumber]=not self.bitsdata[bitnumber]
    def _read(self):
        self.position+=1
        return self.bitsdata[self.position-1]
    def read(self,amount=1):
        bits=[]
        for x in range(0,amount):
            bits.append(self._read())
        return bits
    def getInteger(self,numbits):
        d=self.read(numbits)
        return self._toInteger(d)
    def _toInteger(self,bits):
        return int("".join([str(bit) for bit in bits]),2)
    def getCharacter(self,numbits):
        return chr(self.getInteger(numbits))
    def getSections(self,sectiondata): ## Sectiondata should be a string, containing bits bytes information. Such as, "b1 s4 i4" would get a list of bits 1 long, a string from 4 bits, and an integer from 4 bits
        sections=[]
        for x in sectiondata.split(" "):
            number=int("".join(x[1:]))
            if x[0]=="b":
                sections.append(self.read(number))
            if x[0]=="s":
                sections.append(self.getCharacter(number))
            if x[0]=="i":
                sections.append(self.getInteger(number))
        return sections
    def getAllBits(self,numbits):
        pf=[]
        for x in range(0,int((len(self.bitsdata)-(len(self.bitsdata)%numbits))/numbits)):
            pf.append(self.read(numbits))
        return pf
    def getAllIntegers(self,numbits):
        df=self.getAllBits(numbits)
        return [self._toInteger(x) for x in df]
    def getAllCharacters(self,numbits):
        df=self.getAllIntegers(numbits)
        return [chr(x) for x in df]
    def convertToBits(self,data):
        totalbits=[]
        for character in data:
            curbits=bin(ord(character))[2:].rjust(8,'0')
            for x in curbits:
                totalbits.append(int(x))
        return totalbits


class WebSocketMessage:
    def __init__(self,data=None):
        self.FIN=                     None
        self.RSV1=                    None
        self.RSV2=                    None
        self.RSV3=                    None
        self.OPCODE=                  None
        self.MASK=                    None
        self.PAYLOAD_LEN=             None
        self.EXT_PAYLOAD_LEN=         None
        self.EXT_EXT_PAYLOAD_LEN=     None
        self.MASKING_KEY=             None
        self.PAYLOAD_DATA=            None
        self.PAYLOAD_DATA_CONT=       None
        if data:
            self._decode(data)
    def _decode(self,data):
        bits=Bits(data)
        self.FIN=bits.read()
        self.RSV1=bits.read()
        self.RSV2=bits.read()
        self.RSV3=bits.read()
        self.OPCODE=bits.getCharacter(4)
        self.MASK=bits.read()
        self.PAYLOAD_LEN=bits.read(7)
        self.EXT_PAYLOAD_LEN=bits.getInteger(16)
        self.EXT_EXT_PAYLOAD_LEN=bits.getInteger(64)
        self.MASKING_KEY=bits.getSections("s8 s8 s8")
        self.PAYLOAD_DATA=bits.getAllCharacters(8)
class WebSocketIncoming:
    def __init__(self,data):
        self.data=data
        self.decoded=self.decode(data)


##class Protocol_WebSockets(Protocol):
##    def uponAddToServer(self,server):
##        server.getHook("swit").addFunction(self.tophandle)
##        server.addExtension(HTTPProtocolSwitcher()) ## Protocol switching utility is a requirement for WebSockets
##    def tophandle(self,incoming,outgoing):
##        outgoing.setPreserveConnection(True) ## Preserve the connection for future interaction.
##        
class Protocol_WebSockets(Protocol):
    pass
