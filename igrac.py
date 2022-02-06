from pickle import TRUE
import time
import spade
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State
from argparse import ArgumentParser

idIgrac = ""
agentIgrac = ""

class Igrac(Agent):
    
    class Ponasanje(FSMBehaviour):
        async def on_start(self):
            print(f"{idIgrac} SE PRIKLJUČIO")

        async def on_end(self):
            await self.agent.stop()

    class PokreniIgru(State):
        async def run(self):
            poruka = Message(
                to="server@localhost",
                body=agentIgrac
            )
            await self.send(poruka)
            self.set_next_state("WAIT")
    
    class Cekaonica(State):
        async def run(self):
            poruka = await self.receive(timeout=60)
            if (poruka):
                print(f"IGRA - {poruka.body}")
                self.set_next_state("PLAY")
            else:
                self.set_next_state("WAIT")

    class Igraj(State):
        async def run(self):
            poruka = await self.receive(timeout=120)
            status = False
            if (poruka):
                body = poruka.body
                print(body)
                if "POBJEDNIK" in body:
                    status=True    
                else:
                    pozicija = input("POZICIJA:")
                    poruka = Message(to="server@localhost",body=pozicija)
                    await self.send(poruka)
            if (status != True):
                self.set_next_state("PLAY")

    async def setup(self):
        fsmPonasanje = self.Ponasanje()
        fsmPonasanje.add_state(name="ENTER", state=self.PokreniIgru(), initial=True)
        fsmPonasanje.add_state(name="WAIT", state=self.Cekaonica())
        fsmPonasanje.add_state(name="PLAY", state=self.Igraj())
        fsmPonasanje.add_transition(source="ENTER", dest="WAIT")
        fsmPonasanje.add_transition(source="WAIT", dest="WAIT")
        fsmPonasanje.add_transition(source="WAIT", dest="PLAY")
        fsmPonasanje.add_transition(source="PLAY", dest="PLAY")
        self.add_behaviour(fsmPonasanje)


if __name__ == '__main__':
    argumentParser = ArgumentParser()
    argumentParser.add_argument("-oznaka", type=str, help="OZNAKA IGRAČA.")
    argumenti = argumentParser.parse_args()
    idIgrac = argumenti.oznaka
    agentIgrac = f"{idIgrac}@localhost"
    igrac = Igrac(agentIgrac, "password")
    igracKraj = igrac.start()
    igracKraj.result()

    while igrac.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    igrac.stop()
    spade.quit_spade()
