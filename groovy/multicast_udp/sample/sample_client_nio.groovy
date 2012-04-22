
import java.nio.*
import java.nio.channels.*
import java.nio.charset.Charset

def addr = InetAddress.getByName("224.0.0.2")

def dc = DatagramChannel.open()
	//以下の設定は必須ではない
	.setOption(StandardSocketOptions.IP_MULTICAST_TTL, 1)

def buf = ByteBuffer.wrap(args[0].bytes)

dc.send(buf, new InetSocketAddress(addr, 41234))

dc.close()
