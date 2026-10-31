from mininet.topo import Topo


class LogTopo(Topo):

    def build(self):
        # Two switches
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        # Two log-sending hosts
        h1 = self.addHost("h1", ip="10.0.0.1/24")
        h2 = self.addHost("h2", ip="10.0.0.2/24")

        # Central log-server host
        h3 = self.addHost("h3", ip="10.0.0.3/24")

        # Connect clients to the first switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)

        # Connect switches through a bandwidth-limited link
        self.addLink(s1, s2, bw=0.1)

        # Connect server to the second switch
        self.addLink(h3, s2)


topos = {
    "logtopo": lambda: LogTopo()
}
