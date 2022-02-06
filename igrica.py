import time
import random
import spade
from spade.agent import Agent
from spade.message import Message
from spade.behaviour import FSMBehaviour, State
import os

trenutni_igac = random.choice(['x','o'])
igra_aktivna= True
pobjednik = None
ploca =['-','-','-',
        '-','-','-',
        '-','-','-',]
igraciUIgri = []
indexIgraca = 0

def ispisi_plocu():
    for redak in[ploca[i*3:(i+1)*3] for i in range(3)]:
        print('|'+'|'.join(redak)+'|')

def provjeri_kraj_igre():
    provjeri_pobjedu()
    provjeri_nerijeseno()

def provjeri_pobjedu():
    global pobjednik
    pobjednik_retka=provjeri_retke()
    pobjednik_stupca=provjeri_stupce()
    pobjednik_dijagonale=provjeri_dijagonale()
    if pobjednik_retka:
        pobjednik=pobjednik_retka
    elif pobjednik_stupca:
        pobjednik= pobjednik_stupca
    elif pobjednik_dijagonale:
        pobjednik=pobjednik_dijagonale
    else:
        pobjednik = None

def provjeri_retke():
    global igra_aktivna
    redak1=ploca[0]==ploca[1]==ploca[2] != '-'
    redak2=ploca[3]==ploca[4]==ploca[5] != '-'
    redak3=ploca[6]==ploca[7]==ploca[8] != '-'

    if redak1 or redak2 or redak3:
         igra_aktivna=False
    if redak1:
        return ploca[0]
    elif redak2:
        return ploca[3]
    elif redak3:
        return ploca[6]
    else:
        return False
    

def provjeri_stupce():
    global igra_aktivna
    stupac1=ploca[0]==ploca[3]==ploca[6] != '-'
    stupac2=ploca[1]==ploca[4]==ploca[7] != '-'
    stupac3=ploca[2]==ploca[5]==ploca[8] != '-'

    if stupac1 or stupac2 or stupac3:
         igra_aktivna=False
    if stupac1:
        return ploca[0]
    elif stupac2:
        return ploca[1]
    elif stupac3:
        return ploca[2]
    else:
        return False

def provjeri_dijagonale():
    global igra_aktivna
    dijagonala1=ploca[0]==ploca[4]==ploca[8] != '-'
    dijagonala2=ploca[2]==ploca[4]==ploca[6] != '-'

    if dijagonala1 or dijagonala2:
         igra_aktivna=False
         return ploca[4]
    else:
        return False

def provjeri_nerijeseno():
    global igra_aktivna
    global pobjednik
    if '-' not in ploca:
        igra_aktivna=False
        pobjednik = None

def promjeni_igraca():
    global trenutni_igac
    if trenutni_igac=='x':
        trenutni_igac='o'
    elif trenutni_igac =='o':
        trenutni_igac ='x'

class IgraKrizicKruzic(Agent):
    class Ponasanje(FSMBehaviour):
        async def on_start(self):
            print(f"IGRA JE INICIJALIZIRANA.")

        async def on_end(self):
            global pobjednik
            print(f"IGRA PRESTAJE.")
            for player in igraciUIgri:
                        poruka = Message(
                            to=player,
                            body=f"IGRA JE ZAVRŠENA. POBJEDNIK JE {pobjednik}"
                        )
                        await self.send(poruka)

    class Cekaonica(State):
        async def run(self):
            poruka = await self.receive(timeout=120)
            if (poruka):
                igraciUIgri.append(poruka.body)
                if (len(igraciUIgri) == 2):
                    ispisi_plocu()
                    for player in igraciUIgri:
                        poruka = Message(
                            to=player,
                            body=str("START")
                        )
                        await self.send(poruka)
                    self.set_next_state("PLAY")
                else:
                    self.set_next_state("WAIT")
            else:
                self.set_next_state("WAIT")
            
    class Igraonica(State):
        async def run(self):
            global indexIgraca
            global pobjednik
            while igra_aktivna:
                        poruka = Message(
                            to=igraciUIgri[indexIgraca],
                            body=f"NA REDU JE {trenutni_igac}. ODABERI POZICIJU 1-9"
                        )
                        await self.send(poruka)
                        poruka = await self.receive(timeout=120)
                        if(poruka):
                            pozicija = poruka.body
                            while True:
                                while pozicija not in ['1','2','3','4','5','6','7','8','9']:
                                    poruka = Message(to=igraciUIgri[indexIgraca], body=f"KRIVI UNOS! ODABERI BROJ U RASPONU 1-9")
                                    await self.send(poruka)
                                    poruka = await self.receive(timeout=120)
                                    pozicija = poruka.body
                                
                                pozicija = int(pozicija) - 1
                                
                                if ploca[pozicija]=='-':
                                    break
                                else:
                                    poruka = Message( to=igraciUIgri[indexIgraca], body=f"NEDOZVOLJENO POLJE. PONOVNI UNOS.")
                                    await self.send(poruka)
                            indexIgraca = 1 if indexIgraca == 0 else 0
                            ploca[pozicija]=trenutni_igac
                            promjeni_igraca()
                            clear = lambda: os.system('clear')
                            clear()
                            ispisi_plocu()
                            provjeri_kraj_igre()
                        else:
                            self.set_next_state("PLAY")
            if pobjednik != None:
                if pobjednik.lower()=='x' or pobjednik.lower()=='o':
                    print(f'POBJEDNIK JE {pobjednik}')
            elif pobjednik == None:
                print('NERIJEŠENO')

    async def setup(self):
        fsmPonasanje = self.Ponasanje()
        fsmPonasanje.add_state(name="WAIT", state=self.Cekaonica(), initial=True)
        fsmPonasanje.add_state(name="PLAY", state=self.Igraonica())
        fsmPonasanje.add_transition(source="WAIT", dest="WAIT")
        fsmPonasanje.add_transition(source="WAIT", dest="PLAY")
        fsmPonasanje.add_transition(source="PLAY", dest="PLAY")
        self.add_behaviour(fsmPonasanje)


if __name__ == '__main__':
    igra = IgraKrizicKruzic("server@localhost", "password")
    igraKraj = igra.start()
    igraKraj.result()

    while igra.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    igra.stop()
    spade.quit_spade()
