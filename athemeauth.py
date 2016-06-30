from xmlrpc.client import ServerProxy, Fault

import os
import znc

class Atheme:
    def __init__(self, url):
        self.url = url
        self.proxy = ServerProxy(url)
        self.cookie = "*"
        self.username = "*"
        self._privset = None

    def login(self, username, password):
        self.username = username
        self.cookie = self.proxy.atheme.login(username, password)
        self.privs()

    def privs(self):
        if self._privset is not None:
            return self._privset

        self._privset = self.proxy.atheme.privset(self.cookie, self.username).split()
        return self._privset

class athemeauth(znc.Module):
    module_types = [znc.CModInfo.GlobalModule]

    def __init__(self):
        pass

    def OnLoginAttempt(self, auth):
        username = auth.GetUsername()
        password = auth.GetPassword()

        atheme = Atheme("http://{}/xmlrpc".format(os.environ.get("ATHEME_SERVER", "127.0.0.1:8069")))
        user = znc.CZNC.Get().FindUser(username)

        if user != None:
            if user.GetPass() != "::":
                #Allow normal ZNC accounts to log in
                return znc.CONTINUE
            else:
                try:
                    atheme.login(username, password)

                    with open("/tmp/znc-cookie-%s" % username, "w") as fout:
                        fout.write(atheme.cookie)

                        auth.AcceptLogin(user)
                        user.thisown = 0

                except Fault:
                    return znc.CONTINUE



        try:
            atheme.login(username, password)

        except Fault:
            return znc.CONTINUE

        if user == None:
            myuser = znc.CUser(username)

            nname = os.getenv("IRC_NETWORK_NAME")
            nhost = os.getenv("IRC_NETWORK_DOMAIN")

            auth.GetSocket().Write(":bnc.{} NOTICE * :*** Creating account for {}...\r\n".format(nhost, username))
            auth.GetSocket().Write(":bnc.{} NOTICE * :*** Thank you for supporting {}!\r\n".format(nhost, nname))

            baseuser = znc.CZNC.Get().FindUser("scrub")
            baseuser.thisown = 0

            s = znc.String()
            s.thisown = 0

            if not myuser.Clone(baseuser, s, False):
                print("WTF?", s)
                return znc.CONTINUE

            if not znc.CZNC.Get().AddUser(myuser, s):
                print("WTF?", s)
                return znc.CONTINUE
            user = myuser

            user.SetPass("::", znc.CUser.HASH_NONE, "::")

            #this is a new user, set up stuff
            user.SetNick(username)
            user.SetAltNick(username + "`")
            user.SetIdent(username[:8])
            user.SetRealName("{} hosted bnc user {}".format(nname, username))
            user.SetDenySetBindHost(True)
            user.SetQuitMsg("Shutting down!")
            user.SetMaxNetworks(1)
            user.SetAdmin(False)

            #They are going to want a network to talk on.
            user.AddNetwork(nname, s)
            network = user.FindNetwork(nname)
            network.AddServer("irc.{} +6697".format(nhost))
            network.AddChan("#bnc", True)
            network.JoinChans()

            with open("/tmp/znc-cookie-%s" % username, "w") as fout:
                fout.write(atheme.cookie)

            znc.CZNC.Get().WriteConfig()

        auth.GetSocket().Write(":bnc.{} NOTICE * :*** Welcome to the PonyChat BNC {}!\r\n".format(nhost, username))
        auth.GetSocket().Write(":bnc.{} NOTICE * :*** Your IP address is {} and may be checked for proxies.\r\n".format(nhost, auth.GetRemoteIP()))

        auth.AcceptLogin(user)
        user.thisown = 0

        return znc.HALT
